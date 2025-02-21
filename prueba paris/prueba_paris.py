import requests
import pandas as pd
import time

# ------------------------------------------------------------------
# CONFIGURACIONES GLOBALES
# ------------------------------------------------------------------
API_KEY = "2cbb7f4b-a7ee-48e2-88b5-a4c9a82c8399"  # Reemplázala con la correcta
BASE_URL = "https://api-developers.ecomm-stg.cencosud.com"

LIMIT = 100  # Número de registros por llamada
EXCEL_PRODUCTOS = "productos.xlsx"
EXCEL_ORDENES = "ordenes.xlsx"
SELLER_ID = "1f87cae1-9f72-45ff-9a09-cfb708c65861"  # Ajusta si es necesario

# ------------------------------------------------------------------
# 1) AUTENTICACIÓN PARA OBTENER EL ACCESS TOKEN
# ------------------------------------------------------------------
def obtener_access_token(api_key):
    url = f"{BASE_URL}/v1/auth/apiKey"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("accessToken")
    else:
        print(f"❌ Error en autenticación: {resp.status_code} - {resp.text}")
        return None

# ------------------------------------------------------------------
# 2) OBTENER TODOS LOS PRODUCTOS
# ------------------------------------------------------------------
def get_all_products(access_token):
    url = f"{BASE_URL}/v2/products/search"
    offset = 0
    todos_productos = []

    while True:
        params = {
            "limit": LIMIT,
            "offset": offset,
            "sellerId": SELLER_ID  # Filtrar por vendedor si es necesario
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        print(f"\n🔍 Llamando: {url}?limit={LIMIT}&offset={offset}&sellerId={SELLER_ID}")
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code == 200:
            data = resp.json()
            productos = data.get("results", [])
            total = data.get("total", 0)  # Intentar leer total desde API

            print(f"📌 Respuesta API (total en API: {total}) - Productos recibidos: {len(productos)}")

            if not productos:
                print("✅ No hay más productos. Descarga completada.")
                break  # Salimos cuando la API ya no devuelve más productos

            todos_productos.extend(productos)
            offset += LIMIT

            print(f"📥 Total productos descargados hasta ahora: {len(todos_productos)}")
            time.sleep(1)  # Pausa para evitar bloqueos

        else:
            print(f"❌ Error al obtener productos: {resp.status_code} - {resp.text}")
            break

    print(f"✅ Descarga finalizada: {len(todos_productos)} productos obtenidos.")
    return todos_productos

# ------------------------------------------------------------------
# 3) OBTENER TODAS LAS ÓRDENES
# ------------------------------------------------------------------
def get_all_orders(access_token):
    url = f"{BASE_URL}/v1/orders/simple"
    offset = 0
    todas_ordenes = []

    while True:
        params = {"limit": LIMIT, "offset": offset}
        headers = {"Authorization": f"Bearer {access_token}"}

        print(f"\n🔍 Llamando: {url}?limit={LIMIT}&offset={offset}")
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code == 200:
            data = resp.json()
            ordenes = data.get("data", [])
            total_count = data.get("count", 0)

            print(f"📌 Respuesta API (total en API: {total_count}) - Órdenes recibidas: {len(ordenes)}")

            if not ordenes:
                print("✅ No hay más órdenes. Descarga completada.")
                break

            todas_ordenes.extend(ordenes)
            offset += LIMIT

            print(f"📥 Total órdenes descargadas hasta ahora: {len(todas_ordenes)}")
            time.sleep(1)

        else:
            print(f"❌ Error al obtener órdenes: {resp.status_code} - {resp.text}")
            break

    print(f"✅ Descarga finalizada: {len(todas_ordenes)} órdenes obtenidas.")
    return todas_ordenes

# ------------------------------------------------------------------
# 4) EXPORTAR PRODUCTOS A EXCEL
# ------------------------------------------------------------------
def exportar_productos_a_excel(productos):
    df = pd.DataFrame(productos)
    df.to_excel(EXCEL_PRODUCTOS, index=False)
    print(f"\n📂 Productos exportados a {EXCEL_PRODUCTOS} (total: {len(df)})")

# ------------------------------------------------------------------
# 5) EXPORTAR ÓRDENES A EXCEL
# ------------------------------------------------------------------
def exportar_ordenes_a_excel(ordenes):
    df = pd.DataFrame(ordenes)
    df.to_excel(EXCEL_ORDENES, index=False)
    print(f"\n📂 Órdenes exportadas a {EXCEL_ORDENES} (total: {len(df)})")

# ------------------------------------------------------------------
# MAIN: FLUJO PRINCIPAL
# ------------------------------------------------------------------
def main():
    print("=== AUTENTICACIÓN ===")
    token = obtener_access_token(API_KEY)
    if not token:
        print("❌ Error: No se pudo obtener el token.")
        return

    print("\n=== DESCARGANDO PRODUCTOS ===")
    productos = get_all_products(token)
    exportar_productos_a_excel(productos)

    print("\n=== DESCARGANDO ÓRDENES ===")
    ordenes = get_all_orders(token)
    exportar_ordenes_a_excel(ordenes)

    print("\n✅ Proceso completado.")

if __name__ == "__main__":
    main()
