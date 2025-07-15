document.addEventListener('DOMContentLoaded', function () {
    // [S] Sidebar submenu toggle
    const playSubmenu = document.getElementById('playSubmenu');
    const userSubmenu = document.getElementById('userSubmenu');
    const playToggle = document.querySelector('[href="#playSubmenu"]');
    const userToggle = document.querySelector('[href="#userSubmenu"]');

    // Restore last opened submenu
    // const lastOpenMenu = sessionStorage.getItem('activeSidebar');
    // if (lastOpenMenu) {
    //     const menu = document.querySelector(lastOpenMenu);
    //     if (menu) {
    //         new bootstrap.Collapse(menu, {toggle: true});
    //     }
    // }

    document.querySelectorAll('.submenu').forEach(sub => {
        sub.addEventListener('shown.bs.collapse', function () {
            const toggleLink = document.querySelector(`[href="#${this.id}"]`);
            toggleLink?.querySelector('.menu-toggle i')?.classList.add('rotated');
            toggleLink?.classList.remove('collapsed');
        });

        sub.addEventListener('hidden.bs.collapse', function () {
            const toggleLink = document.querySelector(`[href="#${this.id}"]`);
            toggleLink?.querySelector('.menu-toggle i')?.classList.remove('rotated');
            toggleLink?.classList.add('collapsed');
        });
    });

    // Sidebar menu toggle handler
    document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
        toggle.addEventListener('click', function () {
            const target = this.getAttribute('href');
            const menu = document.querySelector(target);
            const icon = this.querySelector('.menu-toggle i');

            // Close other menu
            if (target === '#playSubmenu') {
                userSubmenu.classList.remove('show');
                userToggle.querySelector('.menu-toggle i')?.classList.remove('rotated');
                userToggle.classList.add('collapsed');
            } else if (target === '#userSubmenu') {
                playSubmenu.classList.remove('show');
                playToggle.querySelector('.menu-toggle i')?.classList.remove('rotated');
                playToggle.classList.add('collapsed');
            }

            const collapse = bootstrap.Collapse.getOrCreateInstance(menu);
            collapse.toggle();

            icon.classList.toggle('rotated', isNowOpen);
            this.classList.toggle('collapsed', !isNowOpen);

            // Save submenu
            if (isNowOpen) {
                sessionStorage.setItem('activeSidebar', target);
            } else {
                sessionStorage.removeItem('activeSidebar');
            }
        });
    });
    // [E] Sidebar submenu toggle

    // [S] Tab switching logic
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const target = this.getAttribute('href');
            const tabPane = document.querySelector(target);

            if (tabPane) {
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('show', 'active'));
                document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));

                tabPane.classList.add('show', 'active');
                this.classList.add('active');

                // Save active tab
                sessionStorage.setItem('activeTab', target);
            }
        });
    });

    // Restore last active tab
    const savedTab = sessionStorage.getItem('activeTab');
    if (savedTab) {
        const savedLink = document.querySelector(`[data-bs-toggle="tab"][href="${savedTab}"]`);
        if (savedLink) savedLink.click();
    }
    // [E] Tab switching logic

    // [S] Accordion open category memory
    const openCategories = {};

    document.querySelectorAll('.accordion-collapse').forEach(collapse => {
        collapse.addEventListener('shown.bs.collapse', function () {
            openCategories[this.id] = true;
            sessionStorage.setItem('openOptions', JSON.stringify(openCategories));
        });

        collapse.addEventListener('hidden.bs.collapse', function () {
            delete openCategories[this.id];
            sessionStorage.setItem('openOptions', JSON.stringify(openCategories));
        });
    });

    const savedOpen = sessionStorage.getItem('openOptions');
    if (savedOpen) {
        const openState = JSON.parse(savedOpen);
        Object.keys(openState).forEach(id => {
            const collapse = document.getElementById(id);
            if (collapse) {
                new bootstrap.Collapse(collapse, {toggle: true});
                const toggleLink = document.querySelector(`[href="#${id}"]`);
                toggleLink?.querySelector('.menu-toggle i')?.classList.add('rotated');
                toggleLink?.classList.remove('collapsed');
            }
        });
    }
    // [E] Accordion open memory

    // [S] Option-item editing mode
    document.querySelectorAll('.option-item').forEach(item => {
        item.addEventListener('click', function (e) {
            if (e.target.closest('.action-btn')) return;
            document.querySelectorAll('.option-item.editing').forEach(openItem => {
                if (openItem !== this) openItem.classList.remove('editing');
            });
            this.classList.toggle('editing');
        });
    });

    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            this.closest('.option-item')?.classList.remove('editing');
        });
    });
    // [E] Option-item editing mode

    // [S] Play option form behavior
    const playTypeSelect = document.getElementById('playTypeSelect');
    const offPlayCategoryDiv = document.getElementById('offPlayCategoryDiv');
    const playCategorySelect = document.getElementById('playCategorySelect');
    const addOptionForm = document.getElementById('addOptionForm');

    function updateOffPlayCategoryVisibility() {
        const selected = playTypeSelect.value;
        if (selected === 'off_play') {
            offPlayCategoryDiv.classList.remove('d-none');
            playCategorySelect.setAttribute('required', 'required');
        } else {
            offPlayCategoryDiv.classList.add('d-none');
            playCategorySelect.removeAttribute('required');
            playCategorySelect.value = '';
        }
    }

    playTypeSelect?.addEventListener('change', () => {
        updateOffPlayCategoryVisibility();
        const selectedParam = playTypeSelect.value;
        addOptionForm.action = selectedParam ? `/settings/play/option/add/${encodeURIComponent(selectedParam)}` : '#';
    });

    const addOptionModal = document.getElementById('addOptionModal');
    addOptionModal?.addEventListener('show.bs.modal', () => {
        playTypeSelect.value = '';
        offPlayCategoryDiv.classList.add('d-none');
        playCategorySelect.value = '';
        playCategorySelect.removeAttribute('required');
        addOptionForm.action = '#';
        addOptionForm.reset();
    });
    // [E] Play option form

    // [S] Save UI state before navigating away
    window.addEventListener('beforeunload', () => {
        const openMenu = document.querySelector('.collapse.show');
        if (openMenu) {
            sessionStorage.setItem('activeSidebar', `#${openMenu.id}`);
        }

        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab) {
            sessionStorage.setItem('activeTab', activeTab.getAttribute('href'));
        }
    });
    // [E] Save UI state on unload
});

