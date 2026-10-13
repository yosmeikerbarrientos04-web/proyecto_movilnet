document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('loginform');
    const mensajeDiv = document.getElementById('mensaje-verificacion');

    if (!formulario) return;

    formulario.addEventListener('submit', function(event) {
        // 1. Evitamos el envío automático para validar la suma
        event.preventDefault();

        // Obtenemos los valores de los inputs ocultos y la respuesta
        // IMPORTANTE: Asegúrate que los IDs coincidan con tu HTML (id_num1 e id_num2)
        const n1 = parseInt(document.getElementById('id_num1').value);
        const n2 = parseInt(document.getElementById('id_num2').value);
        const respuestaUsuario = parseInt(document.getElementById('respuesta_usuario').value);
        
        const sumaCorrecta = n1 + n2;

        if (respuestaUsuario === sumaCorrecta) {
            // Éxito en la suma
            mensajeDiv.style.color = "#28a745"; 
            mensajeDiv.innerText = "✅ Verificación exitosa. Iniciando sesión...";
            
            // 2. ENVIAR AL PHP
            // Ahora sí, enviamos el formulario de verdad para que el PHP verifique correo y clave
            setTimeout(() => {
                formulario.submit(); 
            }, 800);

        } else {
            // Error en la suma
            mensajeDiv.style.color = "#dc3545"; 
            mensajeDiv.innerText = "❌ Suma incorrecta. Inténtalo de nuevo.";
            
            // Limpiamos el campo de respuesta
            document.getElementById('respuesta_usuario').value = '';
        }
    });
});