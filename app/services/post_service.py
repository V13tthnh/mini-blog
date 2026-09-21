import re
from fastapi import UploadFile
from database import get_db
from app.utils.security import verify_csrf_token
from app.utils.sanitize import clean_html
from app.utils.file_upload import save_uploaded_file

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text) or 'tag'

def attach_post_meta(conn, posts_raw):
    enriched_posts = []
    for p in posts_raw:
        post_dict = dict(p)
        post_id = post_dict["id"]
        
        tags = conn.execute("""
            SELECT tags.name, tags.slug 
            FROM tags 
            JOIN post_tags ON tags.id = post_tags.tag_id 
            WHERE post_tags.post_id = ?
        """, (post_id,)).fetchall()
        
        post_dict["tags"] = tags
        enriched_posts.append(post_dict)
    return enriched_posts

class PostService:
    @staticmethod
    def get_home_data(cat: str | None = None, tag: str | None = None) -> dict:
        conn = get_db()
        categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
        all_tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()

        if cat:
            query = """
                SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                       users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE categories.slug = ?
                ORDER BY posts.created_at DESC
            """
            posts_raw = conn.execute(query, (cat,)).fetchall()
        elif tag:
            query = """
                SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                       users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                JOIN post_tags ON posts.id = post_tags.post_id
                JOIN tags ON post_tags.tag_id = tags.id
                WHERE tags.slug = ?
                ORDER BY posts.created_at DESC
            """
            posts_raw = conn.execute(query, (tag,)).fetchall()
        else:
            query = """
                SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                       users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                ORDER BY posts.created_at DESC
            """
            posts_raw = conn.execute(query).fetchall()

        posts = attach_post_meta(conn, posts_raw)

        rec_query = """
            SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                   users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN categories ON posts.category_id = categories.id
            ORDER BY posts.created_at DESC
            LIMIT 4
        """
        recommended_raw = conn.execute(rec_query).fetchall()
        recommended_posts = attach_post_meta(conn, recommended_raw)
        conn.close()

        return {
            "posts": posts,
            "recommended_posts": recommended_posts,
            "categories": categories,
            "all_tags": all_tags
        }

    @staticmethod
    def search_posts(q: str, mode: str) -> dict:
        conn = get_db()
        categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
        all_tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()

        raw_results = []
        sqli_error = None

        if mode == "vulnerable":
            raw_sql = f"""
                SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                       users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE posts.title LIKE '%{q}%' OR posts.content LIKE '%{q}%'
                ORDER BY posts.created_at DESC
            """
            try:
                posts_raw = conn.execute(raw_sql).fetchall()
                raw_results = [dict(r) for r in posts_raw]
            except Exception as e:
                posts_raw = []
                sqli_error = str(e)
                print(f"[SQLi Error Demo]: {e}")
        else:
            safe_sql = """
                SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                       users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
                FROM posts
                JOIN users ON posts.user_id = users.id
                LEFT JOIN categories ON posts.category_id = categories.id
                WHERE posts.title LIKE ? OR posts.content LIKE ?
                ORDER BY posts.created_at DESC
            """
            pattern = f"%{q}%"
            posts_raw = conn.execute(safe_sql, (pattern, pattern)).fetchall()

        posts = attach_post_meta(conn, posts_raw)

        rec_query = """
            SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                   users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN categories ON posts.category_id = categories.id
            ORDER BY posts.created_at DESC
            LIMIT 4
        """
        recommended_raw = conn.execute(rec_query).fetchall()
        recommended_posts = attach_post_meta(conn, recommended_raw)
        conn.close()

        return {
            "posts": posts,
            "raw_results": raw_results,
            "sqli_error": sqli_error,
            "recommended_posts": recommended_posts,
            "categories": categories,
            "all_tags": all_tags
        }

    @staticmethod
    def get_categories():
        conn = get_db()
        categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
        conn.close()
        return categories

    @staticmethod
    def get_all_tags():
        conn = get_db()
        all_tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        conn.close()
        return all_tags


    @staticmethod
    def create_post(
        user: dict,
        title: str,
        content: str,
        category_id: int,
        tags_input: str,
        csrf_token: str,
        image: UploadFile | None,
        mode: str
    ) -> tuple[bool, dict | None, int]:
        if mode == "patched":
            if not verify_csrf_token(csrf_token, user["id"]):
                categories = PostService.get_categories()
                return False, {
                    "categories": categories,
                    "msg": "Lỗi xác thực 400: CSRF Token không hợp lệ!",
                    "msg_type": "error"
                }, 400
            content = clean_html(content)
            title = clean_html(title)

        upload_success, image_url, err_msg = save_uploaded_file(image, mode)
        if not upload_success:
            categories = PostService.get_categories()
            return False, {
                "categories": categories,
                "msg": err_msg,
                "msg_type": "error"
            }, 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, category_id, title, content, image_url) VALUES (?, ?, ?, ?, ?)",
            (user["id"], category_id, title, content, image_url)
        )
        new_post_id = cursor.lastrowid

        if tags_input.strip():
            tag_names = [t.strip().lstrip('#') for t in tags_input.split(',') if t.strip()]
            for name in tag_names:
                slug = slugify(name)
                conn.execute("INSERT OR IGNORE INTO tags (name, slug) VALUES (?, ?)", (name, slug))
                tag_row = conn.execute("SELECT id FROM tags WHERE slug = ?", (slug,)).fetchone()
                if tag_row:
                    conn.execute("INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)", (new_post_id, tag_row["id"]))

        conn.commit()
        conn.close()

        return True, None, 200

    @staticmethod
    def get_post_detail(post_id: int) -> tuple[dict | None, list]:
        conn = get_db()
        post_raw = conn.execute("""
            SELECT posts.id, posts.title, posts.content, posts.image_url, posts.created_at, posts.user_id,
                   users.username, users.avatar_url, categories.name as category_name, categories.slug as category_slug
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN categories ON posts.category_id = categories.id
            WHERE posts.id = ?
        """, (post_id,)).fetchone()

        if not post_raw:
            conn.close()
            return None, []

        post = dict(post_raw)
        tags = conn.execute("""
            SELECT tags.name, tags.slug 
            FROM tags 
            JOIN post_tags ON tags.id = post_tags.tag_id 
            WHERE post_tags.post_id = ?
        """, (post_id,)).fetchall()
        post["tags"] = tags

        comments = conn.execute("""
            SELECT comments.id, comments.content, comments.created_at, comments.user_id,
                   users.username, users.avatar_url
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.created_at DESC, comments.id DESC
        """, (post_id,)).fetchall()
        conn.close()

        return post, comments

    @staticmethod
    def add_comment(user: dict, post_id: int, content: str, csrf_token: str, mode: str) -> tuple[bool, str | None, dict | None, list]:
        if mode == "patched":
            if not verify_csrf_token(csrf_token, user["id"]):
                return False, "csrf", None, []
            content = clean_html(content)

        conn = get_db()
        conn.execute(
            "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
            (post_id, user["id"], content)
        )
        conn.commit()

        post_raw = conn.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
        post = dict(post_raw) if post_raw else {"id": post_id}
        comments = conn.execute("""
            SELECT comments.id, comments.content, comments.created_at, comments.user_id,
                   users.username, users.avatar_url
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.created_at DESC, comments.id DESC
        """, (post_id,)).fetchall()
        conn.close()

        return True, None, post, comments

    @staticmethod
    def get_edit_post_data(user: dict, post_id: int) -> tuple[bool, dict | None, list, str, list]:
        conn = get_db()
        post_raw = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post_raw:
            conn.close()
            return False, None, [], "", []

        post = dict(post_raw)
        if post["user_id"] != user["id"] and user.get("role") != "admin":
            conn.close()
            return False, None, [], "", []

        categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
        all_tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        tags_raw = conn.execute("""
            SELECT tags.name
            FROM tags
            JOIN post_tags ON tags.id = post_tags.tag_id
            WHERE post_tags.post_id = ?
        """, (post_id,)).fetchall()
        tags_str = ", ".join([t["name"] for t in tags_raw])
        conn.close()

        return True, post, categories, tags_str, all_tags

    @staticmethod
    def edit_post(
        user: dict,
        post_id: int,
        title: str,
        content: str,
        category_id: int,
        tags_input: str,
        csrf_token: str,
        image: UploadFile | None,
        mode: str
    ) -> tuple[bool, dict | None, int]:
        conn = get_db()
        post_raw = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post_raw:
            conn.close()
            return False, {"redirect": "/"}, 303

        post = dict(post_raw)
        if post["user_id"] != user["id"] and user.get("role") != "admin":
            conn.close()
            return False, {"redirect": f"/post/{post_id}"}, 303

        if mode == "patched":
            if not verify_csrf_token(csrf_token, user["id"]):
                categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
                conn.close()
                return False, {
                    "post": post,
                    "categories": categories,
                    "tags_str": tags_input,
                    "msg": "Lỗi xác thực 400: CSRF Token không hợp lệ!",
                    "msg_type": "error"
                }, 400

            content = clean_html(content)
            title = clean_html(title)

        image_url = post.get("image_url")
        if image and image.filename:
            upload_success, new_image_url, err_msg = save_uploaded_file(image, mode)
            if not upload_success:
                categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
                conn.close()
                return False, {
                    "post": post,
                    "categories": categories,
                    "tags_str": tags_input,
                    "msg": err_msg,
                    "msg_type": "error"
                }, 400
            image_url = new_image_url

        conn.execute(
            "UPDATE posts SET title = ?, content = ?, category_id = ?, image_url = ? WHERE id = ?",
            (title, content, category_id, image_url, post_id)
        )

        conn.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
        if tags_input.strip():
            tag_names = [t.strip().lstrip('#') for t in tags_input.split(',') if t.strip()]
            for name in tag_names:
                slug = slugify(name)
                conn.execute("INSERT OR IGNORE INTO tags (name, slug) VALUES (?, ?)", (name, slug))
                tag_row = conn.execute("SELECT id FROM tags WHERE slug = ?", (slug,)).fetchone()
                if tag_row:
                    conn.execute("INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)", (post_id, tag_row["id"]))

        conn.commit()
        conn.close()

        return True, None, 200
