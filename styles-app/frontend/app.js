/* ==========================================================================
   LÓGICA DEL CLIENTE WEB (ASINCRONÍA Y FETCH API) - PyLP III
   UCP Posadas - FAITA
   ==========================================================================
   Propósito del Archivo:
   Este script implementa la capa controladora del Frontend. Se encarga de:
   1. Gestionar la comunicación HTTP asíncrona con el backend (API REST) mediante Fetch API.
   2. Manipular reactivamente el DOM (Document Object Model) sin recargar la página (SPA - Single Page Application behavior).
   3. Serializar y deserializar datos en formato JSON.
   4. Proveer validaciones y retroalimentación visual al usuario según los códigos de estado HTTP.
   ========================================================================== */

/* ==========================================================================
   CONFIGURACIÓN GLOBAL Y ENDPOINTS
   ==========================================================================
   Constante API_URL:
   - Define el punto de acceso (endpoint) base expuesto por el servidor backend.
   - Sigue el estándar RESTful con versionado de API (/api/v1/productos).
   
   Uso correcto:
   - Al desplegar en producción o cambiar el puerto del servidor, solo se modifica
     este valor centralizado sin alterar el resto de las funciones.
   ========================================================================== */
const API_URL = 'http://localhost:8080/api/v1/productos';

/* ==========================================================================
   REFERENCIAS A ELEMENTOS DEL DOM (CACHE DE SELECTORES)
   ==========================================================================
   Propósito:
   Almacenar en constantes (`const`) las referencias a los nodos HTML que serán
   manipulados frecuentemente.
   
   Buenas prácticas:
   - Cachear los elementos una sola vez al inicio mejora drásticamente el rendimiento,
     evitando búsquedas repetitivas e innecesarias en el árbol DOM con cada evento.
   - Uso de nombres descriptivos que coinciden con su rol en la interfaz.
   ========================================================================== */
const contenedorLista = document.getElementById('listado');            // Contenedor donde se inyectan las tarjetas de registros
const alertaError = document.getElementById('caja-error');              // Banner visual para notificar fallos y errores HTTP 4xx/5xx
const alertaExito = document.getElementById('caja-exito');              // Banner visual para notificar operaciones exitosas (HTTP 200/201)
const formulario = document.getElementById('formulario-registro');      // Formulario de captura y envío de nuevos datos

/* ==========================================================================
   UTILIDADES VISUALES (HELPERS)
   ==========================================================================
   Función limpiarAlertas():
   - Oculta ambas cajas de notificación (`display = 'none'`).
   
   Uso correcto:
   - Debe invocarse antes de iniciar cualquier nueva transacción o petición de red,
     asegurando que el usuario no visualice mensajes obsoletos de operaciones previas.
   ========================================================================== */
function limpiarAlertas() {
    alertaError.style.display = 'none';
    alertaExito.style.display = 'none';
}

/* ==========================================================================
   1. CARGA Y RENDERIZADO DE DATOS (PETICIÓN HTTP GET ASÍNCRONA)
   ==========================================================================
   Función obtenerRegistros():
   - Consulta al servidor backend para obtener el listado de recursos actualizado.
   - Es una función asíncrona (`async`), lo que permite el uso de `await` para 
     esperar las respuestas de red de forma no bloqueante (mantiene la UI fluida).

   Aspectos clave:
   - Bloque `try...catch`: Captura tanto excepciones de red (ej. servidor caído) 
     como errores generados manualmente.
   - Validación de `respuesta.ok`: Fundamental, ya que `fetch()` NO rechaza la promesa
     ante códigos de error HTTP como 404 o 500; solo la rechaza si hay un fallo físico de red.
   ========================================================================== */
async function obtenerRegistros() {
    try {
        // Ejecuta la solicitud GET al endpoint configurado
        const respuesta = await fetch(API_URL);

        // Si el código de respuesta no está en el rango 200-299, lanzamos un error explícito
        if (!respuesta.ok) {
            throw new Error(`Error en el servidor código ${respuesta.status}`);
        }

        // Deserializa el cuerpo de la respuesta de texto JSON a un array de objetos JavaScript
        const items = await respuesta.json();

        // Limpia el contenido anterior del contenedor (remueve el "Cargando..." o listados viejos)
        contenedorLista.innerHTML = '';

        // Manejo de estado vacío (Zero State): informa al usuario si la base de datos no tiene filas
        if (items.length === 0) {
            contenedorLista.innerHTML = '<p style="color: var(--color-texto-secundario);">No hay registros almacenados.</p>';
            return;
        }

        /* 
          Renderizado Dinámico de Componentes:
          - Itera sobre cada producto recuperado.
          - Crea programáticamente un nodo `<div>` asignándole la clase `.tarjeta-item`.
          - Emplea Template Literals (plantillas de cadena con comillas invertidas)
            para interpolar id, nombre y precio formateado a 2 decimales (`toFixed(2)`).
          - Inserta el elemento en el DOM usando `appendChild()`.
        */
        items.forEach(item => {
            const tarjeta = document.createElement('div');
            tarjeta.className = 'tarjeta-item';
            tarjeta.innerHTML = `
                <div>
                    <strong>#${item.id} - ${item.nombre}</strong>
                </div>
                <span class="precio-tag">$${item.precio.toFixed(2)}</span>
            `;
            contenedorLista.appendChild(tarjeta);
        });

    } catch (error) {
        // Manejo de contingencia ante fallas de conectividad o excepciones no controladas
        console.error('Fallo en la comunicación', error);
        contenedorLista.innerHTML = '<p style="color: var(--color-error-texto);">No se pudo conectar con el servidor backend.</p>';
    }
}

/* ==========================================================================
   2. REGISTRO DE NUEVOS ELEMENTOS (PETICIÓN HTTP POST CON PAYLOAD JSON)
   ==========================================================================
   Manejador del Evento 'submit' del Formulario:
   - Captura la acción de guardado disparada por el usuario.
   
   Flujo de Ejecución:
   1. `e.preventDefault()`: Detiene la recarga por defecto del navegador web.
   2. Limpieza de mensajes previos con `limpiarAlertas()`.
   3. Extracción y sanitización de datos (`.trim()` en cadenas, `parseFloat()` en números).
   4. Construcción del objeto `payload`.
   5. Envío mediante `fetch()` configurando método POST, cabecera `Content-Type` y cuerpo JSON.
   6. Evaluación de códigos de respuesta (201 Created vs 400 Bad Request vs errores de red).
   ========================================================================== */
formulario.addEventListener('submit', async (e) => {
    // Evita el comportamiento clásico de envío de formularios que recargaría la página completa
    e.preventDefault(); 
    
    // Oculta alertas visibles de intentos anteriores
    limpiarAlertas();

    // Obtención de valores desde los inputs del formulario
    const nombre = document.getElementById('campo-nombre').value.trim(); // .trim() remueve espacios en blanco accidentales
    const precio = parseFloat(document.getElementById('campo-precio').value); // Convierte el texto numérico a valor de punto flotante

    // Construcción del objeto de transferencia de datos (DTO) en memoria
    const payload = { nombre: nombre, precio: precio };

    try {
        /*
          Llamada Fetch con método POST:
          - `method: 'POST'`: Indica creación de nuevo recurso.
          - `headers`: Cabecera 'Content-Type': 'application/json' informa al backend que el cuerpo está en JSON.
          - `body: JSON.stringify(payload)`: Serializa el objeto JavaScript a un string con formato JSON válido.
        */
        const respuesta = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // Parsea la respuesta devuelta por la API (que incluye el nuevo ID generado o el mensaje de error)
        const resultado = await respuesta.json();

        // CASO DE ÉXITO: Código HTTP 201 (Created)
        if (respuesta.status === 201) {
            // Informa al usuario con feedback visual positivo
            alertaExito.textContent = `¡Registro guardado con éxito! (#${resultado.id})`;
            alertaExito.style.display = 'block';

            // Restablece los campos del formulario a su estado vacío original
            formulario.reset();
            
            // Refresca la lista de registros en tiempo real sin requerir recargar la página (F5)
            obtenerRegistros(); 

        // CASO DE ERROR DE VALIDACIÓN O REGLA DE NEGOCIO: Código HTTP 400 (Bad Request)
        } else if (respuesta.status === 400) {
            // Muestra el mensaje específico enviado por el backend o un texto de respaldo
            alertaError.textContent = resultado.error || 'Datos incompletos o inválidos según el backend.';
            alertaError.style.display = 'block';
        }

    } catch (error) {
        // Captura fallas de red, CORS no configurado o servidor inaccesible
        alertaError.textContent = 'No se pudo comunicar con el servidor backend. Verifique que esté ejecutándose.';
        alertaError.style.display = 'block';
    }
});

/* ==========================================================================
   INICIALIZACIÓN AUTOMÁTICA
   ==========================================================================
   Propósito:
   Ejecuta la función `obtenerRegistros()` inmediatamente cuando el script es
   cargado por el navegador, garantizando que el usuario vea los datos existentes
   apenas se inicializa la página sin necesidad de interactuar manualmente.
   ========================================================================== */
obtenerRegistros();
