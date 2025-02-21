import requests
import pandas as pd

STORE_API_URL = "https://ripley-prod.mirakl.net/api/account"
ORDERS_API_URL = "https://ripley-prod.mirakl.net/api/orders?paginate=false"
OFFERS_API_URL = "https://ripley-prod.mirakl.net/api/offers?paginate=false"

API_KEY = "5fa9e6ae-509d-4ae7-85b1-0bff2eff4943"  # tu API Key de ejemplo

HEADERS = {
    "Accept": "application/json",
    "Authorization": API_KEY
}

def get_store_info():
    try:
        response = requests.get(STORE_API_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print("Excepción en get_store_info:", e)
        return None

def get_orders():
    try:
        response = requests.get(ORDERS_API_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print("Excepción en get_orders:", e)
        return None

def get_offers():
    try:
        response = requests.get(OFFERS_API_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print("Excepción en get_offers:", e)
        return None

def process_store_info(data):
    if not data:
        return {}
    contact = data.get('contact_informations', {})
    billing = data.get('billing_info', {})
    payment_details = data.get('payment_details', {})
    
    info = {
        "Nombre Tienda": data.get('shop_name', 'N/A'),
        "Estado": data.get('shop_state', 'N/A'),
        "Fecha Creación": data.get('date_created', 'N/A'),
        "Órdenes": data.get('orders_count', 'N/A'),
        "Contacto - Email": contact.get('email', 'N/A'),
        "Banco": billing.get('bank_name', 'N/A'),
        "Saldo Pagado": payment_details.get('paid_balance', 'N/A'),
    }
    return info

def export_to_excel(store, orders, offers, filename="ripley_data.xlsx"):
    """Exporta la información a un archivo Excel con tres hojas."""
    writer = pd.ExcelWriter(filename, engine="openpyxl")
    if store:
        df_store = pd.DataFrame([store])
        df_store.to_excel(writer, sheet_name="Store Info", index=False)
    if orders:
        if isinstance(orders, dict) and 'orders' in orders:
            df_orders = pd.DataFrame(orders['orders'])
        else:
            df_orders = pd.DataFrame(orders)
        df_orders.to_excel(writer, sheet_name="Orders", index=False)
    if offers:
        if isinstance(offers, dict) and 'offers' in offers:
            df_offers = pd.DataFrame(offers['offers'])
        else:
            df_offers = pd.DataFrame(offers)
        df_offers.to_excel(writer, sheet_name="Offers", index=False)
    writer.close()
    print(f"Datos exportados a {filename}")
