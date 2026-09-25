/**
 * Mini Blog ANM - Main JavaScript Module
 * Shadcn UI Interactions & Smooth Scrolling
 */

/**
 * Smoothly scrolls the window to top using a cubic easing function
 * @param {number} duration Duration of the animation in milliseconds
 */
function smoothScrollToTop(duration = 600) {
  const startPosition = window.scrollY || document.documentElement.scrollTop;
  if (startPosition <= 0) return;
  
  let startTime = null;

  // Easing cubic mượt mà (easeInOutCubic)
  function easeInOutCubic(t) {
    return t < 0.5 
      ? 4 * t * t * t 
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function animationStep(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const progress = Math.min(timeElapsed / duration, 1);
    const easeProgress = easeInOutCubic(progress);

    window.scrollTo(0, startPosition * (1 - easeProgress));

    if (timeElapsed < duration) {
      requestAnimationFrame(animationStep);
    }
  }

  requestAnimationFrame(animationStep);
}

// Initialize interactive elements when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
  // Scroll to Top Button Logic
  const scrollToTopBtn = document.getElementById('scrollToTopBtn');
  
  if (scrollToTopBtn) {
    function checkScroll() {
      const scrollPosition = window.scrollY || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.scrollHeight;
      
      // Hiển thị khi cuộn xuống hơn 300px HOẶC khi gần đến cuối trang (cách đáy 500px)
      const isNearBottom = (scrollPosition + windowHeight) >= (fullHeight - 500);
      
      if (scrollPosition > 300 || isNearBottom) {
        scrollToTopBtn.classList.add('show');
      } else {
        scrollToTopBtn.classList.remove('show');
      }
    }

    scrollToTopBtn.addEventListener('click', function () {
      smoothScrollToTop(600);
    });

    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll();
  }

  // Prevent default submit on live search forms that use HTMX
  const searchForms = document.querySelectorAll('.search-form');
  searchForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
    });
  });

  // Restore active admin tab if saved in localStorage
  const savedAdminTab = localStorage.getItem('admin_active_tab');
  if (savedAdminTab) {
    const targetBtn = document.querySelector(`.admin-tab-btn[data-tab="${savedAdminTab}"]`);
    const targetContent = document.getElementById(savedAdminTab);
    if (targetBtn && targetContent) {
      document.querySelectorAll('.admin-tab-btn').forEach(function (btn) {
        btn.classList.remove('active');
      });
      document.querySelectorAll('.admin-tab-content').forEach(function (content) {
        content.classList.remove('active');
      });
      targetBtn.classList.add('active');
      targetContent.classList.add('active');
    }
  }

  // Event Delegation for Interactive Elements
  document.addEventListener('click', function (e) {
    // Admin Sub-Header Tab Switcher
    const adminTabBtn = e.target.closest('.admin-tab-btn');
    if (adminTabBtn) {
      e.preventDefault();
      const tabTargetId = adminTabBtn.getAttribute('data-tab');
      if (!tabTargetId) return;

      document.querySelectorAll('.admin-tab-btn').forEach(function (btn) {
        btn.classList.remove('active');
      });
      document.querySelectorAll('.admin-tab-content').forEach(function (content) {
        content.classList.remove('active');
      });

      adminTabBtn.classList.add('active');
      const targetContent = document.getElementById(tabTargetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      try {
        localStorage.setItem('admin_active_tab', tabTargetId);
      } catch (err) {}
      return;
    }

    // Open Edit User Modal Dialog
    const editUserBtn = e.target.closest('.open-edit-user-modal-btn');
    if (editUserBtn) {
      e.preventDefault();
      const userId = editUserBtn.getAttribute('data-user-id');
      const username = editUserBtn.getAttribute('data-username');
      const email = editUserBtn.getAttribute('data-email');
      const role = editUserBtn.getAttribute('data-role');

      const modal = document.getElementById('editUserModal');
      const form = document.getElementById('editUserForm');
      const userIdDisplay = document.getElementById('modalUserIdDisplay');
      const usernameInput = document.getElementById('modalUsernameInput');
      const emailInput = document.getElementById('modalEmailInput');
      const roleSelect = document.getElementById('modalRoleSelect');

      if (modal && form) {
        form.action = `/admin/user/${userId}/edit`;
        if (userIdDisplay) userIdDisplay.value = `#${userId}`;
        if (usernameInput) usernameInput.value = username || '';
        if (emailInput) emailInput.value = email || '';
        if (roleSelect) roleSelect.value = role || 'user';

        modal.style.display = 'flex';
        requestAnimationFrame(function () {
          modal.classList.add('show');
        });
      }
      return;
    }

    // Close Modal Dialog
    const closeBtn = e.target.closest('#closeEditUserModalBtn, #cancelEditUserModalBtn');
    if (closeBtn) {
      e.preventDefault();
      const modal = document.getElementById('editUserModal');
      if (modal) {
        modal.classList.remove('show');
        setTimeout(function () {
          modal.style.display = 'none';
        }, 200);
      }
      return;
    }

    if (e.target.classList.contains('modal-backdrop')) {
      e.target.classList.remove('show');
      setTimeout(function () {
        e.target.style.display = 'none';
      }, 200);
      return;
    }

    // Toggle Table Row Inline Editing (Categories & Tags)
    const toggleEditBtn = e.target.closest('.toggle-inline-edit-btn');
    if (toggleEditBtn) {
      e.preventDefault();
      const targetId = toggleEditBtn.getAttribute('data-target');
      const hideId = toggleEditBtn.getAttribute('data-hide');

      const editRow = document.getElementById(targetId);
      const viewRow = document.getElementById(hideId);

      if (editRow && viewRow) {
        viewRow.style.display = 'none';
        editRow.style.display = 'table-row';
      }
      return;
    }

    const cancelEditBtn = e.target.closest('.cancel-inline-edit-btn');
    if (cancelEditBtn) {
      e.preventDefault();
      const showId = cancelEditBtn.getAttribute('data-show');
      const hideId = cancelEditBtn.getAttribute('data-hide');

      const viewRow = document.getElementById(showId);
      const editRow = document.getElementById(hideId);

      if (editRow && viewRow) {
        editRow.style.display = 'none';
        viewRow.style.display = 'table-row';
      }
      return;
    }



    // Password Visibility Toggle Logic
    const btn = e.target.closest('.toggle-password-btn');
    if (btn) {
      e.preventDefault();
      const wrapper = btn.closest('.password-input-wrapper');
      if (!wrapper) return;
      const input = wrapper.querySelector('input');
      if (!input) return;

      const eyeIcon = btn.querySelector('.eye-icon');
      const eyeOffIcon = btn.querySelector('.eye-off-icon');

      if (input.type === 'password') {
        input.type = 'text';
        if (eyeIcon) eyeIcon.style.display = 'none';
        if (eyeOffIcon) eyeOffIcon.style.display = 'inline-block';
        btn.setAttribute('aria-label', 'Ẩn mật khẩu');
        btn.setAttribute('title', 'Ẩn mật khẩu');
      } else {
        input.type = 'password';
        if (eyeIcon) eyeIcon.style.display = 'inline-block';
        if (eyeOffIcon) eyeOffIcon.style.display = 'none';
        btn.setAttribute('aria-label', 'Hiện mật khẩu');
        btn.setAttribute('title', 'Hiện mật khẩu');
      }
      return;
    }

    // Sidebar Category & Tag active state switcher for HTMX filtering
    const catItem = e.target.closest('.sidebar-cat-item');
    if (catItem) {
      document.querySelectorAll('.sidebar-cat-item').forEach(function (item) {
        item.classList.remove('active');
      });
      catItem.classList.add('active');
      return;
    }

    const tagItem = e.target.closest('.sidebar-tag-cloud .tag-chip');
    if (tagItem) {
      document.querySelectorAll('.sidebar-tag-cloud .tag-chip').forEach(function (item) {
        item.classList.remove('active');
      });
      tagItem.classList.add('active');
      return;
    }
  });

  // Initialize Admin Table Live Search & Client-Side Pagination
  initAdminTableSearchAndPagination();

  // Initialize Client-Side Form Validation for Patched Mode
  initClientSideValidation();
});

/**
 * Admin Table Search & Pagination Controller
 */
function initAdminTableSearchAndPagination() {
  const adminTables = document.querySelectorAll('.table-custom[data-items-per-page]');
  if (!adminTables.length) return;

  adminTables.forEach(function (table) {
    const tableId = table.id;
    if (!tableId) return;

    const searchInput = document.querySelector(`.admin-table-search[data-table-id="${tableId}"]`);
    const paginationWrapper = document.querySelector(`.table-pagination-wrapper[data-table-id="${tableId}"]`);

    const itemsPerPage = parseInt(table.getAttribute('data-items-per-page')) || 8;
    let currentPage = 1;
    let searchQuery = '';

    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    // Get all standard display rows (excluding edit rows and empty placeholder row)
    const allViewRows = Array.from(tbody.querySelectorAll('tr')).filter(function (row) {
      return !row.classList.contains('cat-row-edit') && 
             !row.classList.contains('tag-row-edit') &&
             !row.querySelector('td[colspan]');
    });

    function updateTableState() {
      const query = searchQuery.trim().toLowerCase();

      // Filter rows based on search text matching any cell content
      const matchedRows = allViewRows.filter(function (row) {
        if (!query) return true;
        const rowText = row.textContent.toLowerCase();
        return rowText.includes(query);
      });

      const totalItems = matchedRows.length;
      const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));

      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

      // Hide all standard rows
      allViewRows.forEach(function (row) {
        row.style.display = 'none';
        // Also hide edit row if associated
        const rowId = row.id;
        if (rowId && (rowId.includes('cat-row-view-') || rowId.includes('tag-row-view-'))) {
          const editRowId = rowId.replace('-view-', '-edit-');
          const editRow = document.getElementById(editRowId);
          if (editRow) editRow.style.display = 'none';
        }
      });

      // Show matching rows for active page
      for (let i = startIndex; i < endIndex; i++) {
        if (matchedRows[i]) {
          matchedRows[i].style.display = 'table-row';
        }
      }

      // Update Pagination UI
      if (paginationWrapper) {
        const pageRangeEl = paginationWrapper.querySelector('.page-range');
        const totalCountEl = paginationWrapper.querySelector('.total-count');
        const pageIndicatorEl = paginationWrapper.querySelector('.page-indicator');
        const prevBtn = paginationWrapper.querySelector('.page-prev-btn');
        const nextBtn = paginationWrapper.querySelector('.page-next-btn');

        if (totalCountEl) totalCountEl.textContent = totalItems;
        if (pageRangeEl) {
          if (totalItems === 0) {
            pageRangeEl.textContent = '0';
          } else {
            pageRangeEl.textContent = `${startIndex + 1}-${endIndex}`;
          }
        }
        if (pageIndicatorEl) {
          pageIndicatorEl.textContent = `Trang ${currentPage} / ${totalPages}`;
        }

        if (prevBtn) prevBtn.disabled = (currentPage <= 1);
        if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);
      }
    }

    if (searchInput) {
      searchInput.addEventListener('input', function (e) {
        searchQuery = e.target.value;
        currentPage = 1;
        updateTableState();
      });
    }

    if (paginationWrapper) {
      const prevBtn = paginationWrapper.querySelector('.page-prev-btn');
      const nextBtn = paginationWrapper.querySelector('.page-next-btn');

      if (prevBtn) {
        prevBtn.addEventListener('click', function () {
          if (currentPage > 1) {
            currentPage--;
            updateTableState();
          }
        });
      }

      if (nextBtn) {
        nextBtn.addEventListener('click', function () {
          if (currentPage < Math.ceil(allViewRows.filter(r => !searchQuery || r.textContent.toLowerCase().includes(searchQuery.trim().toLowerCase())).length / itemsPerPage)) {
            currentPage++;
            updateTableState();
          }
        });
      }
    }

    updateTableState();
  });
}

/**
 * Client-Side Form Validation Module for Patched Mode
 * Automatically validates input fields for all forms in the application
 * only when the system is running under 'patched' mode.
 */
function initClientSideValidation() {
  const isPatched = window.APP_MODE === 'patched' || document.body.dataset.mode === 'patched';
  if (!isPatched) return; // Client validation strictly active in Patched Mode

  function clearErrors(form) {
    form.querySelectorAll('.is-invalid').forEach(function (el) {
      el.classList.remove('is-invalid');
    });
    const ckEditor = form.querySelector('.ck.ck-editor');
    if (ckEditor) ckEditor.classList.remove('is-invalid');
    const tagBox = form.querySelector('.tag-input-box');
    if (tagBox) tagBox.classList.remove('is-invalid');

    form.querySelectorAll('.form-error-msg').forEach(function (el) {
      el.remove();
    });
  }

  function showError(input, message) {
    if (!input) return;
    input.classList.add('is-invalid');

    // Special styling for CKEditor hidden textarea & Tag multiselect box
    if (input.id === 'editor' || input.name === 'content') {
      const ckEditor = input.closest('.form-group')?.querySelector('.ck.ck-editor');
      if (ckEditor) ckEditor.classList.add('is-invalid');
    }
    if (input.classList.contains('tag-text-input')) {
      const tagBox = input.closest('.tag-input-box');
      if (tagBox) tagBox.classList.add('is-invalid');
    }

    const parent = input.closest('.form-group') || input.closest('tr') || input.parentElement;
    if (!parent) return;

    let errorEl = parent.querySelector('.form-error-msg');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.className = 'form-error-msg';
      errorEl.style.cssText = 'color: #dc2626 !important; font-size: 0.75rem !important; font-weight: 500 !important; margin-top: 0.35rem !important; display: flex !important; align-items: center !important; gap: 0.35rem !important; line-height: 1.35 !important; width: 100% !important; flex-basis: 100% !important;';
      errorEl.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 12px !important; height: 12px !important; flex-shrink: 0 !important; stroke: #dc2626 !important;"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg> <span style="color: #dc2626 !important; font-size: 0.75rem !important; font-weight: 500 !important;"></span>';
      errorEl.querySelector('span').textContent = message;

      if (input.classList.contains('tag-text-input')) {
        const wrapper = input.closest('.tag-select-wrapper');
        if (wrapper && wrapper.parentElement) {
          wrapper.parentElement.appendChild(errorEl);
        } else {
          parent.appendChild(errorEl);
        }
      } else if (input.parentElement && input.parentElement.classList.contains('password-input-wrapper')) {
        input.parentElement.parentElement.appendChild(errorEl);
      } else {
        parent.appendChild(errorEl);
      }
    } else {
      const span = errorEl.querySelector('span');
      if (span) {
        span.style.cssText = 'color: #dc2626 !important; font-size: 0.75rem !important; font-weight: 500 !important;';
        span.textContent = message;
      }
    }
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function isAllowedImageFile(file) {
    if (!file) return true;
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    const ext = file.name.split('.').pop().toLowerCase();
    return allowedExtensions.includes(ext);
  }

  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (!form || form.tagName !== 'FORM') return;

    // Ignore search bar form (GET method)
    if (form.classList.contains('search-form') || (form.method && form.method.toUpperCase() === 'GET')) {
      return;
    }

    clearErrors(form);
    let isValid = true;
    let firstInvalidInput = null;

    function invalidate(input, msg) {
      isValid = false;
      showError(input, msg);
      if (!firstInvalidInput && input) {
        firstInvalidInput = input;
      }
    }

    let actionPath = '';
    try {
      const rawAction = form.getAttribute('action') || form.action || '';
      actionPath = new URL(rawAction, window.location.origin).pathname.toLowerCase();
    } catch (err) {
      actionPath = (form.getAttribute('action') || form.action || '').toLowerCase();
    }

    // 1. Login Form (/login)
    if (actionPath.endsWith('/login')) {
      const emailInput = form.querySelector('input[name="email"]');
      const passInput = form.querySelector('input[name="password"]');

      if (emailInput) {
        const val = emailInput.value.trim();
        if (!val) {
          invalidate(emailInput, 'Vui lòng nhập Email hoặc Username.');
        } else if (val.includes('@') && !isValidEmail(val)) {
          invalidate(emailInput, 'Địa chỉ Email không đúng định dạng (ví dụ: user@example.com).');
        }
      }

      if (passInput) {
        if (!passInput.value) {
          invalidate(passInput, 'Vui lòng nhập mật khẩu.');
        } else if (passInput.value.length < 4) {
          invalidate(passInput, 'Mật khẩu phải chứa ít nhất 4 ký tự.');
        }
      }
    }

    // 2. Register Form (/register)
    else if (actionPath.endsWith('/register')) {
      const emailInput = form.querySelector('input[name="email"]');
      const passInput = form.querySelector('input[name="password"]');
      const confirmInput = form.querySelector('input[name="confirm_password"]');

      if (emailInput) {
        const val = emailInput.value.trim();
        if (!val) {
          invalidate(emailInput, 'Vui lòng nhập địa chỉ Email.');
        } else if (!isValidEmail(val)) {
          invalidate(emailInput, 'Định dạng Email không hợp lệ (ví dụ: user@example.com).');
        }
      }

      if (passInput) {
        if (!passInput.value) {
          invalidate(passInput, 'Vui lòng nhập mật khẩu.');
        } else if (passInput.value.length < 6) {
          invalidate(passInput, 'Mật khẩu đăng ký phải từ 6 ký tự trở lên.');
        }
      }

      if (confirmInput && passInput) {
        if (!confirmInput.value) {
          invalidate(confirmInput, 'Vui lòng nhập lại mật khẩu để xác nhận.');
        } else if (confirmInput.value !== passInput.value) {
          invalidate(confirmInput, 'Mật khẩu xác nhận không trùng khớp với mật khẩu đã nhập.');
        }
      }
    }

    // 3. Profile Update Form (/profile/update)
    else if (actionPath.endsWith('/profile/update')) {
      const bioInput = form.querySelector('input[name="bio"]');
      const fileInput = form.querySelector('input[name="avatar"]');

      if (bioInput && bioInput.value.length > 500) {
        invalidate(bioInput, 'Tiểu sử không được vượt quá 500 ký tự.');
      }

      if (fileInput && fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        if (!isAllowedImageFile(file)) {
          invalidate(fileInput, 'Định dạng tệp không được hỗ trợ. Chỉ chấp nhận tệp ảnh (.jpg, .jpeg, .png, .gif, .webp, .svg).');
        } else if (file.size > 5 * 1024 * 1024) {
          invalidate(fileInput, 'Kích thước ảnh đại diện không được vượt quá 5MB.');
        }
      }
    }

    // 4 & 5. Create / Edit Post Forms (/post/create or /post/edit/*)
    else if (actionPath.includes('/post/create') || actionPath.includes('/post/edit/')) {
      const titleInput = form.querySelector('input[name="title"]');
      const categorySelect = form.querySelector('select[name="category_id"]');
      const contentTextarea = form.querySelector('textarea[name="content"]');
      const fileInput = form.querySelector('input[name="image"]');

      if (titleInput) {
        const val = titleInput.value.trim();
        if (!val) {
          invalidate(titleInput, 'Tiêu đề bài viết không được để trống.');
        } else if (val.length < 3) {
          invalidate(titleInput, 'Tiêu đề bài viết phải chứa ít nhất 3 ký tự.');
        } else if (val.length > 200) {
          invalidate(titleInput, 'Tiêu đề bài viết không được vượt quá 200 ký tự.');
        }
      }

      if (categorySelect) {
        if (!categorySelect.value) {
          invalidate(categorySelect, 'Vui lòng chọn danh mục bài viết.');
        }
      }

      if (contentTextarea) {
        if (window.editorInstance) {
          contentTextarea.value = window.editorInstance.getData();
        }
        const textContent = contentTextarea.value.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
        if (!textContent && !contentTextarea.value.trim()) {
          invalidate(contentTextarea, 'Nội dung bài viết không được để trống.');
        }
      }

      if (fileInput && fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        if (!isAllowedImageFile(file)) {
          invalidate(fileInput, 'Định dạng tệp đính kèm không hợp lệ. Chỉ chấp nhận tệp ảnh (.jpg, .jpeg, .png, .gif, .webp, .svg).');
        } else if (file.size > 10 * 1024 * 1024) {
          invalidate(fileInput, 'Dung lượng tệp đính kèm không được vượt quá 10MB.');
        }
      }
    }

    // 6. Comment Form (/comment)
    else if (actionPath.includes('/comment')) {
      const commentTextarea = form.querySelector('textarea[name="content"]');
      if (commentTextarea) {
        const val = commentTextarea.value.trim();
        if (!val) {
          invalidate(commentTextarea, 'Vui lòng nhập nội dung bình luận.');
        } else if (val.length > 1000) {
          invalidate(commentTextarea, 'Nội dung bình luận quá dài (tối đa 1000 ký tự).');
        }
      }
    }

    // 7 & 8. Admin Add / Edit Category Forms (/admin/category/*)
    else if (actionPath.includes('/admin/category/')) {
      const nameInput = form.querySelector('input[name="name"]');
      const slugInput = form.querySelector('input[name="slug"]');

      if (nameInput) {
        const val = nameInput.value.trim();
        if (!val) {
          invalidate(nameInput, 'Tên danh mục không được để trống.');
        } else if (val.length > 100) {
          invalidate(nameInput, 'Tên danh mục không được vượt quá 100 ký tự.');
        }
      }

      if (slugInput && slugInput.value.trim()) {
        const slugVal = slugInput.value.trim();
        if (!/^[a-zA-Z0-9_\-]+$/.test(slugVal)) {
          invalidate(slugInput, 'Slug chỉ bao gồm chữ cái, số, dấu gạch ngang (-) và gạch dưới (_).');
        }
      }
    }

    // 9 & 10. Admin Add / Edit Tag Forms (/admin/tag/*)
    else if (actionPath.includes('/admin/tag/')) {
      const nameInput = form.querySelector('input[name="name"]');
      const slugInput = form.querySelector('input[name="slug"]');

      if (nameInput) {
        const val = nameInput.value.trim().replace(/^#/, '');
        if (!val) {
          invalidate(nameInput, 'Tên thẻ tag không được để trống.');
        } else if (val.length > 50) {
          invalidate(nameInput, 'Tên thẻ tag không được vượt quá 50 ký tự.');
        }
      }

      if (slugInput && slugInput.value.trim()) {
        const slugVal = slugInput.value.trim();
        if (!/^[a-zA-Z0-9_\-]+$/.test(slugVal)) {
          invalidate(slugInput, 'Slug chỉ bao gồm chữ cái, số, dấu gạch ngang (-) và gạch dưới (_).');
        }
      }
    }

    // 11. Admin Edit User Form (#editUserForm or action includes /admin/user/*/edit)
    else if (form.id === 'editUserForm' || actionPath.includes('/admin/user/')) {
      const usernameInput = form.querySelector('input[name="username"]');
      const emailInput = form.querySelector('input[name="email"]');

      if (usernameInput) {
        const val = usernameInput.value.trim();
        if (!val) {
          invalidate(usernameInput, 'Tên người dùng không được để trống.');
        } else if (val.length < 3) {
          invalidate(usernameInput, 'Tên người dùng phải chứa ít nhất 3 ký tự.');
        } else if (!/^[a-zA-Z0-9_\-\.]+$/.test(val)) {
          invalidate(usernameInput, 'Tên người dùng chỉ bao gồm chữ cái, số, dấu chấm, gạch dưới và gạch ngang.');
        }
      }

      if (emailInput && emailInput.value.trim()) {
        if (!isValidEmail(emailInput.value.trim())) {
          invalidate(emailInput, 'Định dạng Email không hợp lệ.');
        }
      }
    }

    // Generic fallback for any other forms with HTML5 required attributes
    else {
      const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
      requiredInputs.forEach(function (input) {
        if (!input.value.trim()) {
          invalidate(input, 'Trường dữ liệu này là bắt buộc.');
        }
      });
    }

    if (!isValid) {
      e.preventDefault();
      e.stopPropagation();
      if (firstInvalidInput) {
        if ((firstInvalidInput.id === 'editor' || firstInvalidInput.name === 'content') && window.editorInstance) {
          try {
            window.editorInstance.editing.view.focus();
          } catch (err) {}
          const ckEditor = firstInvalidInput.closest('.form-group')?.querySelector('.ck.ck-editor');
          if (ckEditor) ckEditor.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          try {
            firstInvalidInput.focus();
          } catch (err) {}
          firstInvalidInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }
  }, true);

  // Live input error clearing on user typing & select/file change
  function clearInputError(input) {
    if (!input || !input.classList) return;

    if (input.classList.contains('is-invalid')) {
      input.classList.remove('is-invalid');

      if (input.id === 'editor' || input.name === 'content') {
        const ckEditor = input.closest('.form-group')?.querySelector('.ck.ck-editor');
        if (ckEditor) ckEditor.classList.remove('is-invalid');
      }
      if (input.classList.contains('tag-text-input')) {
        const tagBox = input.closest('.tag-input-box');
        if (tagBox) tagBox.classList.remove('is-invalid');
      }

      const parent = input.closest('.form-group') || input.closest('tr') || input.parentElement;
      if (parent) {
        const err = parent.querySelector('.form-error-msg');
        if (err) err.remove();
      }
    }
  }

  document.addEventListener('input', function (e) {
    clearInputError(e.target);
  });

  document.addEventListener('change', function (e) {
    clearInputError(e.target);
  });
}



