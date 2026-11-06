"""Datos del catálogo de La Cabaña de Muscari (usados por el comando seed_demo)."""

CATEGORIAS = [
    # (nombre, icono, descripción, orden)
    ('Ramos', '💐', 'Rosas, girasoles, tulipanes y mixtos', 1),
    ('Arreglos Florales', '🏵️', 'Centros de mesa, cajas y bases decorativas', 2),
    ('Peluches', '🧸', 'Ositos, conejitos y personajes adorables', 3),
    ('Chocolates', '🍫', 'Bombones, trufas y cajas premium', 4),
    ('Combos', '🎁', 'La combinación perfecta de flores, peluches y chocolates', 5),
]

OCASIONES = ['Cumpleaños', 'Aniversario', 'Día de la Madre', 'San Valentín', 'Graduación', 'Nacimiento', 'Condolencias']

PRODUCTOS_INICIALES = [
    {'nombre': 'Ramo de Rosas Rosadas', 'cat': 'Ramos', 'desc': '12 rosas rosadas premium con follaje verde y envoltura elegante',
     'precio_orig': 35990, 'precio_oferta': 28990, 'badge': 'MAS_VENDIDO', 'ocasiones': ['Día de la Madre', 'San Valentín', 'Aniversario']},
    {'nombre': 'Osito con Ramo de Flores', 'cat': 'Combos', 'desc': 'Peluche de 40cm + ramo de 6 rosas rojas + chocolate',
     'precio_orig': 45990, 'precio_oferta': 38990, 'badge': 'POPULAR', 'ocasiones': ['San Valentín', 'Aniversario']},
    {'nombre': 'Caja de Chocolates Premium', 'cat': 'Chocolates', 'desc': '24 bombones artesanales surtidos en caja elegante con moño',
     'precio_orig': 32990, 'precio_oferta': 26990, 'badge': 'PREMIUM', 'ocasiones': ['Cumpleaños', 'San Valentín']},
    {'nombre': 'Arreglo Floral Mixto', 'cat': 'Arreglos Florales', 'desc': 'Combinación de rosas, claveles, astromelias y follaje en base de cerámica',
     'precio_orig': 52990, 'precio_oferta': 42990, 'badge': 'NUEVO', 'ocasiones': ['Día de la Madre', 'Cumpleaños']},
    {'nombre': 'Girasoles Radiantes', 'cat': 'Ramos', 'desc': 'Ramo de 8 girasoles grandes con follaje verde y envoltura kraft',
     'precio_orig': 29990, 'precio_oferta': 24990, 'badge': 'NINGUNO', 'ocasiones': ['Cumpleaños', 'Graduación']},
    {'nombre': 'Combo Romántico Completo', 'cat': 'Combos', 'desc': '12 rosas rojas + osito 30cm + caja 12 chocolates + tarjeta personalizada',
     'precio_orig': 65990, 'precio_oferta': 52990, 'badge': 'COMBO', 'ocasiones': ['San Valentín', 'Aniversario']},
]

PRODUCTOS = PRODUCTOS_INICIALES + [
    # --- RAMOS ---
    {'nombre': 'Ramo de 12 Rosas Rojas', 'cat': 'Ramos', 'desc': 'Clásico y elegante, 12 rosas rojas de tallo largo con follaje premium.', 'precio_orig': 32990, 'precio_oferta': 27990, 'badge': 'MAS_VENDIDO', 'ocasiones': ['San Valentín', 'Aniversario']},
    {'nombre': 'Ramo de Girasoles Felices', 'cat': 'Ramos', 'desc': '8 girasoles grandes que iluminan cualquier día. Incluye envoltura kraft.', 'precio_orig': 28990, 'precio_oferta': 24990, 'badge': 'POPULAR', 'ocasiones': ['Cumpleaños', 'Graduación']},
    {'nombre': 'Ramo de Tulipanes Holandeses', 'cat': 'Ramos', 'desc': '10 tulipanes importados en colores surtidos. Elegancia pura.', 'precio_orig': 45990, 'precio_oferta': 39990, 'badge': 'PREMIUM', 'ocasiones': ['Día de la Madre', 'Aniversario']},
    {'nombre': 'Ramo Mixto Primaveral', 'cat': 'Ramos', 'desc': 'Combinación vibrante de gerberas, claveles y follaje verde.', 'precio_orig': 25990, 'precio_oferta': 21990, 'badge': 'OFERTA', 'ocasiones': ['Cumpleaños', 'Nacimiento']},

    # --- ARREGLOS FLORALES ---
    {'nombre': 'Centro de Mesa Elegante', 'cat': 'Arreglos Florales', 'desc': 'Arreglo bajo en base de vidrio con rosas, astromelias y velas.', 'precio_orig': 38990, 'precio_oferta': 34990, 'badge': 'NUEVO', 'ocasiones': ['Aniversario', 'Cumpleaños']},
    {'nombre': 'Caja de Rosas Eternas', 'cat': 'Arreglos Florales', 'desc': '6 rosas preservadas en caja de lujo. Duran más de un año.', 'precio_orig': 55990, 'precio_oferta': 49990, 'badge': 'PREMIUM', 'ocasiones': ['San Valentín', 'Día de la Madre']},
    {'nombre': 'Arreglo de Orquídeas Phalaenopsis', 'cat': 'Arreglos Florales', 'desc': 'Planta de orquídea blanca en maceta de cerámica moderna.', 'precio_orig': 42990, 'precio_oferta': 37990, 'badge': 'NINGUNO', 'ocasiones': ['Condolencias', 'Cumpleaños']},

    # --- PELUCHES ---
    {'nombre': 'Osito Gigante 1 Metro', 'cat': 'Peluches', 'desc': 'Peluche de oso marrón extra suave de 100cm de alto.', 'precio_orig': 35990, 'precio_oferta': 29990, 'badge': 'POPULAR', 'ocasiones': ['San Valentín', 'Cumpleaños']},
    {'nombre': 'Conejito de Peluche con Corazón', 'cat': 'Peluches', 'desc': 'Adorable conejo blanco de 40cm sosteniendo un corazón rojo.', 'precio_orig': 18990, 'precio_oferta': 15990, 'badge': 'OFERTA', 'ocasiones': ['San Valentín', 'Nacimiento']},
    {'nombre': 'Osito con Rosa Eterna', 'cat': 'Peluches', 'desc': 'Osito de 30cm que sostiene una rosa roja preservada en cúpula.', 'precio_orig': 25990, 'precio_oferta': 22990, 'badge': 'MAS_VENDIDO', 'ocasiones': ['Aniversario', 'San Valentín']},
    {'nombre': 'Unicornio Mágico de Peluche', 'cat': 'Peluches', 'desc': 'Peluche de unicornio multicolor de 50cm, súper suave.', 'precio_orig': 22990, 'precio_oferta': 19990, 'badge': 'NUEVO', 'ocasiones': ['Cumpleaños', 'Nacimiento']},

    # --- CHOCOLATES ---
    {'nombre': 'Caja de Bombones Surtidos 24u', 'cat': 'Chocolates', 'desc': 'Selección de 24 bombones de chocolate belga con rellenos variados.', 'precio_orig': 28990, 'precio_oferta': 24990, 'badge': 'PREMIUM', 'ocasiones': ['San Valentín', 'Aniversario']},
    {'nombre': 'Caja Corazón Ferrero Rocher', 'cat': 'Chocolates', 'desc': 'Caja en forma de corazón con 18 chocolates Ferrero Rocher.', 'precio_orig': 32990, 'precio_oferta': 28990, 'badge': 'MAS_VENDIDO', 'ocasiones': ['San Valentín', 'Día de la Madre']},
    {'nombre': 'Tableta de Chocolate Artesanal', 'cat': 'Chocolates', 'desc': 'Tableta de chocolate 70% cacao con frutos secos y flores comestibles.', 'precio_orig': 12990, 'precio_oferta': 9990, 'badge': 'NUEVO', 'ocasiones': ['Cumpleaños', 'Graduación']},
    {'nombre': 'Trufas Belgas Premium (12u)', 'cat': 'Chocolates', 'desc': 'Caja de 12 trufas artesanales de chocolate oscuro y blanco.', 'precio_orig': 18990, 'precio_oferta': 15990, 'badge': 'NINGUNO', 'ocasiones': ['Aniversario', 'Cumpleaños']},

    # --- COMBOS ---
    {'nombre': 'Combo Amor Eterno', 'cat': 'Combos', 'desc': '12 Rosas Rojas + Osito 30cm + Caja 12 Bombones + Tarjeta.', 'precio_orig': 65990, 'precio_oferta': 54990, 'badge': 'MAS_VENDIDO', 'ocasiones': ['San Valentín', 'Aniversario']},
    {'nombre': 'Combo Cumpleaños Feliz', 'cat': 'Combos', 'desc': 'Ramo de Girasoles + Peluche a elección + Globo Metálico.', 'precio_orig': 48990, 'precio_oferta': 42990, 'badge': 'POPULAR', 'ocasiones': ['Cumpleaños', 'Graduación']},
    {'nombre': 'Combo Deluxe Premium', 'cat': 'Combos', 'desc': 'Caja de Rosas Eternas + Trufas Belgas + Vino Espumante.', 'precio_orig': 85990, 'precio_oferta': 74990, 'badge': 'PREMIUM', 'ocasiones': ['Aniversario', 'Día de la Madre']},
    {'nombre': 'Combo Bienvenida Bebé', 'cat': 'Combos', 'desc': 'Ramo Mixto Pastel + Conejito de Peluche + Chocolates blancos.', 'precio_orig': 45990, 'precio_oferta': 39990, 'badge': 'NUEVO', 'ocasiones': ['Nacimiento', 'Cumpleaños']},
]
