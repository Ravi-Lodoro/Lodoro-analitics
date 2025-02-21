import requests
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime, timezone

# Endpoint según la documentación (ambiente productivo)
API_ENDPOINT = "https://sellercenter-api.falabella.com"

def canonical_query_string_custom(params, order):
    """
    Construye la cadena canónica usando el orden especificado en la lista 'order'.
    Para cada clave en 'order' que esté en params, se añade "clave=valor" en ese orden.
    Luego se añaden, en orden alfabético, las claves restantes (si las hubiera).
    """
    result = []
    for key in order:
        if key in params:
            result.append(f"{key}={params[key]}")
    remaining_keys = sorted(set(params.keys()) - set(order))
    for key in remaining_keys:
        result.append(f"{key}={params[key]}")
    return "&".join(result)

def generate_signature_custom(params, api_key, order):
    """
    Genera la firma HMAC-SHA256 (Base64) usando la cadena a firmar construida
    con los parámetros en el orden especificado.

    La cadena a firmar se forma de la siguiente manera:
      HTTP_METHOD + "\n" +
      HOST + "\n" +
      REQUEST_PATH + "\n" +
      CANONICAL_QUERY_STRING

    Donde:
      - HTTP_METHOD es "GET"
      - HOST es "sellercenter-api.falabella.com"
      - REQUEST_PATH es "/"  
      - CANONICAL_QUERY_STRING es la cadena resultante de canonical_query_string_custom.
    """
    canonical_query = canonical_query_string_custom(params, order)
    string_to_sign = "GET\nsellercenter-api.falabella.com\n/\n" + canonical_query
    print("=== String to sign (custom order) ===")
    print(string_to_sign)
    
    signature = hmac.new(api_key.encode('utf-8'),
                         string_to_sign.encode('utf-8'),
                         hashlib.sha256).digest()
    encoded_signature = base64.b64encode(signature).decode()
    print("=== Generated signature (custom order) ===")
    print(encoded_signature)
    return encoded_signature

def get_orders(user_id, api_key):
    """
    Consulta la acción 'GetOrders' de la API de Falabella Seller Center usando un orden
    personalizado para la cadena a firmar. Se muestran por pantalla todos los pasos para depurar.
    """
    # Definir los parámetros base obligatorios
    params = {
        'Action': 'GetOrders',
        'UserID': user_id,
        'Version': '1.0',
        'Format': 'JSON',
        'Timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'SignatureMethod': 'HMAC-SHA256',
        'SignatureVersion': '2'
    }
    
    print("=== Base parameters ===")
    for k, v in params.items():
        print(f"{k}: {v}")
    
    # Definir el orden personalizado (ajústalo según la documentación)
    custom_order = ["Action", "UserID", "Version", "Format", "Timestamp", "SignatureMethod", "SignatureVersion"]
    
    # Generar la firma usando el orden personalizado
    signature = generate_signature_custom(params, api_key, custom_order)
    params['Signature'] = signature
    
    # Construir la URL final (aplicando percent-encoding a cada parámetro)
    encoded_params = "&".join(
        f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}"
        for k, v in params.items()
    )
    final_url = f"{API_ENDPOINT}/?{encoded_params}"
    print("\n=== Final URL ===")
    print(final_url)
    
    response = requests.get(final_url)
    print("\nHTTP status code:", response.status_code)
    print("Raw response text:", response.text)
    
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            print("Error decoding JSON:", e)
            return None
    else:
        return None

if __name__ == '__main__':
    # Reemplaza estos valores por tus credenciales reales
    USER_ID = "marketplace@lodoro.cl"
    API_KEY = "7777f26b867c60f3af759cc62714843e2ba2036c"  # Tu API Key/Secret
    
    data = get_orders(USER_ID, API_KEY)
    print("\n=== Respuesta Falabella Seller Center ===")
    print(data)
