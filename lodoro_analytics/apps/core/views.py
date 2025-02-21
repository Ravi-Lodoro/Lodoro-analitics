import os
import json
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from .forms import SimpleForm
from .services.ripley_api import get_store_info, get_orders, get_offers, process_store_info
from .models import Submission

# Definir la ruta del archivo donde se guardarán los datos de Ripley
RIPLEY_DATA_FILE = os.path.join(settings.BASE_DIR, "ripley_data.json")

def update_ripley_data():
    """
    Llama a las APIs de Ripley, procesa la información y la guarda en un archivo JSON.
    Retorna el diccionario con la información actualizada.
    """
    # Llamadas a la API
    store_data = get_store_info()
    orders_data = get_orders()
    offers_data = get_offers()
    
    # Procesar la información básica de la tienda
    store_info = process_store_info(store_data)
    
    # Estructurar los datos a guardar
    data = {
        "store_info": store_info,
        "orders_data": orders_data,
        "offers_data": offers_data,
        "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    
    # Guardar la información en un archivo JSON
    with open(RIPLEY_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return data

def ripley_view(request):
    # Llama a las funciones de la API
    store_data = get_store_info()
    orders_data = get_orders()
    offers_data = get_offers()

    # Procesa la información básica de la tienda
    store_info = process_store_info(store_data)

    # Pasa todo al template
    context = {
        'store_info': store_info,   # Diccionario con info de la tienda
        'orders_data': orders_data, # Diccionario o lista con las órdenes
        'offers_data': offers_data, # Diccionario o lista con las ofertas
    }
    return render(request, 'ripley_page.html', context)


def form_view(request):
    """
    Vista para el formulario que guarda la información en la base de datos.
    Se muestra un listado de todas las entradas guardadas ordenadas de la más reciente a la más antigua.
    """
    if request.method == 'POST':
        form = SimpleForm(request.POST)
        if form.is_valid():
            # Guarda la información en la base de datos
            Submission.objects.create(
                nombre=form.cleaned_data['nombre'],
                rut=form.cleaned_data['rut']
            )
            # Reinicia el formulario (vacío)
            form = SimpleForm()
    else:
        form = SimpleForm()
    
    # Recupera todas las entradas guardadas, ordenadas de más reciente a más antigua
    submissions = Submission.objects.all().order_by('-submitted_at')
    
    return render(request, 'form_page.html', {
        'form': form,
        'submissions': submissions,
    })
