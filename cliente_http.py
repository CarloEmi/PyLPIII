import json
import urllib.request

# URL base de la API externa (JSONPlaceholder es un servicio para pruebas de APIs REST)
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# Función para realizar una petición HTTP GET
def ejecutar_peticion_get():
    print("=== 1. Ejecutando Petición GET ===")
    
    # 1. Creamos la solicitud HTTP especificando la URL y un encabezado (Header) personalizado
    req = urllib.request.Request(BASE_URL, headers={"User-Agent": "PyLPIII-UCP/2026"})
    
    # 2. Abrimos la conexión al servidor y enviamos la petición
    with urllib.request.urlopen(req) as response:
        # Obtener el código de estado HTTP de la respuesta (ej. 200 OK)
        status_code = response.getcode()
        
        # Leer el contenido binario de la respuesta, decodificarlo a texto UTF-8 
        # y convertir el texto JSON en estructuras nativas de Python (diccionario/lista)
        data = json.loads(response.read().decode('utf-8'))
        
        # Mostrar el código de estado y el título del primer post obtenido
        print(f"Status Code: {status_code}")
        print(f"Primer registro recibido: {data[0]['title']}
")

# Función para realizar una petición HTTP POST (Crear nuevo recurso)
def ejecutar_peticion_post():
    print("=== 2. Ejecutando Petición POST ===")
    
    # 1. Definimos los datos (payload) que enviaremos al servidor en formato de diccionario
    payload = {
        "title": "Proyecto Integrador PyLP III",
        "body": "API RESTful concurrente y asíncrona",
        "userId": 1
    }
    
    # 2. Convertimos el diccionario a una cadena JSON (codificada en bytes UTF-8)
    encoded_data = json.dumps(payload).encode('utf-8')
    
    # 3. Configuramos la solicitud indicando la URL, los datos codificados,
    # los encabezados necesarios (indicando que es JSON) y el método POST
    req = urllib.request.Request(
        BASE_URL,
        data=encoded_data,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        method="POST"
    )
    
    # 4. Enviamos la petición POST y recibimos la respuesta del servidor
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        
        # Decodificamos y convertimos la respuesta JSON recibida
        data = json.loads(response.read().decode('utf-8'))
        
        # Mostramos los resultados (el código de estado esperado es 201 Created)
        print(f"Status Code: {status_code} (Created)")
        print(f"Respuesta del servidor: {data}
")

# Bloque de ejecución principal del script
if __name__ == "__main__":
    ejecutar_peticion_get()   # Ejecuta la consulta (GET)
    ejecutar_peticion_post()  # Ejecuta la creación (POST)
