/**
 * Navbar: menú hamburguesa (móvil/tablet) y dropdowns (escritorio y móvil).
 *  - Escritorio (>=1024px): los dropdowns se abren con el mouse (CSS :hover) y con el teclado.
 *  - Móvil/tablet: la hamburguesa abre/cierra el menú y los dropdowns funcionan como acordeón.
 */
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('mobileMenuToggle');
    const nav = document.getElementById('navBar');
    const escritorio = window.matchMedia('(min-width: 1024px)');
    const conHover = window.matchMedia('(hover: hover)');

    function cerrarDropdowns(excepto) {
        document.querySelectorAll('[data-dropdown].open').forEach(function (d) {
            if (d !== excepto) {
                d.classList.remove('open');
                const b = d.querySelector('.dropdown-toggle');
                if (b) b.setAttribute('aria-expanded', 'false');
            }
        });
    }

    function setMenu(abierto) {
        if (!nav || !toggle) return;
        nav.classList.toggle('open', abierto);
        toggle.setAttribute('aria-expanded', String(abierto));
        toggle.classList.toggle('is-open', abierto);
        toggle.setAttribute('aria-label', abierto ? 'Cerrar menú' : 'Abrir menú');
        if (!abierto) cerrarDropdowns(null);
    }

    // Hamburguesa
    if (toggle && nav) {
        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            setMenu(!nav.classList.contains('open'));
        });
    }

    // Dropdowns
    document.querySelectorAll('[data-dropdown] > .dropdown-toggle').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            // En escritorio con mouse el menú ya se abre por :hover; solo reaccionamos
            // al teclado (Enter/Espacio generan click con detail === 0) y a pantallas táctiles.
            if (escritorio.matches && conHover.matches && e.detail !== 0) return;
            const cont = btn.closest('[data-dropdown]');
            const abrir = !cont.classList.contains('open');
            cerrarDropdowns(cont);
            cont.classList.toggle('open', abrir);
            btn.setAttribute('aria-expanded', String(abrir));
        });
    });

    // Clic fuera: cierra dropdowns y el menú móvil
    document.addEventListener('click', function (e) {
        if (!e.target.closest('[data-dropdown]')) cerrarDropdowns(null);
        if (nav && nav.classList.contains('open') && !e.target.closest('#navBar') && !e.target.closest('#mobileMenuToggle')) {
            setMenu(false);
        }
    });

    // Escape cierra todo
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { cerrarDropdowns(null); setMenu(false); }
    });

    // Al pasar a escritorio, se restablece el estado
    function alCambiarTamano() { if (escritorio.matches) setMenu(false); }
    if (escritorio.addEventListener) escritorio.addEventListener('change', alCambiarTamano);
    else if (escritorio.addListener) escritorio.addListener(alCambiarTamano);
});
