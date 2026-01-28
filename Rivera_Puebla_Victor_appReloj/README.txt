Reloj Digital PySide6
=====================

Requisitos
----------
1. Instala las dependencias: `pip install PySide6`.
2. Asegúrate de que el archivo reloj.ui permanezca junto a reloj_widget.py y main.py.

Ejecución rápida
----------------
1. Desde este directorio ejecuta `python main.py`.
2. El widget arranca en español por defecto; si quieres forzar otro idioma desde la línea de comandos usa `python main.py --lang=es` o `--lang=en` (también puedes cambiarlo desde el desplegable integrado).

Uso del widget
--------------
- Importa la clase RelojDigital desde reloj_widget.py y añádela a cualquier layout existente.
- Cambia entre los tres modos (clock, timer, alarm) con la propiedad pública mode o con el botón integrado de modo.
- El modo alarm muestra la próxima alarma programada y el tiempo restante hasta que suene, ideal para recordatorios rápidos.
- Usa el botón Set Alarm para introducir una hora (HH:MM) y activar inmediatamente la alarma sin escribir código; el selector incorpora flechas para subir/bajar minutos y horas cómodamente.
- Cuando la alarma se dispara o el temporizador cuenta atrás llega a cero, el widget muestra un mensaje emergente para avisarte.
- Controla el temporizador con los métodos públicos start(), stop() y reset().
- Alterna entre temporizador (cuenta atrás) y cronómetro con el botón Use Stopwatch / Use Countdown o mediante la propiedad timerBehavior (valores countdown y stopwatch).
- Configura la alarma mediante alarmEnabled, alarmHour, alarmMinute y alarmMessage.
- El temporizador usa timerDuration (en segundos) cuando está en modo cuenta atrás.
- El widget escala automáticamente su contenido: el tamaño de fuente de los dígitos se ajusta dinámicamente al redimensionar la ventana, garantizando visibilidad óptima sin cortes de texto en cualquier tamaño de pantalla.

Internacionalización
--------------------
- El widget utiliza self.tr() y un QTranslator interno; arranca en español y permite conmutar dinámicamente a inglés desde el desplegable `Language` o con `setLanguage()`.
- También puedes mantener ficheros `.qm` externos si deseas ampliar a más idiomas: genera `reloj_{codigo}.qm`, colócalo en una carpeta `i18n` y cárgalo manualmente instalando tu propio QTranslator antes de crear el widget.

Integración con la app de torneos
---------------------------------
- En la aplicación "Gestión de Torneos de Fútbol" encontrarás el reloj en `Herramientas > Abrir Reloj/Cronómetro`; el controlador crea un QDialog desacoplado y añade el widget reutilizable sin tocar su lógica interna.
- El controlador principal muestra un mensaje informativo "Fin del tiempo del partido" cuando la señal `timerFinished` del componente se emite y reutiliza el texto de la señal `alarmTriggered` para los avisos de alarma.
