document.addEventListener('DOMContentLoaded', function () {
    // [S] init sidebar menu state
    const playSubmenu = document.getElementById('playSubmenu');
    const userSubmenu = document.getElementById('userSubmenu');
    const playToggle = document.querySelector('[href="#playSubmenu"]');
    const userToggle = document.querySelector('[href="#userSubmenu"]');

    // show play menu by default when page loads
    playSubmenu.classList.add('show');
    playToggle.querySelector('.menu-toggle i').classList.add('rotated');
    // [E] init sidebar menu state

    // [S] tab switching logic
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // stop normal link behavior

            // get target tab content area
            const target = this.getAttribute('href');
            const tabPane = document.querySelector(target);

            if (tabPane) {
                // hide all other tab contents
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });

                // show current tab content
                tabPane.classList.add('show', 'active');

                // update active tab link
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    // [E] tab switching logic

    // [S] sidebar menu collapse functionality
    document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
        toggle.addEventListener('click', function () {
            // get target menu element
            const target = this.getAttribute('href');
            const menu = document.querySelector(target);
            const icon = this.querySelector('.menu-toggle i');

            // close other menus when opening a new one
            if (target === '#playSubmenu') {
                userSubmenu.classList.remove('show');
                userToggle.querySelector('.menu-toggle i').classList.remove('rotated');
                userToggle.classList.add('collapsed');
            } else if (target === '#userSubmenu') {
                playSubmenu.classList.remove('show');
                playToggle.querySelector('.menu-toggle i').classList.remove('rotated');
                playToggle.classList.add('collapsed');
            }

            // toggle current menu visibility
            menu.classList.toggle('show');
            icon.classList.toggle('rotated'); // rotate toggle icon

            // update collapsed state attribute
            if (menu.classList.contains('show')) {
                this.classList.remove('collapsed');
            } else {
                this.classList.add('collapsed');
            }
        });
    });
    // [E] sidebar menu collapse functionality

    // [S] remember open categories in session storage
    const openCategories = {}; // track open categories

    document.querySelectorAll('.accordion-collapse').forEach(collapse => {
        // when category is opened
        collapse.addEventListener('shown.bs.collapse', function () {
            openCategories[this.id] = true;
            sessionStorage.setItem('openOptions', JSON.stringify(openCategories));
        });

        // when category is closed
        collapse.addEventListener('hidden.bs.collapse', function () {
            delete openCategories[this.id];
            sessionStorage.setItem('openOptions', JSON.stringify(openCategories));
        });
    });

    // restore open categories when page loads
    const savedOpen = sessionStorage.getItem('openOptions');
    if (savedOpen) {
        const openState = JSON.parse(savedOpen);
        Object.keys(openState).forEach(id => {
            const collapse = document.getElementById(id);
            if (collapse) {
                // bootstrap function to open accordion items
                new bootstrap.Collapse(collapse, {toggle: true});
            }
        });
    }
    // [E] remember open categories in session storage

    // [S] option item interaction
    document.querySelectorAll('.option-item').forEach(item => {
        item.addEventListener('click', function (e) {
            // skip if user clicked action buttons
            if (e.target.closest('.action-btn')) return;

            // close any other open options
            document.querySelectorAll('.option-item.editing').forEach(openItem => {
                if (openItem !== this) {
                    openItem.classList.remove('editing');
                }
            });

            // toggle editing mode for clicked option
            this.classList.toggle('editing');
        });
    });
    // [E] option item interaction

    // [S] close button functionality
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation(); // prevent option item click
            this.closest('.option-item').classList.remove('editing');
        });
    });
    // [E] close button functionality

    // [S] play option form handling
    const playTypeSelect = document.getElementById('playTypeSelect');
    const offPlayCategoryDiv = document.getElementById('offPlayCategoryDiv');
    const playCategorySelect = document.getElementById('playCategorySelect');
    const addOptionForm = document.getElementById('addOptionForm');

    // show/hide category field based on selection
    function updateOffPlayCategoryVisibility() {
        const selected = playTypeSelect.value;
        if (selected === 'off_play') {
            offPlayCategoryDiv.classList.remove('d-none');
            playCategorySelect.setAttribute('required', 'required');
        } else {
            offPlayCategoryDiv.classList.add('d-none');
            playCategorySelect.removeAttribute('required');
            playCategorySelect.value = ''; // clear selection
        }
    }

    // update form when play type changes
    playTypeSelect.addEventListener('change', () => {
        updateOffPlayCategoryVisibility();
        const selectedParam = playTypeSelect.value;
        if (selectedParam) {
            // update form action with selected type
            addOptionForm.action = `/settings/option/add/${encodeURIComponent(selectedParam)}`;
        } else {
            addOptionForm.action = '#';
        }
    });

    // reset form when modal opens
    const addOptionModal = document.getElementById('addOptionModal');
    addOptionModal.addEventListener('show.bs.modal', () => {
        playTypeSelect.value = '';
        offPlayCategoryDiv.classList.add('d-none');
        playCategorySelect.value = '';
        playCategorySelect.removeAttribute('required');
        addOptionForm.action = '#'; // reset form action
        addOptionForm.reset(); // clear all form fields
    });
    // [E] play option form handling
});