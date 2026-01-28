# Aplicación de Gestión de Torneos de Fútbol

**Autor:** Víctor Rivera Puebla  
**Versión:** 1.0  
**Curso:** 2º DAM - 2026

## Descripción

Aplicación de escritorio desarrollada en PySide6 para gestionar torneos de fútbol con sistema de eliminatorias. Permite registrar equipos, participantes (jugadores y árbitros), programar partidos, registrar resultados y visualizar brackets.

## Requisitos

- Python 3.8 o superior
- PySide6
- PyInstaller (opcional, para compilar)

## Instalación

1. Instalar las dependencias:

```bash
pip install PySide6
```

2. Para compilar a ejecutable (opcional):

```bash
pip install pyinstaller
```

## Ejecución

### Modo desarrollo

```bash
python main.py
```

### Compilar a ejecutable

```bash
pyinstaller --name="TorneoFutbol" --windowed --icon=Resources/iconos/tres-puntos.png --add-data="Views;Views" --add-data="Resources;Resources" main.py
```

El ejecutable estará en la carpeta `dist/TorneoFutbol/`

## Estructura del Proyecto

```
Rivera_Puebla_Victor_appTorneoFutbol/
│
├── main.py                          # Punto de entrada de la aplicación
├── instrucciones.txt                # Especificaciones del proyecto
│
├── Models/                          # Modelos y lógica de negocio
│   ├── database.py                  # Gestión de base de datos SQLite
│   └── torneo_logic.py              # Lógica de torneos y brackets
│
├── Views/                           # Interfaces de usuario (.ui)
│   ├── pantalla_principal.ui        # Ventana principal
│   ├── onboarding.ui                # Tutorial inicial
│   ├── gestion_equipos.ui           # Gestión de equipos
│   ├── participantes.ui             # Registro de participantes
│   ├── calendario.ui                # Calendario de partidos
│   ├── resultados.ui                # Registro de resultados
│   ├── clasificacion.ui             # Brackets y clasificación
│   └── nuevo_torneo.ui              # Creación de torneo
│
├── Controllers/                     # Controladores
│   ├── main_controller.py           # Controlador principal
│   ├── onboarding_controller.py     # Tutorial
│   ├── equipos_controller.py        # Gestión de equipos
│   ├── participantes_controller.py  # Gestión de participantes
│   ├── calendario_controller.py     # Gestión de partidos
│   ├── resultados_controller.py     # Registro de resultados
│   ├── clasificacion_controller.py  # Visualización de brackets
│   └── nuevo_torneo_controller.py   # Creación de torneos
│
└── Resources/                       # Recursos
    ├── img/                         # Imágenes y escudos
    │   ├── fondo.jpg                # Fondo de la aplicación
    │   └── [41 escudos SVG]         # Escudos de equipos
    ├── iconos/                      # Iconos de la UI
    │   ├── basura.png
    │   ├── tarjeta-amarilla.png
    │   ├── tarjeta-roja.png
    │   ├── meta.png
    │   ├── editar-texto.png
    │   └── tres-puntos.png
    └── qss/                         # Estilos
        └── estilos.qss              # Hoja de estilos CSS
```

## Base de Datos

La aplicación utiliza SQLite con las siguientes tablas:

- **Equipos**: Información de equipos (nombre, curso, escudo, color)
- **Participantes**: Datos básicos de participantes (nombre, fecha nacimiento, curso)
- **Jugadores**: Jugadores vinculados a equipos (posición)
- **Arbitros**: Árbitros registrados
- **Torneo**: Información del torneo activo
- **Partidos**: Partidos programados
- **Resultados**: Resultados de partidos
- **Eventos**: Goles y tarjetas por jugador

## Características

### Gestión de Equipos
- Crear/editar/eliminar equipos
- Seleccionar escudo de 41 opciones disponibles
- Asignar color personalizado
- Buscar equipos por nombre o curso
- Validación de mínimo 7 jugadores por equipo

### Gestión de Participantes
- Registrar jugadores (con posición y equipo)
- Registrar árbitros
- Participantes mixtos (jugador + árbitro)
- Formato de fecha español (DD/MM/YYYY)

### Calendario
- Visualizar partidos programados
- Registrar nuevos partidos
- Asignar árbitros con validación de disponibilidad
- Eliminar partidos

### Resultados
- Registrar marcadores
- Asignar goles a jugadores
- Registrar tarjetas (amarillas/rojas)
- Avance automático de rondas en fase eliminatoria

### Clasificación
- Visualización gráfica de brackets
- Árbol de eliminatorias con escudos
- Estadísticas del torneo

### Nuevo Torneo
- Crear torneos de 8, 16 o 32 equipos
- Validación automática de equipos
- Generación aleatoria de emparejamientos
- Control de torneo activo único

## Flujo de Uso

1. **Tutorial inicial**: Al abrir la app, se muestra un tutorial explicativo
2. **Crear equipos**: Registrar al menos 8 equipos con mínimo 7 jugadores cada uno
3. **Registrar participantes**: Añadir jugadores a los equipos y árbitros
4. **Crear torneo**: Seleccionar 8, 16 o 32 equipos para iniciar
5. **Programar partidos**: Asignar fechas y árbitros en el calendario
6. **Registrar resultados**: Anotar marcadores, goles y tarjetas
7. **Ver clasificación**: Consultar el bracket actualizado
8. **Finalizar torneo**: Terminar el torneo cuando esté completo

## Notas Técnicas

- La aplicación usa QUiLoader para cargar interfaces dinámicamente
- Compatible con PyInstaller para distribución
- Sistema de recursos con `obtener_ruta_recurso()` para ejecutables
- Locale español configurado para formato de fechas
- Estilos QSS con transparencias y tema verde

## Créditos

Desarrollado por **Víctor Rivera Puebla** como proyecto de **Desarrollo de Interfaces** - 2º DAM (2026)

---

## Solución de Problemas

### Error al cargar .ui
- Verificar que la carpeta `Views/` existe y contiene los archivos .ui
- Revisar rutas en PyInstaller

### Error al cargar escudos
- Verificar que la carpeta `Resources/img/` contiene los 41 archivos SVG
- Comprobar nombres de archivo exactos

### Error de base de datos
- La base de datos se crea automáticamente en la primera ejecución
- Se guarda como `torneo.db` en el directorio de la aplicación

### Interfaz sin estilos
- Verificar que existe `Resources/qss/estilos.qss`
- Revisar rutas de recursos en compilación

## Contacto

Para dudas o sugerencias, contactar con el autor.
