import requests
import base64
import pandas as pd
from datetime import datetime
import sys

# ============================================================================
#  CONFIGURACIÓN: CREDENCIALES DE WALMART CHILE
# ============================================================================
CLIENT_ID = "208a15ba-f194-47ca-b2d1-44e0ae12195c"
CLIENT_SECRET = "AJt8F1RdxrsA1SLssnBR8A-2OtJoPMUuJjAy41OItsa6YnTIfc_WSll0Q1OycZKEF2NOHVyKehNWrZVHwIKQVJ0"
WALMART_API_URL = "https://marketplace.walmartapis.com"
WM_MARKET = "cl"  # Para Chile

# ============================================================================
#  1) FUNCIÓN PARA OBTENER TOKEN
# ============================================================================
def obtener_token():
    """
    Llama a POST /v3/token con las credenciales en Basic Auth.
    Devuelve el 'access_token' si todo va bien.
    """
    url = f"{WALMART_API_URL}/v3/token"

    # Prepara el 'Authorization: Basic <Base64(clientId:clientSecret)>'
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "WM_MARKET": WM_MARKET,
        "WM_QOS.CORRELATION_ID": "GetTokenPy",
        "WM_SVC.NAME": "WalmartAPI",
        "WM_CONSUMER.CHANNEL.TYPE": "PYTHON_SCRIPT"
    }

    data = {"grant_type": "client_credentials"}

    resp = requests.post(url, headers=headers, data=data)

    if resp.status_code == 200:
        token_json = resp.json()
        if "access_token" in token_json:
            return token_json["access_token"]
        else:
            print("❌ Respuesta de token inesperada. Falta 'access_token'.")
            print(resp.text)
            sys.exit(1)
    else:
        print(f"❌ Error al obtener token. Status: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

# ============================================================================
#  2) FUNCIÓN PARA OBTENER ÓRDENES USANDO /v3/orders/cursor
# ============================================================================
def obtener_ordenes(access_token):
    """
    Usa GET /v3/orders/cursor para traer TODAS las órdenes de los últimos 180 días.
    - Requiere los encabezados:
      Authorization: Basic <Base64(clientId:clientSecret)>
      WM_SEC.ACCESS_TOKEN: <access_token>
    - Implementa paginación con 'cursorMark'.
    - Si no hay órdenes, Walmart responde 404 "Order not found".
    """
    base_url = f"{WALMART_API_URL}/v3/orders/cursor"
    todas_las_ordenes = []
    cursor_mark = "*"
    limit = 50  # Máximo 100

    # De nuevo, preparar Basic Auth
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    while True:
        params = {
            "limit": limit,
            "cursorMark": cursor_mark
        }

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "WM_SEC.ACCESS_TOKEN": access_token,
            "WM_MARKET": WM_MARKET,
            "WM_QOS.CORRELATION_ID": "GetOrdersPy",
            "WM_SVC.NAME": "WalmartAPI",
            "WM_CONSUMER.CHANNEL.TYPE": "PYTHON_SCRIPT",
            "Accept": "application/json"
        }

        resp = requests.get(base_url, headers=headers, params=params)

        # Si la API no encuentra órdenes, envía 404 "Order not found"
        if resp.status_code == 404:
            raise ValueError(f"❌ 404 - Order not found\n{resp.text}")

        # Si es otro error 4xx/5xx
        resp.raise_for_status()

        # Parseamos el JSON
        data = resp.json()

        # La respuesta puede traer las órdenes en "payload" -> "orders", o en "order"
        lista_ordenes = []
        next_cursor = None

        # Formato nuevo
        if "payload" in data and "orders" in data["payload"]:
            lista_ordenes = data["payload"]["orders"]
            next_cursor = data["payload"].get("nextCursorMark")

        # Formato 'legacy'
        elif "order" in data and isinstance(data["order"], list):
            lista_ordenes = data["order"]
            if "meta" in data and "nextCursorMark" in data["meta"]:
                next_cursor = data["meta"]["nextCursorMark"]

        todas_las_ordenes.extend(lista_ordenes)

        # Revisar si hay otra página
        if not next_cursor or next_cursor == "-1":
            break  # No hay más

        cursor_mark = next_cursor

    return todas_las_ordenes

# ============================================================================
#  FUNCIÓN MAIN
# ============================================================================
def main():
    print("=== 1) SOLICITANDO TOKEN DE WALMART CHILE ===")
    token = obtener_token()
    print(f"✅ Token obtenido: {token[:25]}...")

    print("\n=== 2) DESCARGANDO ÓRDENES (HASTA 180 DÍAS) ===")
    try:
        ordenes = obtener_ordenes(token)
        print(f"✅ Órdenes descargadas: {len(ordenes)}")

        if ordenes:
            # Guardamos en Excel
            df = pd.json_normalize(ordenes, sep="_")
            nombre_archivo = f"Walmart_Ordenes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(nombre_archivo, index=False)
            print(f"✅ Archivo generado: {nombre_archivo}")
        else:
            print("⚠️ No se encontraron órdenes (lista vacía).")
    except ValueError as ve:
        # Caso específico: 404 'Order not found'
        print(str(ve))
        print("⚠️ Esto significa que la API no encontró pedidos. " 
              "Podría ser que no haya ventas o que la cuenta no esté habilitada.")
    except Exception as e:
        print(f"❌ Error general: {e}")

# ============================================================================
#  EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    main()
