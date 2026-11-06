"""
Estimación de costos del proyecto (Evaluación 2 - Backend).

⚠ Los valores son SUPUESTOS DEL EQUIPO (referenciales). Para la presentación, reemplaza
las horas y tarifas por las reales de tu grupo: la página /reportes/costos/ se recalcula sola.
Moneda: CLP. Tipo de cambio referencial para servicios en USD: TIPO_CAMBIO.
"""
from decimal import Decimal

TIPO_CAMBIO = Decimal('950')  # CLP por USD (supuesto)

# Valor hora (CLP) por rol — referencia de mercado para perfil junior/analista programador.
TARIFAS = {
    'Analista / Documentación': Decimal('8000'),
    'Desarrollo Backend': Decimal('10000'),
    'Desarrollo Frontend': Decimal('9000'),
    'QA / Pruebas': Decimal('8000'),
}

# (tarea, rol, horas CON asistencia de IA, horas estimadas SIN IA)
TAREAS = [
    ('Levantamiento de requisitos y co-creación con las clientas', 'Analista / Documentación', 24, 26),
    ('Diseño UML 4+1 y modelo de datos', 'Analista / Documentación', 30, 33),
    ('Diseño de interfaz y prototipo', 'Desarrollo Frontend', 16, 18),
    ('Modelos Django, migraciones y conexión a Supabase', 'Desarrollo Backend', 24, 36),
    ('CRUD de productos, categorías e inventario', 'Desarrollo Backend', 36, 54),
    ('Autenticación, sesiones y control de acceso', 'Desarrollo Backend', 14, 22),
    ('Carrito, checkout y gestión de pedidos', 'Desarrollo Backend', 28, 42),
    ('Reportes y dashboard (agregaciones ORM)', 'Desarrollo Backend', 20, 30),
    ('Plantillas, estilos y navegación responsive', 'Desarrollo Frontend', 40, 56),
    ('Pruebas y depuración', 'QA / Pruebas', 24, 31),
    ('Despliegue en la nube y configuración de producción', 'Desarrollo Backend', 10, 14),
    ('Documentación y preparación de la presentación', 'Analista / Documentación', 14, 15),
]

# (servicio, costo mensual USD usado, costo mensual USD proyectado a producción, nota)
INFRAESTRUCTURA = [
    ('Hosting aplicación Django (Render)', Decimal('0'), Decimal('7'), 'Plan Free para la evaluación; Starter al escalar'),
    ('Base de datos PostgreSQL (Supabase)', Decimal('0'), Decimal('25'), 'Plan Free ahora; Pro en producción'),
    ('Repositorio y CI (GitHub)', Decimal('0'), Decimal('0'), 'Plan gratuito'),
    ('Frontend estático (GitHub Pages)', Decimal('0'), Decimal('0'), 'Plan gratuito'),
]
DOMINIO_ANUAL_CLP = Decimal('10000')   # dominio .cl (valor referencial anual)
MESES_PROYECCION = 12
MESES_DESARROLLO = 2

# (herramienta, costo mensual USD, meses)
HERRAMIENTAS_IA = [
    ('Asistente de IA para código (suscripción Pro)', Decimal('20'), MESES_DESARROLLO),
    ('GitHub Copilot (plan gratuito para estudiantes)', Decimal('0'), MESES_DESARROLLO),
]


def calcular():
    filas = []
    por_rol = {}
    for tarea, rol, h_ia, h_sin in TAREAS:
        tarifa = TARIFAS[rol]
        filas.append({'tarea': tarea, 'rol': rol, 'tarifa': tarifa, 'h_ia': h_ia, 'h_sin': h_sin,
                      'costo_ia': tarifa * h_ia, 'costo_sin': tarifa * h_sin})
        r = por_rol.setdefault(rol, {'rol': rol, 'tarifa': tarifa, 'horas': 0, 'costo': Decimal('0')})
        r['horas'] += h_ia
        r['costo'] += tarifa * h_ia

    horas_ia = sum(f['h_ia'] for f in filas)
    horas_sin = sum(f['h_sin'] for f in filas)
    costo_hh_ia = sum((f['costo_ia'] for f in filas), Decimal('0'))
    costo_hh_sin = sum((f['costo_sin'] for f in filas), Decimal('0'))

    infra = []
    for nombre, usado, proyectado, nota in INFRAESTRUCTURA:
        infra.append({'servicio': nombre, 'usd_mes_usado': usado, 'usd_mes_proy': proyectado,
                      'clp_usado': usado * TIPO_CAMBIO * MESES_DESARROLLO,
                      'clp_proyectado': proyectado * TIPO_CAMBIO * MESES_PROYECCION, 'nota': nota})
    infra_usada = sum((i['clp_usado'] for i in infra), Decimal('0'))
    infra_proy = sum((i['clp_proyectado'] for i in infra), Decimal('0')) + DOMINIO_ANUAL_CLP

    ia = [{'herramienta': n, 'usd_mes': c, 'meses': m, 'clp': c * m * TIPO_CAMBIO} for n, c, m in HERRAMIENTAS_IA]
    costo_ia = sum((x['clp'] for x in ia), Decimal('0'))

    total_con_ia = costo_hh_ia + infra_usada + costo_ia
    total_sin_ia = costo_hh_sin + infra_usada
    ahorro = total_sin_ia - total_con_ia

    return {
        'filas': filas, 'por_rol': list(por_rol.values()),
        'horas_ia': horas_ia, 'horas_sin': horas_sin, 'horas_ahorradas': horas_sin - horas_ia,
        'pct_horas': round((horas_sin - horas_ia) / horas_sin * 100, 1) if horas_sin else 0,
        'costo_hh_ia': costo_hh_ia, 'costo_hh_sin': costo_hh_sin,
        'infra': infra, 'infra_usada': infra_usada, 'infra_proy': infra_proy, 'dominio': DOMINIO_ANUAL_CLP,
        'ia': ia, 'costo_ia': costo_ia,
        'total_con_ia': total_con_ia, 'total_sin_ia': total_sin_ia, 'ahorro': ahorro,
        'pct_ahorro': round(ahorro / total_sin_ia * 100, 1) if total_sin_ia else 0,
        'tipo_cambio': TIPO_CAMBIO, 'meses_desarrollo': MESES_DESARROLLO, 'meses_proyeccion': MESES_PROYECCION,
        'costo_mensual_prod': round(infra_proy / MESES_PROYECCION),
    }
