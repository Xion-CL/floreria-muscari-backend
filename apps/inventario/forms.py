from django import forms
from django.db import transaction

from apps.catalogo.models import Producto

from .models import MovimientoStock

SUMAN = {'ENTRADA', 'DEVOLUCION'}
RESTAN = {'SALIDA', 'MERMA'}


class MovimientoForm(forms.ModelForm):
    """Registra un movimiento. `cantidad` es siempre positiva:
    ENTRADA/DEVOLUCION suman, SALIDA/MERMA restan y AJUSTE fija el stock al valor indicado."""
    cantidad = forms.IntegerField(min_value=0, label='Cantidad',
                                  help_text='En "Ajuste manual" es el nuevo stock total del producto.')

    class Meta:
        model = MovimientoStock
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'referencia']
        widgets = {'motivo': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        cleaned = super().clean()
        producto, tipo, cant = cleaned.get('producto'), cleaned.get('tipo'), cleaned.get('cantidad')
        if producto and tipo and cant is not None:
            if tipo != 'AJUSTE' and cant < 1:
                self.add_error('cantidad', 'La cantidad debe ser al menos 1.')
            if tipo in RESTAN and cant > producto.stock:
                self.add_error('cantidad', f'No puedes restar {cant}: el stock actual es {producto.stock}.')
        return cleaned

    @transaction.atomic
    def save(self, usuario=None):
        mov = super().save(commit=False)
        producto = Producto.objects.select_for_update().get(pk=mov.producto_id)
        anterior = producto.stock
        cant = self.cleaned_data['cantidad']
        if mov.tipo in SUMAN:
            nuevo, delta = anterior + cant, cant
        elif mov.tipo in RESTAN:
            nuevo, delta = max(anterior - cant, 0), -cant
        else:
            nuevo, delta = cant, cant - anterior
        producto.stock = nuevo
        producto.save(update_fields=['stock', 'fecha_modificacion'])
        mov.cantidad, mov.stock_anterior, mov.stock_nuevo, mov.usuario = delta, anterior, nuevo, usuario
        mov.save()
        return mov
