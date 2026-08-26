from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

# Simulación de una base de datos de productos en memoria usando una lista de diccionarios
PRODUCTOS_DB = [
    {"id": 1, "nombre": "Yerba Mate Misionera Premium", "precio": 3500.0},
    {"id": 2, "nombre": "Té Negro Misiones 500g", "precio": 2100.0}
]

# Clase manejadora que define cómo responder a las peticiones HTTP que llegan al servidor
class PyLPApiHandler(BaseHTTPRequestHandler):
    
    # Función auxiliar para configurar las cabeceras HTTP de respuesta
    def _set_headers(self, status_code=200):
        # 1. Envía el código de estado (ej: 200 OK, 404 Not Found, 201 Created)
        self.send_response(status_code)
        # 2. Envía la cabecera indicando que el contenido devuelto es en formato JSON
        self.send_header('Content-Type', 'application/json')
        # 3. Finaliza la sección de cabeceras HTTP
        self.end_headers()

    # Maneja las peticiones HTTP GET (Consulta de datos)
    def do_GET(self):
        # Caso 1: Ruta para verificar el estado del servidor (Health Check)
        if self.path == '/api/v1/health':
            self._set_headers(200) # Establece respuesta exitosa
            res = {"status": "online", "timestamp": datetime.now().isoformat()}
            # Convierte el diccionario a JSON codificado en UTF-8 y lo escribe en el flujo de salida
            self.wfile.write(json.dumps(res).encode('utf-8'))
            
        # Caso 2: Ruta para listar todos los productos
        elif self.path == '/api/v1/productos':
            self._set_headers(200)
            # Retorna la base de datos de productos en formato JSON
            self.wfile.write(json.dumps(PRODUCTOS_DB).encode('utf-8'))
            
        # Caso 3: Ruta desconocida (Retorna Error 404)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Recurso no encontrado"}).encode('utf-8'))

    # Maneja las peticiones HTTP POST (Creación/Envío de datos)
    def do_POST(self):
        # Solo procesamos si el POST se hace en la ruta de productos
        if self.path == '/api/v1/productos':
            # 1. Obtiene la longitud del cuerpo de la petición (en bytes)
            length = int(self.headers.get('Content-Length', 0))
            # 2. Lee del flujo de entrada ('rfile') la cantidad de bytes indicada
            body = self.rfile.read(length)
            
            try:
                # 3. Convierte los bytes leídos de JSON a un diccionario de Python
                data = json.loads(body.decode('utf-8'))
                
                # Validación: Verifica que se hayan enviado los campos requeridos
                if "nombre" not in data or "precio" not in data:
                    self._set_headers(400) # Bad Request
                    self.wfile.write(json.dumps({"error": "Faltan campos 'nombre' o 'precio'"}).encode('utf-8'))
                    return
                
                # 4. Crea el nuevo producto, asignándole un ID autoincremental
                nuevo = {
                    "id": len(PRODUCTOS_DB) + 1, 
                    "nombre": data["nombre"], 
                    "precio": float(data["precio"])
                }
                # 5. Agrega el nuevo producto a nuestra base de datos simulada
                PRODUCTOS_DB.append(nuevo)
                
                # 6. Envía respuesta indicando que fue creado (201 Created) junto con el nuevo producto
                self._set_headers(201)
                self.wfile.write(json.dumps(nuevo).encode('utf-8'))
                
            except json.JSONDecodeError:
                # Maneja el caso de que los datos enviados no sean un JSON válido
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "JSON invalido"}).encode('utf-8'))

# Inicialización y arranque del servidor web local
if __name__ == '__main__':
    # Configura el servidor en la IP local (puerto 8080) usando nuestro manejador PyLPApiHandler
    server = HTTPServer(('', 8080), PyLPApiHandler)
    print("🚀 Servidor PyLP III corriendo en http://localhost:8080")
    # Mantiene el servidor escuchando peticiones indefinidamente
    server.serve_forever()
