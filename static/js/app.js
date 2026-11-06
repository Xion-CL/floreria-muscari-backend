/**
 * Clase principal de la aplicación
 */
class App {
    constructor() {
        this.cart = window.cart;
        this.productUI = new ProductUI();
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log(' Inicializando aplicación...');
            this.setupEventListeners();
            this.loadFeaturedProducts();
        });
    }

    setupEventListeners() {
        // Botón "Ver Productos": baja a la sección de productos destacados
        const verProductosBtn = document.getElementById('verProductosBtn');
        if (verProductosBtn) {
            verProductosBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const container = document.getElementById('productos-container');
                if (container) container.scrollIntoView({ behavior: 'smooth' });
            });
        }
    }

    async loadFeaturedProducts() {
        // Solo en páginas que tienen el contenedor de destacados (inicio)
        if (!document.getElementById('productos-container')) return;
        await this.productUI.loadAndRender('productos-container');
    }

    addToCart(productId) {
        // Los datos salen de atributos data-* de la tarjeta (más fiable que leer el texto del precio)
        const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);
        if (!card) {
            console.error('Producto no encontrado:', productId);
            return;
        }
        this.cart.add({
            id: Number(productId),
            name: card.dataset.name || 'Producto',
            price: Number(card.dataset.price) || 0,
            image: card.dataset.image || ''
        });
    }

    toggleFavorite(productId) {
        const btn = document.querySelector(`[data-product-id="${productId}"] .product-fav`);
        if (!btn) return;

        const icon = btn.querySelector('i');
        const isFavorite = icon.classList.contains('fas');

        if (isFavorite) {
            icon.classList.remove('fas');
            icon.classList.add('far');
            btn.classList.remove('active');
            if (window.Utils) Utils.showNotification('Eliminado de favoritos');
        } else {
            icon.classList.remove('far');
            icon.classList.add('fas');
            btn.classList.add('active');
            if (window.Utils) Utils.showNotification('Agregado a favoritos');
        }
    }
}

// Crear instancia global
window.app = new App();