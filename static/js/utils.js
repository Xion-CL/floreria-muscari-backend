/**
 * Clase de utilidades generales
 */
class Utils {
    /**
     * Formatea un número como moneda chilena
     */
    static formatMoney(amount) {
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: 'CLP',
            minimumFractionDigits: 0
        }).format(amount);
    }

    /**
     * Muestra una notificación temporal
     */
    static showNotification(message, type = 'success') {
        const notif = document.createElement('div');
        notif.className = `notification notification-${type}`;
        notif.textContent = message;
        notif.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'success' ? 'var(--magenta-dark)' : '#dc3545'};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notif);
        
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notif.remove(), 300);
        }, 3000);
    }

    /**
     * Obtiene el texto del badge según el tipo
     */
    static getBadgeText(badge) {
        const badges = {
            'MAS_VENDIDO': '⭐ Más vendido',
            'POPULAR': ' Popular',
            'PREMIUM': '💎 Premium',
            'NUEVO': '🌸 Nuevo',
            'OFERTA': '💝 Oferta',
            'COMBO': '💝 Combo'
        };
        return badges[badge] || badge;
    }

    /**
     * Agrega animaciones CSS dinámicamente
     */
    static addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Inicializar animaciones
Utils.addAnimationStyles();