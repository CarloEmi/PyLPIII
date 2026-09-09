// URL base de la API backend desarrollada en el AE1
const API_URL = 'http://localhost:8080/api/v1/productos';

// Elementos de la interfaz
const contenedorLista = document.getElementById('listado');
const alertaError = document.getElementById('caja-error');
const alertaExito = document.getElementById('caja-exito');
const formulario = document.getElementById('formulario-registro');

// Función auxiliar para limpiar alertas visuales
function limpiarAlertas() {
    alertaError.style.display = 'none';
    alertaExito.style.display = 'none';
}

// 1. CARGAR DATOS (GET Asíncrono)
async function obtenerRegistros() {
    try {
        const respuesta = await fetch(API_URL);

        if (!respuesta.ok) {
            throw new Error(`Error en el servidor código ${respuesta.status}`);
        }

        const items = await respuesta.json();

        contenedorLista.innerHTML = '';

        if (items.length === 0) {
            contenedorLista.innerHTML = '<p style="color: var(--color-texto-secundario);">No hay registros almacenados.</p>';
            return;
        }

        // Renderizado dinámico usando las clases de styles.css
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
        console.error('Fallo en la comunicación', error);
        contenedorLista.innerHTML = '<p style="color: var(--color-error-texto);">No se pudo conectar con el servidor backend.</p>';
    }
}

// 2. DAR DE ALTA (POST con Payload JSON)
formulario.addEventListener('submit', async (e) => {
    e.preventDefault(); // Evita la recarga de página
    limpiarAlertas();

    const nombre = document.getElementById('campo-nombre').value.trim();
    const precio = parseFloat(document.getElementById('campo-precio').value);

    const payload = { nombre: nombre, precio: precio };

    try {
        const respuesta = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await respuesta.json();

        if (respuesta.status === 201) {
            // Éxito: Feedback visual en verde y refresco automático
            alertaExito.textContent = `¡Registro guardado con éxito! (#${resultado.id})`;
            alertaExito.style.display = 'block';

            formulario.reset();
            obtenerRegistros(); // Actualiza la lista sin F5

        } else if (respuesta.status === 400) {
            // Error de negocio: Feedback visual en rojo
            alertaError.textContent = resultado.error || 'Datos incompletos o inválidos según el backend.';
            alertaError.style.display = 'block';
        }

    } catch (error) {
        alertaError.textContent = 'No se pudo comunicar con el servidor backend. Verifique que esté ejecutándose.';
        alertaError.style.display = 'block';
    }
});

// Llamada inicial para poblar la vista al cargar la pantalla
obtenerRegistros();

