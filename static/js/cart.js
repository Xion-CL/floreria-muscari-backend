/**
 * Clase para manejar el carrito de compras
 */
class Cart {
    constructor() {
        this.storageKey = 'cabaña_muscari_cart';
        this.items = this.load();
        this.updateBadge();
    }

    /**
     * Carga el carrito desde localStorage
     */
    load() {
        const cart = localStorage.getItem(this.storageKey);
        return cart ? JSON.parse(cart) : [];
    }

    /**
     * Guarda el carrito en localStorage
     */
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.updateBadge();
    }

    /**
     * Agrega un producto al carrito
     */
    add(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                quantity: 1,
                image: product.image || ''
            });
        }
        
        this.save();
        Utils.showNotification(`${product.name} agregado al carrito`);
    }

    /**
     * Elimina un producto del carrito
     */
    remove(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.save();
        Utils.showNotification('Producto eliminado del carrito');
    }

    /**
     * Actualiza la cantidad de un producto
     */
    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.remove(productId);
            } else {
                item.quantity = quantity;
                this.save();
            }
        }
    }

    /**
     * Obtiene el total del carrito
     */
    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    /**
     * Obtiene la cantidad total de items
     */
    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }

    /**
     * Actualiza el badge del carrito en el navbar
     */
    updateBadge() {
        const badge = document.getElementById('cartBadge');
        if (badge) {
            const count = this.getItemCount();
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Vacía el carrito
     */
    clear() {
        this.items = [];
        this.save();
        Utils.showNotification('Carrito vaciado');
    }
}

// Instancia global del carrito
window.cart = new Cart();