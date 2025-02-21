import requests
import pandas as pd

# Configuración de API y endpoints
STORE_API_URL = "https://ripley-prod.mirakl.net/api/account"
ORDERS_API_URL = "https://ripley-prod.mirakl.net/api/orders?paginate=false"
OFFERS_API_URL = "https://ripley-prod.mirakl.net/api/offers?paginate=false"

# Reemplaza este valor por tu API key real
API_KEY = "5fa9e6ae-509d-4ae7-85b1-0bff2eff4943"

HEADERS = {
    "Accept": "application/json",
    "Authorization": API_KEY
}

def get_store_info():
    try:
        response = requests.get(STORE_API_URL, headers=HEADERS)
        print("Store API - HTTP status code:", response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error al obtener la información de la tienda.")
            return None
    except Exception as e:
        print("Excepción en get_store_info:", e)
        return None

def get_orders():
    try:
        response = requests.get(ORDERS_API_URL, headers=HEADERS)
        print("Orders API - HTTP status code:", response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error al obtener las órdenes.")
            return None
    except Exception as e:
        print("Excepción en get_orders:", e)
        return None

def get_offers():
    try:
        response = requests.get(OFFERS_API_URL, headers=HEADERS)
        print("Offers API - HTTP status code:", response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error al obtener las ofertas.")
            return None
    except Exception as e:
        print("Excepción en get_offers:", e)
        return None

def process_store_info(data):
    """Organiza la información de la tienda en un diccionario plano."""
    if not data:
        return {}
    
    contact = data.get('contact_informations', {})
    billing = data.get('billing_info', {})
    payment_details = data.get('payment_details', {})
    
    info = {
        "Nombre Tienda": data.get('shop_name', 'N/A'),
        "Estado": data.get('shop_state', 'N/A'),
        "Modelo": data.get('model', 'N/A'),
        "Fecha Creación": data.get('date_created', 'N/A'),
        "Última Actualización": data.get('last_updated_date', 'N/A'),
        "Órdenes": data.get('orders_count', 'N/A'),
        "Ofertas": data.get('offers_count', 'N/A'),
        "Contacto - Nombre": f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
        "Contacto - Email": contact.get('email', 'N/A'),
        "Contacto - Teléfono": contact.get('phone', 'N/A'),
        "Dirección - Calle": contact.get('street1', 'N/A'),
        "Dirección - Ciudad": contact.get('city', 'N/A'),
        "Dirección - Región": contact.get('state', 'N/A'),
        "Dirección - Código Postal": contact.get('zip_code', 'N/A'),
        "Dirección - País": contact.get('country', 'N/A'),
        "Banco": billing.get('bank_name', 'N/A'),
        "IBAN": billing.get('iban', 'N/A'),
        "BIC": billing.get('bic', 'N/A'),
        "Titular Facturación": billing.get('owner', 'N/A'),
        "Saldo Pagado": payment_details.get('paid_balance', 'N/A'),
        "Saldo a Pagar": payment_details.get('payable_balance', 'N/A'),
        "Saldo Pendiente": payment_details.get('pending_balance', 'N/A'),
        "Política Devoluciones": data.get('return_policy', 'N/A'),
        "Descripción": data.get('description', 'N/A')
    }
    
    return info

def export_to_excel(store, orders, offers, filename="ripley_data.xlsx"):
    """
    Exporta la información a un archivo Excel con tres hojas:
    - "Store Info": Información de la tienda
    - "Orders": Lista de órdenes
    - "Offers": Lista de ofertas
    """
    writer = pd.ExcelWriter(filename, engine="openpyxl")
    
    # Store info: convertir el diccionario a DataFrame de una sola fila
    if store:
        df_store = pd.DataFrame([store])
        df_store.to_excel(writer, sheet_name="Store Info", index=False)
    
    # Orders: se asume que la respuesta contiene una lista o un dict con la clave 'orders'
    if orders:
        if isinstance(orders, dict) and 'orders' in orders:
            df_orders = pd.DataFrame(orders['orders'])
        elif isinstance(orders, list):
            df_orders = pd.DataFrame(orders)
        else:
            df_orders = pd.DataFrame([orders])
        df_orders.to_excel(writer, sheet_name="Orders", index=False)
    
    # Offers: similar procesamiento para las ofertas
    if offers:
        if isinstance(offers, dict) and 'offers' in offers:
            df_offers = pd.DataFrame(offers['offers'])
        elif isinstance(offers, list):
            df_offers = pd.DataFrame(offers)
        else:
            df_offers = pd.DataFrame([offers])
        df_offers.to_excel(writer, sheet_name="Offers", index=False)
    
    writer.close()
    print(f"Datos exportados a {filename}")

if __name__ == '__main__':
    store_data = get_store_info()
    orders_data = get_orders()
    offers_data = get_offers()
    
    store_info = process_store_info(store_data)
    
    export_to_excel(store_info, orders_data, offers_data)
