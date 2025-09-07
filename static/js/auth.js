/**
 * Sistema de Autenticación y Timeout de Sesión
 * Maneja la verificación de autenticación y cierre automático por inactividad
 */

// Variables globales para el sistema de timeout
let inactivityTimer;
let lastActivityTime;
let TIMEOUT_MINUTES = 30; // Valor por defecto, se actualiza desde el servidor
let WARNING_MINUTES = 2;  // Valor por defecto, se actualiza desde el servidor
let CHECK_INTERVAL = 60;  // Valor por defecto, se actualiza desde el servidor

// Función para verificar autenticación
function checkAuthentication() {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Función para cerrar sesión
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    // También limpiar cookies
    document.cookie = "auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.href = '/login';
}

// Función para resetear el timer de inactividad
function resetInactivityTimer() {
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }
    
    lastActivityTime = Date.now();
    
    inactivityTimer = setTimeout(() => {
        // Mostrar advertencia antes de cerrar sesión
        showTimeoutWarning();
    }, (TIMEOUT_MINUTES - WARNING_MINUTES) * 60 * 1000);
}

// Función para mostrar advertencia de timeout
function showTimeoutWarning() {
    // Crear modal de advertencia
    const warningModal = document.createElement('div');
    warningModal.className = 'modal fade';
    warningModal.id = 'timeoutWarningModal';
    warningModal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title">
                        <i class="bi bi-exclamation-triangle"></i> Sesión por expirar
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Tu sesión expirará en <strong id="countdown">${WARNING_MINUTES * 60}</strong> segundos por inactividad.</p>
                    <p>¿Deseas continuar con la sesión activa?</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="logout()">
                        Cerrar Sesión
                    </button>
                    <button type="button" class="btn btn-primary" onclick="extendSession()">
                        Continuar Sesión
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(warningModal);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(warningModal);
    modal.show();
    
    // Iniciar countdown
    let countdown = WARNING_MINUTES * 60;
    const countdownElement = document.getElementById('countdown');
    
    const countdownInterval = setInterval(() => {
        countdown--;
        if (countdownElement) {
            countdownElement.textContent = countdown;
        }
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            modal.hide();
            logout();
        }
    }, 1000);
    
    // Limpiar modal cuando se cierre
    warningModal.addEventListener('hidden.bs.modal', () => {
        clearInterval(countdownInterval);
        document.body.removeChild(warningModal);
    });
}

// Función para extender la sesión
function extendSession() {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    
    if (!token) {
        // No hay token, redirigir al login
        window.location.href = '/login';
        return;
    }
    
    try {
        // Verificar si el token ya expiró
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expTime = payload.exp * 1000;
        const currentTime = Date.now();
        
        if (currentTime >= expTime) {
            // Token ya expiró, no se puede extender
            alert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
            logout();
            return;
        }
        
        // Cerrar modal de advertencia si existe
        const modal = bootstrap.Modal.getInstance(document.getElementById('timeoutWarningModal'));
        if (modal) {
            modal.hide();
        }
        
        // Cerrar toast de advertencia si existe
        const toastElements = document.querySelectorAll('.toast');
        toastElements.forEach(toast => {
            const bsToast = bootstrap.Toast.getInstance(toast);
            if (bsToast) {
                bsToast.hide();
            }
        });
        
        // Resetear timer de inactividad
        resetInactivityTimer();
        
        // Hacer ping al servidor para verificar que el token sigue siendo válido
        fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).then(response => {
            if (response.ok) {
                console.log('Sesión extendida exitosamente');
            } else {
                console.log('Token inválido, redirigiendo al login');
                logout();
            }
        }).catch(error => {
            console.log('Error verificando sesión:', error);
            logout();
        });
        
    } catch (error) {
        console.log('Error procesando token:', error);
        logout();
    }
}

// Función para detectar actividad del usuario
function detectUserActivity() {
    resetInactivityTimer();
}

// Configurar eventos para detectar actividad
function setupActivityDetection() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
        document.addEventListener(event, detectUserActivity, true);
    });
    
    // También detectar actividad en ventanas
    window.addEventListener('focus', detectUserActivity);
    window.addEventListener('blur', detectUserActivity);
}

// Función para verificar si el token está próximo a expirar
function checkTokenExpiration() {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    if (!token) {
        return;
    }
    
    try {
        // Decodificar el token JWT (solo la parte del payload)
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expTime = payload.exp * 1000; // Convertir a milisegundos
        const currentTime = Date.now();
        const timeUntilExpiry = expTime - currentTime;
        
        // Si expira en menos de 5 minutos, mostrar advertencia
        if (timeUntilExpiry < 5 * 60 * 1000) {
            showTokenExpiryWarning(timeUntilExpiry);
        }
    } catch (error) {
        console.log('Error verificando expiración del token:', error);
    }
}

// Función para mostrar advertencia de expiración del token
function showTokenExpiryWarning(timeUntilExpiry) {
    const minutes = Math.floor(timeUntilExpiry / 60000);
    const seconds = Math.floor((timeUntilExpiry % 60000) / 1000);
    
    // Si el tiempo es negativo, la sesión ya expiró
    if (timeUntilExpiry <= 0) {
        alert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
        logout();
        return;
    }
    
    // Crear notificación toast
    const toast = document.createElement('div');
    toast.className = 'toast position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast-header bg-warning text-dark">
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong class="me-auto">Sesión por expirar</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            Tu sesión expirará en ${minutes}:${seconds.toString().padStart(2, '0')} minutos.
            <button class="btn btn-sm btn-primary ms-2" onclick="extendSession()">
                Extender
            </button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Auto-remover después de 10 segundos
    setTimeout(() => {
        if (document.body.contains(toast)) {
            document.body.removeChild(toast);
        }
    }, 10000);
}

// Función para cargar configuraciones del servidor
async function loadServerConfig() {
    try {
        const response = await fetch('/api/v1/settings/');
        if (response.ok) {
            const settings = await response.json();
            
            // Actualizar configuraciones de timeout si están disponibles
            if (settings.session_timeout_minutes) {
                TIMEOUT_MINUTES = settings.session_timeout_minutes;
            }
            if (settings.session_warning_minutes) {
                WARNING_MINUTES = settings.session_warning_minutes;
            }
            if (settings.session_check_interval) {
                CHECK_INTERVAL = settings.session_check_interval;
            }
            
            console.log('Configuraciones de sesión cargadas:', {
                timeout: TIMEOUT_MINUTES,
                warning: WARNING_MINUTES,
                checkInterval: CHECK_INTERVAL
            });
        }
    } catch (error) {
        console.log('Error cargando configuraciones del servidor:', error);
    }
}

// Función para inicializar el sistema de autenticación
async function initAuthSystem() {
    // Cargar configuraciones del servidor primero
    await loadServerConfig();
    
    // Verificar autenticación al cargar la página
    checkAuthentication();
    
    // Iniciar el timer de inactividad
    resetInactivityTimer();
    
    // Configurar detección de actividad
    setupActivityDetection();
    
    // Verificar expiración del token
    checkTokenExpiration();
    
    // Configurar verificación periódica del token
    setInterval(checkTokenExpiration, CHECK_INTERVAL * 1000);
    
    console.log('Sistema de autenticación inicializado con timeout de', TIMEOUT_MINUTES, 'minutos');
}

// Exportar funciones para uso global
window.checkAuthentication = checkAuthentication;
window.logout = logout;
window.extendSession = extendSession;
window.initAuthSystem = initAuthSystem;
