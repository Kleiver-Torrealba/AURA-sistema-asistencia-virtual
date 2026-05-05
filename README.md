# AURA - Sistema Automático de Registro de Asistencia 🎓✨

¡Hola! Soy **Kleiver Torrealba**, estudiante de Ingeniería en la Universidad José Antonio Páez (UJAP) en Valencia, Venezuela. 

**AURA** (anteriormente conocido como SAV) es un proyecto _Full-Stack_ que desarrollé para resolver un problema real y cotidiano en mi entorno universitario: la pérdida de tiempo y la falta de optimización en la toma de asistencia manual en las aulas. 

Este proyecto refleja mi capacidad para identificar una necesidad, diseñar una solución lógica y llevarla a la realidad escribiendo código limpio, seguro y escalable.

---

## 🚀 ¿Qué resuelve AURA?
El sistema moderniza el control de clases permitiendo a los profesores registrar la asistencia de sus secciones en segundos mediante códigos QR dinámicos, ofreciendo un panel de administración en tiempo real y un diseño enfocado en la experiencia de usuario (UX/UI).

## 💡 Funcionalidades que he desarrollado

Durante la construcción de este proyecto, trabajé en todo el ciclo de desarrollo (Backend y Frontend), implementando las siguientes características:

* **Generación de QR Dinámicos:** Creación de sesiones de clase únicas con tiempo de expiración. El código QR se genera en el backend y valida la autenticidad del escaneo.
* **Dashboard en Tiempo Real:** Un panel de control para el profesor donde puede visualizar contadores de estudiantes presentes, ausentes y el total de la sección.
* **Buscador Inteligente Integrado:** Implementación de un buscador interactivo con JavaScript puro que permite filtrar estudiantes por cédula o nombre para añadirlos manualmente.
* **Diseño UI/UX "Ultra-Polished":** Interfaz moderna en modo oscuro construida con **CSS puro**. Uso de técnicas de _glassmorphism_, micro-animaciones y diseño responsivo.
* **Gestión de Base de Datos:** Modelado de datos relacional para gestionar Usuarios, Secciones, Estudiantes y Registros de Asistencia.

---

## 🛠️ Stack Tecnológico

**Backend:**
* **Python 3.12+**
* **Django 6.0:** Framework principal para la lógica de negocio, ORM y enrutamiento.
* **PostgreSQL:** Base de datos principal para asegurar la integridad de los registros.
* **Librerías:** `qrcode`, `Pillow`, `python-dotenv`.

**Frontend:**
* **HTML5 / CSS3:** Maquetación semántica y estilos personalizados sin frameworks externos.
* **JavaScript (Vanilla):** Manejo del DOM, eventos asíncronos y lógica del buscador.

---

## ⚙️ Cómo ejecutar este proyecto en local

Si deseas probar **AURA** en tu entorno local, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Kleiver-Torrealba/AURA-sistema-asistencia-virtual.git](https://github.com/Kleiver-Torrealba/AURA-sistema-asistencia-virtual.git)
   cd AURA-sistema-asistencia-virtual

2. #Crear el entorno virtual
python -m venv env

# Activar el entorno (En Windows)
.\env\Scripts\activate

3. #Instalación de Dependencias Técnicas
pip install -r requirements.txt

4. Configuración de Seguridad y Variables (.env)
Por seguridad, los datos sensibles no se suben a GitHub. Crea un archivo manualmente llamado .env en la raíz del proyecto con las siguientes variables

SECRET_KEY=tu_clave_secreta_de_django
DB_NAME=db_ujap
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432

#5.  Migración de Base de Datos y Ejecución Finalmente, prepara las tablas en PostgreSQL y lanza el servidor de desarrollo

# Aplicar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
