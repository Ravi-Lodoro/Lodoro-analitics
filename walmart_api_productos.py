import requests
import base64
import pandas as pd

def get_token(main_url, client_id, client_secret):
    """
    Obtiene el token de autorización usando las credenciales del cliente.
    """
    url = main_url + '/v3/token'
    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()  # Aquí se usa base64
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'accept': 'application/json',
        'WM_MARKET': 'cl',
        'WM_QOS.CORRELATION_ID': 'Operaciones Walmart',
        'WM_SVC.NAME': 'Operaciones Walmart',
        'Content-Type': 'application/x-www-form-urlencoded',
        'WM_CONSUMER.CHANNEL.TYPE': 'Operaciones Walmart'
    }
    params = {'grant_type': 'client_credentials'}
    
    r = requests.post(url, headers=headers, data=params)
    token = r.json()['access_token']
    return token

def get_items(main_url, token):
    """
    Obtiene todos los productos, paginando a través de todas las páginas usando `nextCursor`.
    """
    products = []
    next_cursor = "*"  # Comienza con "*" para la primera página
    limit = 50  # Límite de productos por página

    while next_cursor:
        print(f"Obteniendo productos con cursor: {next_cursor}")
        url = main_url + '/v3/items'
        headers = {
            'accept': 'application/json',
            'WM_SEC.ACCESS_TOKEN': token,
            'WM_MARKET': 'cl',
            'WM_QOS.CORRELATION_ID': 'Operaciones Walmart',
            'WM_SVC.NAME': 'Operaciones Walmart',
            'WM_CONSUMER.CHANNEL.TYPE': 'Operaciones Walmart'
        }
        params = {'nextCursor': next_cursor, 'limit': limit}

        r = requests.get(url, headers=headers, params=params)

        if r.status_code == 200:
            data = r.json()
            items = data.get('ItemResponse', [])
            next_cursor = data.get('nextCursor', None)  # Obtiene el cursor para la siguiente página

            if not items:
                print("No se han encontrado más productos, deteniendo la búsqueda.")
                break  # Si no hay productos en la respuesta, terminamos el ciclo

            products.extend(items)
            print(f"Productos obtenidos: {len(items)} en esta página.")
            
        else:
            print(f"Error al obtener los productos: {r.status_code}")
            break

    print(f"Total de productos obtenidos: {len(products)}")
    return products

# Datos de configuración
main_url = "https://marketplace.walmartapis.com"
client_id = "208a15ba-f194-47ca-b2d1-44e0ae12195c"
client_secret = "AJt8F1RdxrsA1SLssnBR8A-2OtJoPMUuJjAy41OItsa6YnTIfc_WSll0Q1OycZKEF2NOHVyKehNWrZVHwIKQVJ0"

# Obtener el token
token = get_token(main_url, client_id, client_secret)

# Obtener todos los productos
products = get_items(main_url, token)

# Guardar los productos en un archivo Excel
df = pd.DataFrame(products)
df.to_excel('productos_walmart.xlsx', index=False)
print("Datos guardados en productos_walmart.xlsx")
