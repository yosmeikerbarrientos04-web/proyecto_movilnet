document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registroForm');
    const mensaje = document.getElementById('mensaje-registro');

    if (!form) return; // Seguridad por si el formulario no carga

    form.addEventListener('submit', function(e) {
        // 1. BLOQUEAMOS el envío automático para que el JS valide
        e.preventDefault(); 

        // Captura de datos de los inputs
        const nombre = document.getElementById('nombre').value.trim();
        const apellido = document.getElementById('apellido').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const p1 = document.getElementById('pass1').value;
        const p2 = document.getElementById('pass2').value;

        // 2. VALIDACIONES
        if (nombre === "" || apellido === "") {
            mostrarError("❌ Por favor, llena todos los campos.");
            return;
        }

        if (p1 !== p2) {
            mostrarError("❌ Las contraseñas no coinciden.");
            return;
        }

        if (p1.length < 6) {
            mostrarError("❌ La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        if (telefono.length < 11) {
            mostrarError("❌ El número Movilnet debe tener 11 dígitos.");
            return;
        }

        // 3. SI TODO ESTÁ CORRECTO:
        mensaje.style.color = "#2ecc71"; // Verde Movilnet
        mensaje.innerText = "✅ Datos validados. Guardando...";

        // Guardamos el nombre para usarlo en la bienvenida después
        localStorage.setItem('usuarioNombre', nombre);

        // 4. ENVIAR AL PHP (El paso final que faltaba)
        // Usamos form.submit() para que el navegador dispare el action="verificacion.php"
        setTimeout(() => {
            form.submit(); 
        }, 800);
    });

    // Función auxiliar para no repetir código de error
    function mostrarError(texto) {
        mensaje.style.color = "#e74c3c"; // Rojo error
        mensaje.innerText = texto;
    }
});