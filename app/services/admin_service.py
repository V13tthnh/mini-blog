import re
from database import get_db

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text) or 'item'

class AdminService:
    @staticmethod
    def get_dashboard_data() -> dict:
        """
        Retrieves system users, posts, categories, and tags summary for the admin dashboard.
        """
        conn = get_db()

        users = conn.execute("SELECT id, username, email, role, bio, created_at FROM users ORDER BY id ASC").fetchall()
        posts = conn.execute("""
            SELECT posts.id, posts.title, posts.created_at, users.username, categories.name as category_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN categories ON posts.category_id = categories.id
            ORDER BY posts.id DESC
        """).fetchall()

        categories = conn.execute("""
            SELECT categories.id, categories.name, categories.slug, COUNT(posts.id) as post_count
            FROM categories
            LEFT JOIN posts ON categories.id = posts.category_id
            GROUP BY categories.id
            ORDER BY categories.id ASC
        """).fetchall()

        tags = conn.execute("""
            SELECT tags.id, tags.name, tags.slug, COUNT(post_tags.post_id) as tag_count
            FROM tags
            LEFT JOIN post_tags ON tags.id = post_tags.tag_id
            GROUP BY tags.id
            ORDER BY tags.name ASC
        """).fetchall()

        conn.close()

        return {
            "users": users,
            "posts": posts,
            "categories": categories,
            "tags": tags
        }

    @staticmethod
    def toggle_user_role(target_user_id: int):
        conn = get_db()
        target_user = conn.execute("SELECT id, role FROM users WHERE id = ?", (target_user_id,)).fetchone()
        if target_user:
            new_role = "user" if target_user["role"] == "admin" else "admin"
            conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, target_user_id))
            conn.commit()
        conn.close()

    @staticmethod
    def edit_user(target_user_id: int, username: str, email: str, role: str):
        username_clean = username.strip()
        email_clean = email.strip()
        role_clean = role.strip().lower() if role.strip().lower() in ["admin", "user"] else "user"

        if username_clean:
            conn = get_db()
            try:
                conn.execute(
                    "UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?",
                    (username_clean, email_clean, role_clean, target_user_id)
                )
                conn.commit()
            except Exception as e:
                print(f"[Admin User Edit Error]: {e}")
            finally:
                conn.close()

    @staticmethod
    def add_category(name: str, slug: str):
        name_clean = name.strip()
        slug_clean = slug.strip() if slug.strip() else slugify(name_clean)

        if name_clean:
            conn = get_db()
            try:
                conn.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name_clean, slug_clean))
                conn.commit()
            except Exception as e:
                print(f"[Admin Cat Error]: {e}")
            finally:
                conn.close()

    @staticmethod
    def edit_category(cat_id: int, name: str, slug: str):
        name_clean = name.strip()
        slug_clean = slug.strip() if slug.strip() else slugify(name_clean)

        if name_clean:
            conn = get_db()
            try:
                conn.execute("UPDATE categories SET name = ?, slug = ? WHERE id = ?", (name_clean, slug_clean, cat_id))
                conn.commit()
            except Exception as e:
                print(f"[Admin Cat Edit Error]: {e}")
            finally:
                conn.close()

    @staticmethod
    def delete_category(cat_id: int):
        conn = get_db()
        conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def add_tag(name: str, slug: str):
        name_clean = name.strip().lstrip('#')
        slug_clean = slug.strip() if slug.strip() else slugify(name_clean)

        if name_clean:
            conn = get_db()
            try:
                conn.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name_clean, slug_clean))
                conn.commit()
            except Exception as e:
                print(f"[Admin Tag Error]: {e}")
            finally:
                conn.close()

    @staticmethod
    def edit_tag(tag_id: int, name: str, slug: str):
        name_clean = name.strip().lstrip('#')
        slug_clean = slug.strip() if slug.strip() else slugify(name_clean)

        if name_clean:
            conn = get_db()
            try:
                conn.execute("UPDATE tags SET name = ?, slug = ? WHERE id = ?", (name_clean, slug_clean, tag_id))
                conn.commit()
            except Exception as e:
                print(f"[Admin Tag Edit Error]: {e}")
            finally:
                conn.close()

    @staticmethod
    def delete_tag(tag_id: int):
        conn = get_db()
        conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_post(post_id: int):
        conn = get_db()
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
