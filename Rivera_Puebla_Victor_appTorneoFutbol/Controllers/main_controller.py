from __future__ import annotations

"""
Controlador principal de la aplicación.
Gestiona la navegación entre pantallas y la lógica global.
"""

from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QPushButton, QDialog, QVBoxLayout
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
from Models.database import DatabaseManager, obtener_ruta_recurso
from Models.torneo_logic import TorneoLogic
from Controllers.nuevo_torneo_controller import NuevoTorneoController
from Views.components.reloj_widget import RelojDigital


class MainController:
    """
    Controlador principal que gestiona la ventana principal
    y la navegación entre diferentes pantallas.
    """
    
    def __init__(self, main_window: QMainWindow):
        """
        Inicializa el controlador principal.
        
        Args:
            main_window: Ventana principal de la aplicación
        """
        self.main_window = main_window
        self.db = DatabaseManager()
        self.torneo_logic = TorneoLogic()
        
        # Obtener el QStackedWidget de la ventana principal
        self.stacked_widget = self.main_window.findChild(QStackedWidget, "stackedWidget")
        
        # Diccionario para trackear las pantallas creadas
        self.pantallas = {}
        self._clock_dialog: QDialog | None = None
        self._clock_widget: RelojDigital | None = None
        self._current_language = "es"
        
        # Conectar señales de los botones principales
        self._conectar_senales()
        
        # Verificar si hay torneo activo al inicio
        self._verificar_torneo_activo()
        
    def _conectar_senales(self):
        """Conecta las señales de los botones del menú principal."""
        # Botones de navegación
        btn_equipos = self.main_window.findChild(object, "btnEquipos")
        if btn_equipos:
            btn_equipos.clicked.connect(lambda: self.navegar_a("equipos"))
            
        btn_participantes = self.main_window.findChild(object, "btnParticipantes")
        if btn_participantes:
            btn_participantes.clicked.connect(lambda: self.navegar_a("participantes"))
            
        btn_calendario = self.main_window.findChild(object, "btnCalendario")
        if btn_calendario:
            btn_calendario.clicked.connect(lambda: self.navegar_a("calendario"))
            
        btn_resultados = self.main_window.findChild(object, "btnResultados")
        if btn_resultados:
            btn_resultados.clicked.connect(lambda: self.navegar_a("resultados"))
            
        btn_clasificacion = self.main_window.findChild(object, "btnClasificacion")
        if btn_clasificacion:
            btn_clasificacion.clicked.connect(lambda: self.navegar_a("clasificacion"))
            
        btn_nuevo_torneo = self.main_window.findChild(object, "btnNuevoTorneo")
        if btn_nuevo_torneo:
            btn_nuevo_torneo.clicked.connect(self.abrir_nuevo_torneo)
            
        btn_finalizar = self.main_window.findChild(object, "btnFinalizarTorneo")
        if btn_finalizar:
            btn_finalizar.clicked.connect(self.finalizar_torneo)
            
        # Menú Ayuda y Créditos
        action_ayuda = self.main_window.findChild(object, "actionAyuda")
        if action_ayuda:
            action_ayuda.triggered.connect(self.mostrar_ayuda)
            
        action_creditos = self.main_window.findChild(object, "actionCreditos")
        if action_creditos:
            action_creditos.triggered.connect(self.mostrar_creditos)

        action_reloj = self.main_window.findChild(object, "actionAbrirReloj")
        if action_reloj:
            action_reloj.triggered.connect(self.abrir_reloj)
            
    def _verificar_torneo_activo(self):
        """
        Verifica si hay un torneo activo al iniciar la aplicación.
        Muestra mensaje informativo y botón de finalizar si existe.
        """
        torneo_activo = self.db.torneo_activo_existe()
        
        btn_finalizar = self.main_window.findChild(object, "btnFinalizarTorneo")
        
        if torneo_activo:
            # Mostrar botón de finalizar torneo
            if btn_finalizar:
                btn_finalizar.setVisible(True)
                
            # Mostrar mensaje informativo
            QMessageBox.information(
                self.main_window,
                "Torneo en Curso",
                f"Hay un torneo activo: {torneo_activo['nombre']}\n\n"
                f"Puedes continuar gestionándolo o finalizarlo desde el botón 'FIN DE TORNEO'."
            )
        else:
            # Ocultar botón de finalizar
            if btn_finalizar:
                btn_finalizar.setVisible(False)
                
    def navegar_a(self, pantalla: str):
        """
        Navega a una pantalla específica.
        
        Args:
            pantalla: Nombre de la pantalla destino
        """
        if pantalla == "equipos":
            self._cargar_equipos()
        elif pantalla == "participantes":
            self._cargar_participantes()
        elif pantalla == "calendario":
            from Views.calendario_view import crear_vista_calendario
            from Controllers.calendario_controller import CalendarioController
            
            # Crear vista de calendario (retorna widget y reloj)
            widget_calendario, reloj_widget = crear_vista_calendario()
            
            # Añadir al stacked widget
            self.stacked_widget.addWidget(widget_calendario)
            indice = self.stacked_widget.indexOf(widget_calendario)
            self.stacked_widget.setCurrentIndex(indice)
            
            # Crear controlador pasando el widget del reloj
            CalendarioController(widget_calendario, self, reloj_widget)
        elif pantalla == "resultados":
            from Views.resultados_view import crear_vista_resultados
            from Controllers.resultados_controller import ResultadosController
            
            # Crear vista de resultados
            widget_resultados = crear_vista_resultados()
            
            # Añadir al stacked widget
            self.stacked_widget.addWidget(widget_resultados)
            indice = self.stacked_widget.indexOf(widget_resultados)
            self.stacked_widget.setCurrentIndex(indice)
            
            # Crear controlador y guardarlo
            self.resultados_controller = ResultadosController(widget_resultados, self)
            
            # Establecer idioma del reloj
            if hasattr(self, '_current_language'):
                self.resultados_controller.establecer_idioma(self._current_language)
        elif pantalla == "clasificacion":
            from Views.clasificacion_view import crear_vista_clasificacion
            from Controllers.clasificacion_controller import ClasificacionController
            
            # Crear vista de clasificación
            widget_clasificacion = crear_vista_clasificacion()
            
            # Añadir al stacked widget
            self.stacked_widget.addWidget(widget_clasificacion)
            indice = self.stacked_widget.indexOf(widget_clasificacion)
            self.stacked_widget.setCurrentIndex(indice)
            
            # Crear controlador y guardarlo
            self.clasificacion_controller = ClasificacionController(widget_clasificacion, self)
            
            # Recargar brackets para asegurar que estén actualizados
            self.clasificacion_controller.cargar_brackets()
                                   
    def _cargar_equipos(self):
        """Carga la pantalla de gestión de equipos."""
        # Verificar si ya existe la pantalla
        if "equipos" in self.pantallas:
            # Ya existe, solo cambiar a ella
            self.stacked_widget.setCurrentWidget(self.pantallas["equipos"])
        else:
            # Crear la pantalla
            from Views.equipos_view import crear_vista_equipos
            from Controllers.equipos_controller import EquiposController
            
            vista_equipos = crear_vista_equipos()
            self.stacked_widget.addWidget(vista_equipos)
            self.stacked_widget.setCurrentWidget(vista_equipos)
            
            # Guardar referencia
            self.pantallas["equipos"] = vista_equipos
            
            # Inicializar controlador
            self.equipos_controller = EquiposController(vista_equipos, self)
            
    def _cargar_participantes(self):
        """Carga la pantalla de gestión de participantes."""
        # Verificar si ya existe la pantalla
        if "participantes" in self.pantallas:
            # Ya existe, solo cambiar a ella
            self.stacked_widget.setCurrentWidget(self.pantallas["participantes"])
        else:
            # Crear la pantalla
            from Views.participantes_view import crear_vista_participantes
            from Controllers.participantes_controller import ParticipantesController
            
            vista_participantes = crear_vista_participantes()
            self.stacked_widget.addWidget(vista_participantes)
            self.stacked_widget.setCurrentWidget(vista_participantes)
            
            # Guardar referencia
            self.pantallas["participantes"] = vista_participantes
            
            # Inicializar controlador
            self.participantes_controller = ParticipantesController(vista_participantes, self)
            
    def volver_a_principal(self):
        """Vuelve a la pantalla principal."""
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(0)
            
    def abrir_nuevo_torneo(self):
        """Abre el diálogo para crear un nuevo torneo."""
        # Verificar que no haya torneo activo
        torneo_activo = self.db.torneo_activo_existe()
        
        if torneo_activo:
            QMessageBox.warning(
                self.main_window,
                "Torneo Activo",
                f"Ya existe un torneo activo: {torneo_activo['nombre']}\n\n"
                "Debes finalizarlo antes de crear uno nuevo."
            )
            return
            
        # Verificar que haya equipos registrados
        equipos = self.db.obtener_todos_equipos()
        
        if len(equipos) < 8:
            QMessageBox.warning(
                self.main_window,
                "Equipos Insuficientes",
                f"Necesitas al menos 8 equipos registrados.\n"
                f"Actualmente hay {len(equipos)} equipo(s)."
            )
            return
            
        # Abrir diálogo de nuevo torneo
        try:
            # Cargar el diálogo desde el archivo .ui
            ui_file_path = obtener_ruta_recurso("Views/nuevo_torneo.ui")
            ui_file = QFile(ui_file_path)
            if not ui_file.open(QFile.ReadOnly):
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "No se pudo abrir el archivo de interfaz nuevo_torneo.ui"
                )
                return
                
            loader = QUiLoader()
            dialog = loader.load(ui_file, self.main_window)
            ui_file.close()
            
            # Crear controlador del diálogo
            controller = NuevoTorneoController(dialog, self)
            
            # Mostrar diálogo
            resultado = dialog.exec()
            
            # Si se creó el torneo exitosamente, actualizar interfaz
            if resultado == QDialog.Accepted:
                QMessageBox.information(
                    self.main_window,
                    "Torneo Creado",
                    "El torneo se ha creado exitosamente.\n"
                    "Ahora puedes asignar fechas a los partidos desde el Calendario."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Error al abrir el diálogo de nuevo torneo:\n{str(e)}"
            )
        
    def finalizar_torneo(self):
        """Finaliza el torneo activo con confirmación."""
        torneo_activo = self.db.torneo_activo_existe()
        
        if not torneo_activo:
            QMessageBox.information(
                self.main_window,
                "Sin Torneo Activo",
                "No hay ningún torneo activo en este momento."
            )
            return
            
        # Pedir confirmación
        respuesta = QMessageBox.question(
            self.main_window,
            "Confirmar Finalización",
            f"¿Estás seguro de que quieres finalizar el torneo '{torneo_activo['nombre']}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            # Finalizar el torneo
            self.torneo_logic.finalizar_torneo_manual(torneo_activo['id'])
            
            # Ocultar botón de finalizar
            btn_finalizar = self.main_window.findChild(object, "btnFinalizarTorneo")
            if btn_finalizar:
                btn_finalizar.setVisible(False)
                
            QMessageBox.information(
                self.main_window,
                "Torneo Finalizado",
                f"El torneo '{torneo_activo['nombre']}' ha sido finalizado correctamente."
            )
            
    def mostrar_ayuda(self):
        """Muestra el diálogo de ayuda (onboarding)."""
        from Controllers.onboarding_controller import OnboardingController
        
        # Cargar el diálogo de onboarding
        loader = QUiLoader()
        ui_file = QFile(obtener_ruta_recurso("Views/onboarding.ui"))
        
        if ui_file.open(QFile.ReadOnly):
            dialog = loader.load(ui_file, self.main_window)
            ui_file.close()
            
            # Crear controlador del onboarding
            onboarding_ctrl = OnboardingController(dialog)
            
            # Mostrar el diálogo
            dialog.exec()
        else:
            QMessageBox.warning(
                self.main_window,
                "Error",
                "No se pudo cargar el diálogo de ayuda."
            )
            
    def mostrar_creditos(self):
        """Muestra el diálogo de créditos."""
        QMessageBox.about(
            self.main_window,
            "Créditos",
            "<h2>Gestión de Torneos de Fútbol</h2>"
            "<p><b>Desarrollado por:</b> Víctor Rivera Puebla</p>"
            "<p><b>Versión:</b> 1.0</p>"
            "<p><b>Curso:</b> 2º DAM - 2026</p>"
            "<br>"
            "<p>Aplicación desarrollada con PySide6 y SQLite</p>"
        )
        
    def abrir_reloj(self):
        """Abre el diálogo del reloj digital o lo trae al frente."""
        if self._clock_dialog is None:
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle("Reloj / Cronómetro")
            dialog.setModal(False)
            dialog.setAttribute(Qt.WA_DeleteOnClose, True)
            dialog.setSizeGripEnabled(True)
            dialog.resize(440, 300)

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(16, 16, 16, 16)

            reloj = RelojDigital(dialog)
            layout.addWidget(reloj)

            reloj.timerFinished.connect(self._mostrar_fin_tiempo_partido)
            reloj.alarmTriggered.connect(self._mostrar_alarma_configurada)
            dialog.finished.connect(self._handle_clock_dialog_closed)

            self._clock_dialog = dialog
            self._clock_widget = reloj
            self._configurar_reloj_para_partido()
        else:
            dialog = self._clock_dialog

        self._propagar_idioma_reloj()
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _configurar_reloj_para_partido(self) -> None:
        """Configura el reloj reutilizable utilizando solo su API pública."""
        if not self._clock_widget:
            return

        reloj = self._clock_widget
        reloj.is24Hour = True
        reloj.timerDuration = 45 * 60  # 45 minutos por parte
        reloj.timerBehavior = "countdown"
        reloj.mode = "timer"
        reloj.reset()
        reloj.alarmEnabled = True
        reloj.alarmMessage = self.main_window.tr("Alarma del partido")
        reloj.setLanguage(self._current_language)

    def establecer_idioma(self, language_code: str) -> None:
        """Actualiza el idioma activo y sincroniza el reloj si está abierto."""
        normalized = (language_code or "es").lower()
        self._current_language = "es" if normalized.startswith("es") else "en"
        self._propagar_idioma_reloj()
        
        # Propagar idioma al controlador de resultados si existe
        if hasattr(self, 'resultados_controller') and self.resultados_controller:
            self.resultados_controller.establecer_idioma(self._current_language)

    def _propagar_idioma_reloj(self) -> None:
        if self._clock_widget:
            self._clock_widget.setLanguage(self._current_language)

    def _handle_clock_dialog_closed(self, _result: int) -> None:
        """Libera referencias cuando se cierra el diálogo."""
        self._clock_dialog = None
        self._clock_widget = None

    def _mostrar_fin_tiempo_partido(self) -> None:
        QMessageBox.information(
            self.main_window,
            "Partido",
            "Fin del tiempo del partido",
        )

    def _mostrar_alarma_configurada(self, mensaje: str) -> None:
        QMessageBox.information(
            self.main_window,
            "Alarma",
            mensaje,
        )

    def obtener_main_window(self):
        """Retorna la ventana principal."""
        return self.main_window
