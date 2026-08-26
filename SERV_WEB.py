#============================================================================== 
# ASIGNATURA: Paradigmas y Lenguajes de Programación III (UCP - FAITA) 
# DOCENTE: Prof. Carlos Emiliano Pereyra (Carlin) 
# ARCHIVO: servidor_web.py 
# DESCRIPCIÓN: Servidor HTTP nativo con ruteo, manejo de JSON y Status Codes. 
# ============================================================================== 
 
# Importamos las clases necesarias para crear el servidor de socket y gestionar peticiones HTTP 
from http.server import HTTPServer, BaseHTTPRequestHandler 
import json  # Librería nativa para serializar (dict -> str) y deserializar (str -> dict) JSON 
from datetime import datetime  # Para generar timestamps en el healthcheck 
 
# ------------------------------------------------------------------------------ 
# BASE DE DATOS EN MEMORIA (Simulación de la Capa de Datos) 
# ------------------------------------------------------------------------------ 
PRODUCTOS_DB = [ 
    {"id": 1, "nombre": "Yerba Mate Misionera Premium", "precio": 3500.0}, 
    {"id": 2, "nombre": "Té Negro Misiones 500g", "precio": 2100.0} 
] 
 
# ------------------------------------------------------------------------------ 
# CLASE MANEJA DE PETICIONES (Capa de Presentacion / Rutas) 
# Inherita de BaseHTTPRequestHandler para sobreescribir los metodos do_GET y do_POST 
# ------------------------------------------------------------------------------ 
class PyLPApiHandler(BaseHTTPRequestHandler): 
 
    def _set_headers(self, status_code=200): 
        """ 
        Método auxiliar privado para enviar la línea de estado y encabezados HTTP. 
        - status_code: Código de estado HTTP (200, 201, 400, 404, etc.) 
        """ 
        self.send_response(status_code)  # Envía la linea de estado (Ej: HTTP/1.1 200 OK) 
        self.send_header('Content-Type', 'application/json')  # Le avisa al cliente que el body es JSON 
        self.send_header('Access-Control-Allow-Origin', '*')  # Habilitar CORS para pruebas 
        self.end_headers()  # Fin de la sección de encabezados (agrega linea en blanco obligatoria) 
 
    def do_GET(self): 
        """ 
        Manejador automático para peticiones de lectura (HTTP GET) 
        """ 
        # Evaluamos la ruta solicitada por el cliente mediante self.path 
        if self.path == '/api/v1/health': 
            # Ruta de monitoreo de estado del servidor 
            self._set_headers(200)  # Estado 200 OK 
            respuesta = { 
                "status": "online", 
                "timestamp": datetime.now().isoformat(), 
                "materia": "PyLP III - UCP Sede Posadas" 
            } 
            # json.dumps convierte el diccionario en un string JSON 
            # .encode('utf-8') convierte el string en bytes para enviarlo por la red 
            self.wfile.write(json.dumps(respuesta).encode('utf-8')) 
 
        elif self.path == '/api/v1/productos': 
            # Ruta para listar todos los productos 
            self._set_headers(200)  # Estado 200 OK 
            self.wfile.write(json.dumps(PRODUCTOS_DB).encode('utf-8')) 
 
        else: 
            # Si la ruta no coincide con ninguna configurada, devolvemos 404 Not Found 
            self._set_headers(404)  # Estado 404 Not Found 
            error_payload = { 
                "error": "Recurso no encontrado", 
                "path_solicitado": self.path 
            } 
            self.wfile.write(json.dumps(error_payload).encode('utf-8')) 
 
    def do_POST(self): 
        """ 
        Manejador automático para peticiones de creación (HTTP POST) 
        """ 
        if self.path == '/api/v1/productos': 
            # 1. Leemos el encabezado Content-Length para saber cuántos bytes mide el body 
            length = int(self.headers.get('Content-Length', 0)) 
             
            # 2. Leemos exactamente esa cantidad de bytes del flujo de entrada (self.rfile) 
            body_bytes = self.rfile.read(length) 
 
            try: 
                # 3. Convertimos los bytes a string UTF-8 y luego a un diccionario Python con 
                json.loads 
                data = json.loads(body_bytes.decode('utf-8')) 
 
                # 4. VALIDACIÓN DE REGLAS DE NEGOCIO (Saber Hacer Tecnico) 
                if "nombre" not in data or "precio" not in data: 
                    self._set_headers(400)  # Estado 400 Bad Request 
                    error_val = {"error": "Bad Request: Faltan campos obligatorios 'nombre' o 'precio'"} 
                    self.wfile.write(json.dumps(error_val).encode('utf-8')) 
                    return  # Cortamos la ejecucion 
 
                # 5. Si la validacion pasa, creamos el nuevo objeto 
                nuevo_producto = { 
                    "id": len(PRODUCTOS_DB) + 1, 
                    "nombre": data["nombre"], 
                    "precio": float(data["precio"]) 
                } 
                PRODUCTOS_DB.append(nuevo_producto) 
 
                # 6. Respondemos con 201 Created y el objeto recién creado 
                self._set_headers(201)  # Estado 201 Created 
                self.wfile.write(json.dumps(nuevo_producto).encode('utf-8')) 
 
            except json.JSONDecodeError: 
                # Si el cliente envio un JSON mal formado (sintaxis rota) 
                self._set_headers(400)  # Estado 400 Bad Request 
                self.wfile.write(json.dumps({"error": "JSON mal formado en el payload"}).encode('utf-8')) 
        else: 
            self._set_headers(404) 
 
# ------------------------------------------------------------------------------ 
# PUNTO DE ENTRADA Y PUESTA EN MARCHA DEL SERVIDOR 
# ------------------------------------------------------------------------------ 
if __name__ == '__main__': 
    PUERTO = 8080 
    # Creamos la instancia del servidor vinculando el puerto y nuestra clase Handler 
    server = HTTPServer(('', PUERTO), PyLPApiHandler) 
    print(f"Servidor PyLP III corriendo exitosamente en http://localhost:{PUERTO}") 
    print("Endpoints listos para probar:") 
    print(f"  - GET  http://localhost:{PUERTO}/api/v1/health") 
    print(f"  - GET  http://localhost:{PUERTO}/api/v1/productos") 
    print(f"  - POST http://localhost:{PUERTO}/api/v1/productos")

    server.serve_forever()