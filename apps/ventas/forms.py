import json
import re
from datetime import date

from django import forms

from .models import Pedido


class CheckoutForm(forms.ModelForm):
    """Datos de entrega. Los productos llegan en `items` (JSON) desde el carrito del navegador;
    los precios NUNCA se toman del navegador: se recalculan en el servidor."""
    items = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Pedido
        fields = [
            'nombre_cliente', 'email', 'telefono', 'direccion_entrega', 'comuna', 'ciudad',
            'instrucciones_entrega', 'destinatario', 'mensaje_tarjeta', 'metodo_pago',
            'fecha_entrega_deseada', 'hora_entrega_deseada',
        ]
        widgets = {
            'fecha_entrega_deseada': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_entrega_deseada': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'instrucciones_entrega': forms.Textarea(attrs={'rows': 2}),
            'mensaje_tarjeta': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'nombre_cliente': 'Nombre de quien compra', 'telefono': 'Teléfono de contacto',
            'direccion_entrega': 'Dirección de entrega', 'instrucciones_entrega': 'Instrucciones de entrega',
            'destinatario': 'Nombre del destinatario', 'mensaje_tarjeta': 'Mensaje para la tarjeta',
            'metodo_pago': 'Método de pago', 'fecha_entrega_deseada': 'Fecha de entrega',
            'hora_entrega_deseada': 'Hora de entrega (opcional)',
        }

    def clean_telefono(self):
        tel = self.cleaned_data['telefono'].strip()
        if not re.fullmatch(r'[+\d][\d\s-]{6,19}', tel):
            raise forms.ValidationError('Ingresa un teléfono válido, por ejemplo +56 9 1234 5678.')
        return tel

    def clean_fecha_entrega_deseada(self):
        fecha = self.cleaned_data['fecha_entrega_deseada']
        if fecha < date.today():
            raise forms.ValidationError('La fecha de entrega no puede ser anterior a hoy.')
        return fecha

    def clean_items(self):
        """Devuelve {producto_id: cantidad} validado."""
        try:
            data = json.loads(self.cleaned_data['items'] or '[]')
        except (TypeError, ValueError):
            raise forms.ValidationError('El carrito no es válido.')
        if not isinstance(data, list) or not data or len(data) > 50:
            raise forms.ValidationError('Tu carrito está vacío.')
        resultado = {}
        for it in data:
            try:
                pid, cant = int(it['id']), int(it['quantity'])
            except (TypeError, ValueError, KeyError):
                raise forms.ValidationError('El carrito contiene datos inválidos.')
            if cant < 1 or cant > 99:
                raise forms.ValidationError('Cantidad inválida en el carrito.')
            resultado[pid] = resultado.get(pid, 0) + cant
        return resultado
