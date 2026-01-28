"""
Controlador para la gestión de resultados de partidos.
Maneja el registro de goles, tarjetas y actualización de resultados.
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QListWidget, QListWidgetItem,
                               QTableWidget, QTableWidgetItem, QLabel, QSpinBox,
                               QCheckBox, QMessageBox, QComboBox, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QBrush, QColor
from datetime import datetime
import os

from Models.database import DatabaseManager


class ResultadosController:
    """Controlador para la pantalla de gestión de resultados."""
    
    def __init__(self, widget: QWidget, main_controller):
        """
        Inicializa el controlador de resultados.
        
        Args:
            widget: Widget de la vista de resultados
            main_controller: Controlador principal para navegación
        """
        self.widget = widget
        self.main_controller = main_controller
        self.db = DatabaseManager()
        
        self.partido_actual = None
        self.equipo_a_id = None
        self.equipo_b_id = None
        self.jugadores_equipo_a = []
        self.jugadores_equipo_b = []
        self.estado_partido_actual = None
        
        # Obtener widgets
        self._obtener_widgets()
        
        # Ejecutar migraciones si es necesario
        try:
            self.db.migrar_estados_partidos()
            self.db.migrar_partidos_nullable_equipos()
        except:
            pass  # Si falla, continuar normalmente
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar partidos
        self.cargar_partidos()
        
    def _obtener_widgets(self):
        """Obtiene referencias a los widgets de la UI."""
        self.list_partidos = self.widget.findChild(QListWidget, "listPartidos")
        self.combo_filtro_estado = self.widget.findChild(QComboBox, "comboFiltroEstado")
        self.lbl_resumen = self.widget.findChild(QLabel, "lblResumen")
        self.lbl_partido_seleccionado = self.widget.findChild(QLabel, "lblPartidoSeleccionado")
        self.lbl_nombre_equipo_a = self.widget.findChild(QLabel, "lblNombreEquipoA")
        self.lbl_nombre_equipo_b = self.widget.findChild(QLabel, "lblNombreEquipoB")
        self.table_jugadores_a = self.widget.findChild(QTableWidget, "tableJugadoresA")
        self.table_jugadores_b = self.widget.findChild(QTableWidget, "tableJugadoresB")
        self.spin_total_goles_a = self.widget.findChild(QSpinBox, "spinTotalGolesA")
        self.spin_total_goles_b = self.widget.findChild(QSpinBox, "spinTotalGolesB")
        self.btn_registrar = self.widget.findChild(QPushButton, "btnRegistrarResultado")
        self.btn_limpiar = self.widget.findChild(QPushButton, "btnLimpiar")
        self.btn_volver = self.widget.findChild(QPushButton, "btnVolver")
        self.btn_iniciar = self.widget.findChild(QPushButton, "btnIniciarPartido")
        self.btn_finalizar = self.widget.findChild(QPushButton, "btnFinalizarPartido")
        self.btn_cancelar = self.widget.findChild(QPushButton, "btnCancelarPartido")
        self.btn_reabrir = self.widget.findChild(QPushButton, "btnReabrirPartido")
        self.reloj_partido = self.widget.findChild(QWidget, "relojPartido")
        
        # Configurar el reloj para partidos
        if self.reloj_partido:
            self._configurar_reloj()
            
    def _configurar_reloj(self):
        """Configura el reloj para el modo de partido."""
        if not self.reloj_partido:
            return
            
        # Configurar propiedades del reloj usando su API publica
        self.reloj_partido.mode = "timer"
        self.reloj_partido.timerBehavior = "countdown"
        self.reloj_partido.timerDuration = 45 * 60  # 45 minutos en segundos
        self.reloj_partido.is24Hour = True
        self.reloj_partido.alarmEnabled = True
        self.reloj_partido.alarmMessage = "Fin del tiempo del partido"
        
        # Conectar senales
        try:
            self.reloj_partido.timerFinished.connect(self._mostrar_fin_tiempo_partido)
        except Exception as e:
            print(f"Error conectando senal timerFinished: {e}")
            
    def _mostrar_fin_tiempo_partido(self):
        """Muestra un mensaje cuando el tiempo del partido termina."""
        QMessageBox.information(
            self.widget,
            "Fin del tiempo",
            "El tiempo del partido ha finalizado.\\n\\nRecuerda registrar el resultado final."
        )
        
    def _conectar_senales(self):
        """Conecta las señales de los widgets."""
        if self.list_partidos:
            self.list_partidos.itemClicked.connect(self.cargar_partido)
        if self.combo_filtro_estado:
            self.combo_filtro_estado.currentIndexChanged.connect(self.filtrar_partidos)
        if self.btn_registrar:
            self.btn_registrar.clicked.connect(self.registrar_resultado)
        if self.btn_limpiar:
            self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.main_controller.volver_a_principal)
        if self.btn_iniciar:
            self.btn_iniciar.clicked.connect(self.iniciar_partido)
        if self.btn_finalizar:
            self.btn_finalizar.clicked.connect(self.finalizar_partido)
        if self.btn_cancelar:
            self.btn_cancelar.clicked.connect(self.cancelar_partido)
        if self.btn_reabrir:
            self.btn_reabrir.clicked.connect(self.reabrir_partido)
            
    def cargar_partidos(self, filtro_estado=None):
        """
        Carga todos los partidos en la lista.
        
        Args:
            filtro_estado: Estado por el cual filtrar ('pendiente', 'en_curso', 'finalizado', 'cancelado', None para todos)
        """
        if not self.list_partidos:
            return
            
        self.list_partidos.clear()
        
        # Verificar si hay torneo activo
        torneo = self.db.torneo_activo_existe()
        if not torneo:
            return
            
        # Obtener partidos del torneo
        partidos = self.db.obtener_partidos_por_torneo(torneo['id'])
        
        # Aplicar filtro
        if filtro_estado and filtro_estado != 'todos':
            partidos = [p for p in partidos if p.get('estado', 'pendiente') == filtro_estado]
        
        for partido in partidos:
            # Formatear fecha
            try:
                if partido['fecha']:
                    fecha_obj = datetime.strptime(partido['fecha'], "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                else:
                    fecha_formateada = "Por definir"
            except:
                fecha_formateada = partido['fecha'] if partido['fecha'] else "Por definir"
                
            # Formatear VS con equipos pendientes
            equipo_a_nombre = partido['equipo_a_nombre'] if partido['equipo_a_nombre'] else "Por definir"
            equipo_b_nombre = partido['equipo_b_nombre'] if partido['equipo_b_nombre'] else "Por definir"
            vs_texto = f"{equipo_a_nombre} VS {equipo_b_nombre}"
            
            # Obtener estado y configurar color de fondo
            estado = partido.get('estado', 'pendiente')
            
            if estado == 'pendiente':
                color_fondo = QColor(245, 245, 245)  # Gris claro
                estado_icono = "⏳"
                estado_texto = ""
            elif estado == 'en_curso':
                color_fondo = QColor(255, 224, 178)  # Naranja claro
                estado_icono = "⚽"
                estado_texto = "[EN CURSO]"
            elif estado == 'finalizado':
                color_fondo = QColor(200, 230, 201)  # Verde claro
                estado_icono = "✓"
                # Obtener resultado
                resultado = self.db.obtener_resultado_partido(partido['id'])
                if resultado:
                    estado_texto = f"[{resultado['goles_equipo_a']} - {resultado['goles_equipo_b']}]"
                else:
                    estado_texto = "[FINALIZADO]"
            elif estado == 'cancelado':
                color_fondo = QColor(255, 205, 210)  # Rojo claro
                estado_icono = "✗"
                estado_texto = "[CANCELADO]"
            else:
                color_fondo = QColor(245, 245, 245)  # Gris claro
                estado_texto = ""
                
            texto = f"{fecha_formateada} - {vs_texto}\n{partido['ronda']} {estado_icono} {estado_texto}"
            
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, partido['id'])
            item.setBackground(QBrush(color_fondo))
            
            # Color de texto negro
            item.setForeground(QBrush(QColor(0, 0, 0)))
            
            # Añadir icono del equipo A si existe
            if partido.get('equipo_a_escudo') and os.path.exists(partido['equipo_a_escudo']):
                icon = QIcon(partido['equipo_a_escudo'])
                item.setIcon(icon)
                
            self.list_partidos.addItem(item)
            
    def filtrar_partidos(self):
        """Filtra los partidos según el combo seleccionado."""
        if not self.combo_filtro_estado:
            return
            
        filtro = self.combo_filtro_estado.currentData()
        self.cargar_partidos(filtro_estado=filtro)
            
    def cargar_partido(self, item: QListWidgetItem):
        """
        Carga los jugadores de ambos equipos del partido seleccionado.
        
        Args:
            item: Item seleccionado de la lista
        """
        print("=== DEBUG: cargar_partido() ejecutado ===")
        partido_id = item.data(Qt.UserRole)
        print(f"DEBUG: partido_id = {partido_id}")
        if not partido_id:
            print("DEBUG: partido_id es None, saliendo...")
            return
            
        # Obtener información del partido
        partido = self.db.obtener_partido_por_id(partido_id)
        if not partido:
            return
            
        # Verificar si los equipos están definidos
        if not partido['equipo_a_id'] or not partido['equipo_b_id']:
            QMessageBox.information(
                self.widget,
                "Partido Pendiente",
                f"Este partido de {partido['ronda']} aún no tiene equipos definidos.\n"
                f"Los equipos se asignarán automáticamente cuando se completen los partidos de la ronda anterior."
            )
            return
            
        self.partido_actual = partido_id
        self.equipo_a_id = partido['equipo_a_id']
        self.equipo_b_id = partido['equipo_b_id']
        self.estado_partido_actual = partido.get('estado', 'pendiente')
        
        # Actualizar etiquetas
        if self.lbl_partido_seleccionado:
            vs_texto = f"{partido['equipo_a_nombre']} vs {partido['equipo_b_nombre']} - {partido['ronda']}"
            self.lbl_partido_seleccionado.setText(vs_texto)
            
        if self.lbl_nombre_equipo_a:
            self.lbl_nombre_equipo_a.setText(partido['equipo_a_nombre'])
            
        if self.lbl_nombre_equipo_b:
            self.lbl_nombre_equipo_b.setText(partido['equipo_b_nombre'])
            
        # Cargar jugadores
        self.jugadores_equipo_a = self.db.obtener_jugadores_por_equipo(self.equipo_a_id)
        self.jugadores_equipo_b = self.db.obtener_jugadores_por_equipo(self.equipo_b_id)
        
        print(f"DEBUG: Jugadores equipo A: {len(self.jugadores_equipo_a)}")
        print(f"DEBUG: Jugadores equipo B: {len(self.jugadores_equipo_b)}")
        
        # Mostrar jugadores en las tablas
        self._mostrar_jugadores_equipo_a()
        self._mostrar_jugadores_equipo_b()
        
        # Cargar datos existentes si hay resultado registrado
        resultado = self.db.obtener_resultado_partido(partido_id)
        if resultado:
            self._cargar_eventos_existentes(partido_id)
            
        # Actualizar resumen
        self._actualizar_resumen()
        
        # Actualizar estado de los botones según el estado del partido
        self._actualizar_botones_segun_estado()
        
    def _mostrar_jugadores_equipo_a(self):
        """Muestra los jugadores del equipo A en la tabla."""
        print("DEBUG: _mostrar_jugadores_equipo_a() ejecutado")
        if not self.table_jugadores_a:
            print("DEBUG: self.table_jugadores_a es None!")
            return
            
        self.table_jugadores_a.setRowCount(0)
        self.table_jugadores_a.setRowCount(len(self.jugadores_equipo_a))
        print(f"DEBUG: Tabla A configurada con {len(self.jugadores_equipo_a)} filas")
        
        for fila, jugador in enumerate(self.jugadores_equipo_a):
            # Columna 0: Nombre del jugador
            item_nombre = QTableWidgetItem(jugador['nombre'])
            item_nombre.setForeground(QColor(0, 0, 0))  # Negro
            item_nombre.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)  # No editable
            self.table_jugadores_a.setItem(fila, 0, item_nombre)
            
            # Columna 1: SpinBox para goles
            spin_goles = QSpinBox()
            spin_goles.setMinimum(0)
            spin_goles.setMaximum(20)
            spin_goles.setValue(0)
            spin_goles.setStyleSheet("color: black; background-color: white;")
            spin_goles.valueChanged.connect(self._actualizar_total_goles_a)
            # Guardar referencia del jugador_id en el widget
            spin_goles.setProperty("jugador_id", jugador['id'])
            self.table_jugadores_a.setCellWidget(fila, 1, spin_goles)
            
            # Columna 2: CheckBox para tarjetas amarillas
            check_amarilla = QCheckBox()
            check_amarilla.setStyleSheet("QCheckBox { background-color: transparent; }")
            check_amarilla.setProperty("jugador_id", jugador['id'])
            # Centrar el checkbox
            container_amarilla = QWidget()
            layout_amarilla = QHBoxLayout(container_amarilla)
            layout_amarilla.addWidget(check_amarilla)
            layout_amarilla.setAlignment(Qt.AlignCenter)
            layout_amarilla.setContentsMargins(0, 0, 0, 0)
            self.table_jugadores_a.setCellWidget(fila, 2, container_amarilla)
            
            # Columna 3: CheckBox para tarjetas rojas
            check_roja = QCheckBox()
            check_roja.setStyleSheet("QCheckBox { background-color: transparent; }")
            check_roja.setProperty("jugador_id", jugador['id'])
            # Centrar el checkbox
            container_roja = QWidget()
            layout_roja = QHBoxLayout(container_roja)
            layout_roja.addWidget(check_roja)
            layout_roja.setAlignment(Qt.AlignCenter)
            layout_roja.setContentsMargins(0, 0, 0, 0)
            self.table_jugadores_a.setCellWidget(fila, 3, container_roja)
            
    def _mostrar_jugadores_equipo_b(self):
        """Muestra los jugadores del equipo B en la tabla."""
        if not self.table_jugadores_b:
            return
            
        self.table_jugadores_b.setRowCount(0)
        self.table_jugadores_b.setRowCount(len(self.jugadores_equipo_b))
        
        for fila, jugador in enumerate(self.jugadores_equipo_b):
            # Columna 0: Nombre del jugador
            item_nombre = QTableWidgetItem(jugador['nombre'])
            item_nombre.setForeground(QColor(0, 0, 0))  # Negro
            item_nombre.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)  # No editable
            self.table_jugadores_b.setItem(fila, 0, item_nombre)
            
            # Columna 1: SpinBox para goles
            spin_goles = QSpinBox()
            spin_goles.setMinimum(0)
            spin_goles.setMaximum(20)
            spin_goles.setValue(0)
            spin_goles.setStyleSheet("color: black; background-color: white;")
            spin_goles.valueChanged.connect(self._actualizar_total_goles_b)
            # Guardar referencia del jugador_id en el widget
            spin_goles.setProperty("jugador_id", jugador['id'])
            self.table_jugadores_b.setCellWidget(fila, 1, spin_goles)
            
            # Columna 2: CheckBox para tarjetas amarillas
            check_amarilla = QCheckBox()
            check_amarilla.setStyleSheet("QCheckBox { background-color: transparent; }")
            check_amarilla.setProperty("jugador_id", jugador['id'])
            # Centrar el checkbox
            container_amarilla = QWidget()
            layout_amarilla = QHBoxLayout(container_amarilla)
            layout_amarilla.addWidget(check_amarilla)
            layout_amarilla.setAlignment(Qt.AlignCenter)
            layout_amarilla.setContentsMargins(0, 0, 0, 0)
            self.table_jugadores_b.setCellWidget(fila, 2, container_amarilla)
            
            # Columna 3: CheckBox para tarjetas rojas
            check_roja = QCheckBox()
            check_roja.setStyleSheet("QCheckBox { background-color: transparent; }")
            check_roja.setProperty("jugador_id", jugador['id'])
            # Centrar el checkbox
            container_roja = QWidget()
            layout_roja = QHBoxLayout(container_roja)
            layout_roja.addWidget(check_roja)
            layout_roja.setAlignment(Qt.AlignCenter)
            layout_roja.setContentsMargins(0, 0, 0, 0)
            self.table_jugadores_b.setCellWidget(fila, 3, container_roja)
            
    def _cargar_eventos_existentes(self, partido_id):
        """Carga los eventos existentes del partido en las tablas."""
        eventos = self.db.obtener_eventos_partido(partido_id)
        
        for evento in eventos:
            jugador_id = evento['jugador_id']
            tipo_evento = evento['tipo_evento']
            
            # Buscar en tabla equipo A
            for fila in range(self.table_jugadores_a.rowCount()):
                spin = self.table_jugadores_a.cellWidget(fila, 1)
                if spin and spin.property("jugador_id") == jugador_id:
                    if tipo_evento == 'gol':
                        spin.setValue(spin.value() + 1)
                    elif tipo_evento == 'tarjeta_amarilla':
                        container = self.table_jugadores_a.cellWidget(fila, 2)
                        if container:
                            check = container.layout().itemAt(0).widget()
                            check.setChecked(True)
                    elif tipo_evento == 'tarjeta_roja':
                        container = self.table_jugadores_a.cellWidget(fila, 3)
                        if container:
                            check = container.layout().itemAt(0).widget()
                            check.setChecked(True)
                            
            # Buscar en tabla equipo B
            for fila in range(self.table_jugadores_b.rowCount()):
                spin = self.table_jugadores_b.cellWidget(fila, 1)
                if spin and spin.property("jugador_id") == jugador_id:
                    if tipo_evento == 'gol':
                        spin.setValue(spin.value() + 1)
                    elif tipo_evento == 'tarjeta_amarilla':
                        container = self.table_jugadores_b.cellWidget(fila, 2)
                        if container:
                            check = container.layout().itemAt(0).widget()
                            check.setChecked(True)
                    elif tipo_evento == 'tarjeta_roja':
                        container = self.table_jugadores_b.cellWidget(fila, 3)
                        if container:
                            check = container.layout().itemAt(0).widget()
                            check.setChecked(True)
            
    def _actualizar_total_goles_a(self):
        """Actualiza el total de goles del equipo A."""
        if not self.table_jugadores_a or not self.spin_total_goles_a:
            return
            
        total = 0
        for fila in range(self.table_jugadores_a.rowCount()):
            spin = self.table_jugadores_a.cellWidget(fila, 1)
            if spin:
                total += spin.value()
                
        self.spin_total_goles_a.setValue(total)
            
    def _actualizar_total_goles_b(self):
        """Actualiza el total de goles del equipo B."""
        if not self.table_jugadores_b or not self.spin_total_goles_b:
            return
            
        total = 0
        for fila in range(self.table_jugadores_b.rowCount()):
            spin = self.table_jugadores_b.cellWidget(fila, 1)
            if spin:
                total += spin.value()
                
        self.spin_total_goles_b.setValue(total)
            
    def registrar_resultado(self):
        """Registra el resultado del partido y los eventos."""
        if not self.partido_actual:
            QMessageBox.warning(self.widget, "Error", "Debes seleccionar un partido.")
            return
            
        # Validar que el partido no esté finalizado
        if self.estado_partido_actual == 'finalizado':
            QMessageBox.warning(
                self.widget,
                "Partido Finalizado",
                "Este partido ya está finalizado. Si deseas modificar el resultado, primero debes reabrirlo."
            )
            return
            
        # Validar que el partido no esté cancelado
        if self.estado_partido_actual == 'cancelado':
            QMessageBox.warning(
                self.widget,
                "Partido Cancelado",
                "No se puede registrar resultado en un partido cancelado."
            )
            return
        
        # Obtener totales de goles
        goles_a = self.spin_total_goles_a.value() if self.spin_total_goles_a else 0
        goles_b = self.spin_total_goles_b.value() if self.spin_total_goles_b else 0
        
        # Validar que no haya empate
        if goles_a == goles_b:
            QMessageBox.warning(
                self.widget,
                "Empate No Permitido",
                "El torneo no permite empates. Debe haber un ganador.\nPor favor, ajusta los goles."
            )
            return
        
        # Determinar ganador
        ganador_id = self.equipo_a_id if goles_a > goles_b else self.equipo_b_id
        
        # Confirmar registro
        respuesta = QMessageBox.question(
            self.widget,
            "Confirmar Registro",
            f"¿Estás seguro de registrar el resultado?\n\n"
            f"{self.lbl_nombre_equipo_a.text()}: {goles_a} goles\n"
            f"{self.lbl_nombre_equipo_b.text()}: {goles_b} goles\n\n"
            f"El partido se marcará como FINALIZADO.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta != QMessageBox.Yes:
            return
        
        try:
            # 1. Guardar resultado del partido
            self.db.registrar_resultado(
                self.partido_actual,
                goles_a,
                goles_b,
                ganador_id
            )
            
            # 2. Eliminar eventos anteriores
            self.db.eliminar_eventos_partido(self.partido_actual)
            
            # 3. Guardar eventos del equipo A
            for fila in range(self.table_jugadores_a.rowCount()):
                spin_goles = self.table_jugadores_a.cellWidget(fila, 1)
                container_amarilla = self.table_jugadores_a.cellWidget(fila, 2)
                container_roja = self.table_jugadores_a.cellWidget(fila, 3)
                
                if spin_goles:
                    jugador_id = spin_goles.property("jugador_id")
                    goles = spin_goles.value()
                    
                    # Registrar goles
                    for _ in range(goles):
                        self.db.registrar_evento(self.partido_actual, jugador_id, 'gol')
                    
                    # Registrar tarjetas amarillas
                    if container_amarilla:
                        check = container_amarilla.layout().itemAt(0).widget()
                        if check.isChecked():
                            self.db.registrar_evento(self.partido_actual, jugador_id, 'tarjeta_amarilla')
                    
                    # Registrar tarjetas rojas
                    if container_roja:
                        check = container_roja.layout().itemAt(0).widget()
                        if check.isChecked():
                            self.db.registrar_evento(self.partido_actual, jugador_id, 'tarjeta_roja')
            
            # 4. Guardar eventos del equipo B
            for fila in range(self.table_jugadores_b.rowCount()):
                spin_goles = self.table_jugadores_b.cellWidget(fila, 1)
                container_amarilla = self.table_jugadores_b.cellWidget(fila, 2)
                container_roja = self.table_jugadores_b.cellWidget(fila, 3)
                
                if spin_goles:
                    jugador_id = spin_goles.property("jugador_id")
                    goles = spin_goles.value()
                    
                    # Registrar goles
                    for _ in range(goles):
                        self.db.registrar_evento(self.partido_actual, jugador_id, 'gol')
                    
                    # Registrar tarjetas amarillas
                    if container_amarilla:
                        check = container_amarilla.layout().itemAt(0).widget()
                        if check.isChecked():
                            self.db.registrar_evento(self.partido_actual, jugador_id, 'tarjeta_amarilla')
                    
                    # Registrar tarjetas rojas
                    if container_roja:
                        check = container_roja.layout().itemAt(0).widget()
                        if check.isChecked():
                            self.db.registrar_evento(self.partido_actual, jugador_id, 'tarjeta_roja')
            
            # 5. Actualizar estadísticas de jugadores
            self.db.actualizar_estadisticas_jugadores_desde_eventos()
            
            # 6. El estado ya fue cambiado a 'finalizado' por registrar_resultado
            self.estado_partido_actual = 'finalizado'
            
            # 7. Mostrar mensaje de éxito
            QMessageBox.information(
                self.widget,
                "Éxito",
                f"Resultado registrado correctamente.\n\n"
                f"Ganador: {self.lbl_nombre_equipo_a.text() if ganador_id == self.equipo_a_id else self.lbl_nombre_equipo_b.text()}\n"
                f"Resultado: {goles_a} - {goles_b}"
            )
            
            # 8. Recargar lista de partidos
            self.cargar_partidos()
            
            # 9. Actualizar resumen
            self._actualizar_resumen()
            
            # 10. Actualizar botones
            self._actualizar_botones_segun_estado()
            
            # 11. Actualizar brackets en clasificación (con pequeño delay para evitar lock)
            if hasattr(self.main_controller, 'clasificacion_controller') and self.main_controller.clasificacion_controller:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(100, self.main_controller.clasificacion_controller.cargar_brackets)
            
        except Exception as e:
            QMessageBox.critical(
                self.widget,
                "Error",
                f"Error al registrar resultado: {str(e)}"
            )
            
    def _actualizar_resumen(self):
        """Actualiza el resumen del partido en el panel izquierdo."""
        if not self.lbl_resumen or not self.partido_actual:
            return
            
        resultado = self.db.obtener_resultado_partido(self.partido_actual)
        
        if resultado:
            # Obtener nombres de equipos
            equipo_a = self.lbl_nombre_equipo_a.text() if self.lbl_nombre_equipo_a else "Equipo A"
            equipo_b = self.lbl_nombre_equipo_b.text() if self.lbl_nombre_equipo_b else "Equipo B"
            
            # Obtener información del partido para el ganador_id
            partido = self.db.obtener_partido_por_id(self.partido_actual)
            
            # Determinar ganador
            if partido and partido.get('ganador_id'):
                if partido['ganador_id'] == self.equipo_a_id:
                    ganador = equipo_a
                else:
                    ganador = equipo_b
            else:
                # Si no hay ganador definido, usar los goles
                if resultado['goles_equipo_a'] > resultado['goles_equipo_b']:
                    ganador = equipo_a
                else:
                    ganador = equipo_b
                
            resumen = f"🏆 Resultado Final 🏆\n\n"
            resumen += f"{equipo_a}: {resultado['goles_equipo_a']} goles\n"
            resumen += f"{equipo_b}: {resultado['goles_equipo_b']} goles\n\n"
            resumen += f"Ganador: {ganador}"
            
            self.lbl_resumen.setText(resumen)
        else:
            self.lbl_resumen.setText("Sin resultado registrado")
            
    def _actualizar_botones_segun_estado(self):
        """Actualiza la visibilidad y estado de los botones según el estado del partido."""
        if not self.partido_actual:
            # Sin partido seleccionado, deshabilitar todo
            if self.btn_iniciar:
                self.btn_iniciar.setEnabled(False)
            if self.btn_finalizar:
                self.btn_finalizar.setEnabled(False)
            if self.btn_cancelar:
                self.btn_cancelar.setEnabled(False)
            if self.btn_reabrir:
                self.btn_reabrir.setEnabled(False)
            if self.btn_registrar:
                self.btn_registrar.setEnabled(False)
            if self.table_jugadores_a:
                self.table_jugadores_a.setEnabled(False)
            if self.table_jugadores_b:
                self.table_jugadores_b.setEnabled(False)
            return
            
        # Habilitar tablas por defecto
        if self.table_jugadores_a:
            self.table_jugadores_a.setEnabled(True)
        if self.table_jugadores_b:
            self.table_jugadores_b.setEnabled(True)
            
        # Configurar botones según estado
        if self.estado_partido_actual == 'pendiente':
            if self.btn_iniciar:
                self.btn_iniciar.setEnabled(True)
            if self.btn_finalizar:
                self.btn_finalizar.setEnabled(False)
            if self.btn_cancelar:
                self.btn_cancelar.setEnabled(True)
            if self.btn_reabrir:
                self.btn_reabrir.setEnabled(False)
            if self.btn_registrar:
                self.btn_registrar.setEnabled(True)
                
        elif self.estado_partido_actual == 'en_curso':
            if self.btn_iniciar:
                self.btn_iniciar.setEnabled(False)
            if self.btn_finalizar:
                self.btn_finalizar.setEnabled(True)
            if self.btn_cancelar:
                self.btn_cancelar.setEnabled(True)
            if self.btn_reabrir:
                self.btn_reabrir.setEnabled(False)
            if self.btn_registrar:
                self.btn_registrar.setEnabled(True)
                
        elif self.estado_partido_actual == 'finalizado':
            if self.btn_iniciar:
                self.btn_iniciar.setEnabled(False)
            if self.btn_finalizar:
                self.btn_finalizar.setEnabled(False)
            if self.btn_cancelar:
                self.btn_cancelar.setEnabled(False)
            if self.btn_reabrir:
                self.btn_reabrir.setEnabled(True)
            if self.btn_registrar:
                self.btn_registrar.setEnabled(False)
            # Bloquear tablas
            if self.table_jugadores_a:
                self.table_jugadores_a.setEnabled(False)
            if self.table_jugadores_b:
                self.table_jugadores_b.setEnabled(False)
                
        elif self.estado_partido_actual == 'cancelado':
            if self.btn_iniciar:
                self.btn_iniciar.setEnabled(False)
            if self.btn_finalizar:
                self.btn_finalizar.setEnabled(False)
            if self.btn_cancelar:
                self.btn_cancelar.setEnabled(False)
            if self.btn_reabrir:
                self.btn_reabrir.setEnabled(True)
            if self.btn_registrar:
                self.btn_registrar.setEnabled(False)
            # Bloquear tablas
            if self.table_jugadores_a:
                self.table_jugadores_a.setEnabled(False)
            if self.table_jugadores_b:
                self.table_jugadores_b.setEnabled(False)
                
    def iniciar_partido(self):
        """Cambia el estado del partido a 'en_curso' e inicia el reloj."""
        if not self.partido_actual:
            return
            
        try:
            respuesta = QMessageBox.question(
                self.widget,
                "Iniciar Partido",
                "¿Estás seguro de que quieres iniciar este partido?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                if self.db.actualizar_estado_partido(self.partido_actual, 'en_curso'):
                    self.estado_partido_actual = 'en_curso'
                    self._actualizar_botones_segun_estado()
                    
                    # Iniciar el reloj automáticamente
                    if self.reloj_partido:
                        self.reloj_partido.reset()
                        self.reloj_partido.start()
                    
                    QMessageBox.information(self.widget, "Éxito", "Partido iniciado correctamente.")
                else:
                    QMessageBox.critical(self.widget, "Error", "No se pudo iniciar el partido.")
        except Exception as e:
            print(f"Error en iniciar_partido: {e}")
            QMessageBox.critical(self.widget, "Error", f"Error al iniciar partido: {str(e)}")
                
    def finalizar_partido(self):
        """Cambia el estado del partido a 'finalizado' si tiene resultado."""
        if not self.partido_actual:
            return
            
        # Verificar que el partido tenga resultado
        resultado = self.db.obtener_resultado_partido(self.partido_actual)
        if not resultado:
            QMessageBox.warning(
                self.widget,
                "Sin Resultado",
                "Debes registrar el resultado del partido antes de finalizarlo.\nUsa el botón 'REGISTRAR RESULTADO'."
            )
            return
            
        respuesta = QMessageBox.question(
            self.widget,
            "Finalizar Partido",
            "¿Estás seguro de que quieres finalizar este partido?\nNo podrás modificar el resultado a menos que lo reabras.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            if self.db.actualizar_estado_partido(self.partido_actual, 'finalizado'):
                self.estado_partido_actual = 'finalizado'
                QMessageBox.information(self.widget, "Éxito", "Partido finalizado correctamente.")
                self.cargar_partidos()
                self._actualizar_botones_segun_estado()
                
                # Actualizar brackets en clasificación (con pequeño delay para evitar lock)
                if hasattr(self.main_controller, 'clasificacion_controller') and self.main_controller.clasificacion_controller:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(100, self.main_controller.clasificacion_controller.cargar_brackets)
            else:
                QMessageBox.critical(self.widget, "Error", "No se pudo finalizar el partido.")
                
    def cancelar_partido(self):
        """Cambia el estado del partido a 'cancelado'."""
        if not self.partido_actual:
            return
            
        respuesta = QMessageBox.question(
            self.widget,
            "Cancelar Partido",
            "¿Estás seguro de que quieres cancelar este partido?\nEsta acción marcará el partido como no jugado.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            if self.db.actualizar_estado_partido(self.partido_actual, 'cancelado'):
                self.estado_partido_actual = 'cancelado'
                QMessageBox.information(self.widget, "Éxito", "Partido cancelado correctamente.")
                # Solo actualizar botones, no recargar toda la lista
                self._actualizar_botones_segun_estado()
            else:
                QMessageBox.critical(self.widget, "Error", "No se pudo cancelar el partido.")
                
    def reabrir_partido(self):
        """Cambia el estado del partido de 'finalizado' o 'cancelado' a 'en_curso'."""
        if not self.partido_actual:
            return
            
        respuesta = QMessageBox.question(
            self.widget,
            "Reabrir Partido",
            "¿Estás seguro de que quieres reabrir este partido?\nPodrás modificar el resultado nuevamente.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            if self.db.actualizar_estado_partido(self.partido_actual, 'en_curso'):
                self.estado_partido_actual = 'en_curso'
                QMessageBox.information(self.widget, "Éxito", "Partido reabierto correctamente.")
                self.cargar_partidos()
                self._actualizar_botones_segun_estado()
                # Recargar el partido para permitir edición
                item = self.list_partidos.currentItem()
                if item:
                    self.cargar_partido(item)
            else:
                QMessageBox.critical(self.widget, "Error", "No se pudo reabrir el partido.")
                
    def limpiar_formulario(self):
        """Limpia el formulario de registro de resultados."""
        self.partido_actual = None
        self.equipo_a_id = None
        self.equipo_b_id = None
        self.jugadores_equipo_a = []
        self.jugadores_equipo_b = []
        self.estado_partido_actual = None
        
        # Limpiar tablas
        if self.table_jugadores_a:
            self.table_jugadores_a.setRowCount(0)
        if self.table_jugadores_b:
            self.table_jugadores_b.setRowCount(0)
            
        # Limpiar etiquetas
        if self.lbl_partido_seleccionado:
            self.lbl_partido_seleccionado.setText("Selecciona un partido para registrar el resultado")
        if self.lbl_nombre_equipo_a:
            self.lbl_nombre_equipo_a.setText("")
        if self.lbl_nombre_equipo_b:
            self.lbl_nombre_equipo_b.setText("")
        if self.lbl_resumen:
            self.lbl_resumen.setText("")
            
        # Limpiar totales
        if self.spin_total_goles_a:
            self.spin_total_goles_a.setValue(0)
        if self.spin_total_goles_b:
            self.spin_total_goles_b.setValue(0)
            
        # Deseleccionar en la lista
        if self.list_partidos:
            self.list_partidos.clearSelection()
            
        # Actualizar botones
        self._actualizar_botones_segun_estado()
        
    def establecer_idioma(self, language_code: str):
        """Establece el idioma del reloj.
        
        Args:
            language_code: Código del idioma ('es' o 'en')
        """
        if self.reloj_partido and hasattr(self.reloj_partido, 'setLanguage'):
            self.reloj_partido.setLanguage(language_code)
            # Actualizar mensaje de alarma según idioma
            if language_code == 'es':
                self.reloj_partido.alarmMessage = "Fin del tiempo del partido"
            else:
                self.reloj_partido.alarmMessage = "Match time is up"
