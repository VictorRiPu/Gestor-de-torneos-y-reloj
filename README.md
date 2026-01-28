# Gestor de Torneos de Fútbol con Reloj Integrado

Este proyecto es una aplicación de escritorio para la gestión de torneos de fútbol, que incluye un reloj digital integrado. Permite organizar equipos, gestionar calendarios, clasificaciones, resultados y participantes de manera sencilla y visual.

## Estructura del Proyecto

El proyecto está desarrollado siguiendo el patrón de arquitectura **MVC (Modelo-Vista-Controlador)**:

- **Modelos (Models):** Encargados de la lógica de negocio y la gestión de datos (por ejemplo, base de datos y lógica de torneos).
- **Vistas (Views):** Interfaz gráfica de usuario, desarrollada con PySide6 y archivos `.ui`.
- **Controladores (Controllers):** Gestionan la interacción entre las vistas y los modelos, coordinando la lógica de la aplicación.

La aplicación está dividida en dos módulos principales:
- **Gestor de Torneos de Fútbol:** Permite crear, modificar y gestionar torneos, equipos, calendarios y resultados.
- **Reloj Digital:** Widget de reloj integrado para el control del tiempo en los partidos o eventos.

## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/VictorRiPu/Gestor-de-torneos-y-reloj.git
   ```
2. **Accede a la carpeta del proyecto:**
   ```bash
   cd Gestor-de-torneos-y-reloj
   ```
3. **Instala las dependencias necesarias:**
   Se recomienda usar un entorno virtual. Instala las dependencias con:
   ```bash
   pip install -r requirements.txt
   ```
   Si no existe el archivo `requirements.txt`, asegúrate de instalar al menos:
   - PySide6
   - sqlite3 (incluido en Python estándar)

4. **Ejecuta la aplicación:**
   ```bash
   python Rivera_Puebla_Victor_appTorneoFutbol/main.py
   ```

## Notas
- El reloj digital se encuentra en el módulo `Rivera_Puebla_Victor_appReloj` y puede integrarse o ejecutarse de forma independiente.
- La estructura modular permite ampliar fácilmente la funcionalidad del gestor o del reloj.

---
Desarrollado para fines educativos en 2º DAM - Desarrollo de Interfaces.