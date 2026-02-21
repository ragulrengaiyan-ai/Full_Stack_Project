// Mobile Navigation - Hamburger Menu Handler
document.addEventListener('DOMContentLoaded', function () {
    const header = document.querySelector('header');
    if (!header) return;

    // Create toggle button
    const menuToggle = document.createElement('div');
    menuToggle.className = 'menu-toggle';
    menuToggle.setAttribute('aria-label', 'Toggle navigation');
    menuToggle.setAttribute('role', 'button');
    menuToggle.setAttribute('tabindex', '0');
    menuToggle.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    header.appendChild(menuToggle);

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);

    const nav = header.querySelector('nav');

    function openMenu() {
        nav.classList.add('open');
        overlay.classList.add('active');
        menuToggle.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        nav.classList.remove('open');
        overlay.classList.remove('active');
        menuToggle.classList.remove('active');
        document.body.style.overflow = '';
    }

    menuToggle.addEventListener('click', function () {
        if (nav.classList.contains('open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    overlay.addEventListener('click', closeMenu);

    // Close on nav link click
    if (nav) {
        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeMenu);
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMenu();
    });
});
