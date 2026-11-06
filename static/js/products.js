/**
 * Clase para manejar productos y la API
 */
class ProductAPI {
    constructor() {
        this.baseUrl = '/api';
    }

    async getFeaturedProducts() {
        console.log('🔍 Cargando productos desde:', `${this.baseUrl}/productos-destacados/`);
        
        try {
            const response = await fetch(`${this.baseUrl}/productos-destacados/`);
            console.log('📡 Status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Productos recibidos:', data.results?.length || data.length || 0);
            
            // Log para depurar las imágenes
            if (data.results && data.results.length > 0) {
                console.log('🖼️  Primera imagen:', data.results[0].imagen_principal);
            }
            
            return data.results || data;
        } catch (error) {
            console.error('❌ Error al cargar productos:', error);
            return [];
        }
    }
}

/**
 * Clase para renderizar productos
 */
class ProductUI {
    constructor() {
        this.api = new ProductAPI();
    }

    async loadAndRender(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('❌ Contenedor no encontrado:', containerId);
            return;
        }

        console.log('⏳ Iniciando carga de productos...');
        const products = await this.api.getFeaturedProducts();
        
        if (!products || products.length === 0) {
            console.warn('⚠️ No hay productos para mostrar');
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: #888;">
                    <i class="fas fa-box-open" style="font-size: 60px; margin-bottom: 20px; color: var(--pink-light);"></i>
                    <h3>No hay productos disponibles</h3>
                    <p>Vuelve pronto para ver nuestras novedades</p>
                </div>
            `;
            return;
        }

        console.log('🎨 Renderizando', products.length, 'productos...');
        container.innerHTML = products.map(p => this.createCard(p)).join('');
        console.log('✅ Productos renderizados correctamente');
    }

    createCard(product) {
        // ✅ USAR la imagen de la base de datos, no un mapeo hardcoded
        const imageUrl = product.imagen_principal || '';
        const detalleUrl = `/catalogo/producto/${product.slug}/`;
        const safe = (t) => String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
        const imgHTML = imageUrl
            ? `<img src="${safe(imageUrl)}" alt="${safe(product.nombre)}" loading="lazy">`
            : `<div class="ph">🌸</div>`;
        
        const badgeText = this.getBadgeText(product.badge);
        const badgeHTML = product.badge !== 'NINGUNO' 
            ? `<span class="product-tag">${badgeText}</span>` 
            : '';
        
        const oldPriceHTML = product.tiene_descuento 
            ? `<span class="old-price">$${this.formatMoney(product.precio_original)}</span>` 
            : '';

        return `
            <div class="product-card" data-product-id="${product.id}" data-name="${safe(product.nombre)}" data-price="${Number(product.precio_final)}" data-image="${safe(imageUrl)}">
                <div class="product-img">
                    <a href="${detalleUrl}">${imgHTML}</a>
                    ${badgeHTML}
                    <button class="product-fav" onclick="app.toggleFavorite(${product.id})">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
                <div class="product-info">
                    <h3><a href="${detalleUrl}">${safe(product.nombre)}</a></h3>
                    <p class="product-description">${safe(product.descripcion_corta)}</p>
                    <div class="product-rating">
                        <span class="stars">
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                        </span>
                        <span class="rating-text">(0 reseñas)</span>
                    </div>
                    <div class="product-price-row">
                        <div class="product-price">
                            ${oldPriceHTML}
                            $${this.formatMoney(product.precio_final)}
                        </div>
                        <button class="btn-add-cart" onclick="app.addToCart(${product.id})">
                            <i class="fas fa-cart-plus"></i> Agregar
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    formatMoney(amount) {
        return Number(amount).toLocaleString('es-CL');
    }

    getBadgeText(badge) {
        const badges = {
            'MAS_VENDIDO': '⭐ Más vendido',
            'POPULAR': '🔥 Popular',
            'PREMIUM': '💎 Premium',
            'NUEVO': '🌸 Nuevo',
            'OFERTA': '💝 Oferta',
            'COMBO': '💝 Combo'
        };
        return badges[badge] || badge;
    }
}

// Exportar para uso global
window.ProductUI = ProductUI;