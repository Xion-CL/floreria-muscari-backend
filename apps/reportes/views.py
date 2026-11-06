import csv
import json
from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.catalogo.models import Categoria, Producto, Resena
from apps.core.mixins import PanelAccessMixin
from apps.usuarios.models import Usuario
from apps.ventas.models import DetallePedido, Pedido

from . import costos


def _num(valor):
    """Decimal/None -> int, para poder serializar a JSON."""
    return int(valor or 0)


class DashboardView(PanelAccessMixin, TemplateView):
    """Dashboard de reportes: agregaciones del ORM (Count, Sum, Avg) sobre la florería."""
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        estados = dict(Pedido.ESTADO_CHOICES)
        validos = Pedido.objects.exclude(estado='CANCELADO')
        detalles = DetallePedido.objects.exclude(pedido__estado='CANCELADO')

        # --- KPIs de ventas -------------------------------------------------
        kpi = validos.aggregate(n=Count('id'), ingresos=Sum('total'), ticket=Avg('total'),
                                envios=Sum('costo_envio'))
        unidades = detalles.aggregate(u=Sum('cantidad'))['u'] or 0

        # --- Pedidos por estado --------------------------------------------
        por_estado = list(Pedido.objects.values('estado').annotate(n=Count('id')).order_by('-n'))
        for fila in por_estado:
            fila['etiqueta'] = estados.get(fila['estado'], fila['estado'])

        # --- Ingresos por mes ----------------------------------------------
        por_mes = list(validos.annotate(mes=TruncMonth('fecha_creacion'))
                       .values('mes').annotate(ingresos=Sum('total'), n=Count('id')).order_by('mes'))

        # --- Ventas por categoría y top productos -------------------------------
        por_categoria = list(detalles.values(cat=F('producto__categoria__nombre'))
                             .annotate(unidades=Sum('cantidad'), ingresos=Sum('subtotal')).order_by('-ingresos'))
        top_productos = list(detalles.values(prod=F('producto__nombre'))
                             .annotate(unidades=Sum('cantidad'), ingresos=Sum('subtotal')).order_by('-unidades')[:5])
        por_pago = list(validos.values('metodo_pago').annotate(n=Count('id'), total=Sum('total')).order_by('-total'))
        pagos = dict(Pedido.METODO_PAGO_CHOICES)
        for fila in por_pago:
            fila['etiqueta'] = pagos.get(fila['metodo_pago'], fila['metodo_pago'])

        # --- Inventario -------------------------------------------------------
        valor_stock = ExpressionWrapper(F('stock') * F('precio_original'),
                                        output_field=DecimalField(max_digits=14, decimal_places=0))
        inv = Producto.objects.aggregate(n=Count('id'), total_stock=Sum('stock'), valor=Sum(valor_stock),
                                         precio_prom=Avg('precio_original'))
        n_agotados = Producto.objects.filter(stock=0).count()
        stock_bajo = list(Producto.objects.filter(stock__lte=F('stock_minimo'))
                          .select_related('categoria').order_by('stock')[:8])
        por_cat_inv = list(Categoria.objects.annotate(n=Count('productos'), stock=Sum('productos__stock'),
                                                      precio_prom=Avg('productos__precio_original')).order_by('-n'))

        # --- Reseñas y clientes -----------------------------------------------
        res = Resena.objects.filter(aprobado=True).aggregate(n=Count('id'), prom=Avg('valoracion'))
        mejor_valorados = list(
            Producto.objects.annotate(
                prom=Avg('resenas__valoracion', filter=Q(resenas__aprobado=True)),
                n_res=Count('resenas', filter=Q(resenas__aprobado=True)))
            .filter(n_res__gt=0).order_by('-prom', '-n_res')[:5])
        top_clientes = list(Usuario.objects.annotate(n_pedidos=Count('pedidos'), gasto=Sum('pedidos__total'))
                            .filter(n_pedidos__gt=0).order_by('-gasto')[:5])

        ctx.update({
            'kpi_pedidos': kpi['n'] or 0, 'kpi_ingresos': _num(kpi['ingresos']), 'kpi_ticket': _num(kpi['ticket']),
            'kpi_unidades': unidades, 'kpi_envios': _num(kpi['envios']),
            'por_estado': por_estado, 'por_mes': por_mes, 'por_categoria': por_categoria,
            'top_productos': top_productos, 'por_pago': por_pago,
            'inv': inv, 'inv_valor': _num(inv['valor']), 'inv_precio_prom': _num(inv['precio_prom']),
            'n_agotados': n_agotados, 'stock_bajo': stock_bajo, 'por_cat_inv': por_cat_inv,
            'res_n': res['n'] or 0, 'res_prom': round(res['prom'] or 0, 2),
            'mejor_valorados': mejor_valorados, 'top_clientes': top_clientes,
            'total_usuarios': Usuario.objects.count(),
            'generado': timezone.localtime(),
            'chart_data': json.dumps({
                'mes': {'labels': [f['mes'].strftime('%m/%Y') for f in por_mes],
                        'ingresos': [_num(f['ingresos']) for f in por_mes]},
                'estado': {'labels': [f['etiqueta'] for f in por_estado], 'data': [f['n'] for f in por_estado]},
                'categoria': {'labels': [f['cat'] for f in por_categoria],
                              'data': [_num(f['ingresos']) for f in por_categoria]},
            }),
        })
        return ctx


class ExportarPedidosCSV(PanelAccessMixin, View):
    def get(self, request):
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="pedidos_muscari.csv"'
        resp.write('﻿')  # BOM para que Excel respete las tildes
        w = csv.writer(resp, delimiter=';')
        w.writerow(['ID', 'Fecha', 'Cliente', 'Email', 'Comuna', 'Estado', 'Pago', 'Subtotal', 'Envío', 'Total'])
        for p in Pedido.objects.all().order_by('-fecha_creacion').iterator():
            w.writerow([p.pk, timezone.localtime(p.fecha_creacion).strftime('%Y-%m-%d %H:%M'), p.nombre_cliente,
                        p.email, p.comuna, p.get_estado_display(), p.get_metodo_pago_display(),
                        p.subtotal, p.costo_envio, p.total])
        return resp


class CostosView(TemplateView):
    """Estimación de costos del proyecto y análisis del impacto de la IA (se expone en la presentación)."""
    template_name = 'reportes/costos.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['c'] = costos.calcular()
        return ctx
