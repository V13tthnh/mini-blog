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


