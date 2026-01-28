"""
Controlador para la pantalla de calendario y gestión de partidos.
Gestiona la visualización del calendario y la programación de partidos.
"""

from PySide6.QtWidgets import (QMessageBox, QWidget, QPushButton, QComboBox,
                               QDateEdit, QTimeEdit, QTreeWidget, QTreeWidgetItem,
                               QHeaderView)
from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtGui import QIcon
from datetime import datetime
import os

from Models.database import DatabaseManager, obtener_ruta_recurso


class CalendarioController:
    """Controlador para gestión del calendario y partidos."""
    
    def __init__(self, widget: QWidget, main_controller, reloj_widget=None):
        """
        Inicializa el controlador.
        
        Args:
            widget: Widget de la vista de calendario
            main_controller: Controlador principal para navegación
            reloj_widget: Widget del reloj digital (opcional)
        """
        self.widget = widget
        self.main_controller = main_controller
        self.db = DatabaseManager()
        self.reloj = reloj_widget
        
        self.partido_editando = None  # ID del partido en edición
        
        # Obtener widgets
        self._obtener_widgets()
        
        # Conectar señales
        self._conectar_senales()
        
        # Conectar señales del reloj si está disponible
        if self.reloj:
            self._conectar_senales_reloj()
        
        # Cargar datos iniciales
        self.cargar_equipos()
        self.cargar_arbitros()
        self.cargar_partidos()
        
    def _obtener_widgets(self):
        """Obtiene referencias a los widgets de la UI."""
        self.combo_equipo_a = self.widget.findChild(QComboBox, "comboEquipoA")
        self.combo_equipo_b = self.widget.findChild(QComboBox, "comboEquipoB")
        self.date_fecha = self.widget.findChild(QDateEdit, "dateFecha")
        self.time_hora = self.widget.findChild(QTimeEdit, "timeHora")
        self.combo_arbitro = self.widget.findChild(QComboBox, "comboArbitro")
        self.combo_eliminatoria = self.widget.findChild(QComboBox, "comboEliminatoria")
        self.btn_guardar = self.widget.findChild(QPushButton, "btnGuardar")
        self.btn_limpiar = self.widget.findChild(QPushButton, "btnLimpiar")
        self.tree_partidos = self.widget.findChild(QTreeWidget, "treePartidos")
        self.btn_editar = self.widget.findChild(QPushButton, "btnEditar")
        self.btn_eliminar = self.widget.findChild(QPushButton, "btnEliminar")
        self.btn_volver = self.widget.findChild(QPushButton, "btnVolver")
        
    def _conectar_senales(self):
        """Conecta las señales de los widgets."""
        if self.btn_guardar:
            self.btn_guardar.clicked.connect(self.guardar_partido)
        if self.btn_limpiar:
            self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        if self.btn_editar:
            self.btn_editar.clicked.connect(self.editar_partido_seleccionado)
        if self.btn_eliminar:
            self.btn_eliminar.clicked.connect(self.eliminar_partido_seleccionado)
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.main_controller.volver_a_principal)
        if self.tree_partidos:
            self.tree_partidos.itemClicked.connect(self.cargar_partido_edicion)
    
    def _conectar_senales_reloj(self):
        """Conecta las señales del reloj digital."""
        if self.reloj:
            self.reloj.timerFinished.connect(self._manejar_temporizador_finalizado)
            self.reloj.alarmTriggered.connect(self._manejar_alarma_activada)
    
    def _manejar_temporizador_finalizado(self):
        """Muestra un mensaje cuando el temporizador finaliza."""
        QMessageBox.information(
            self.widget,
            "Temporizador",
            "El temporizador ha finalizado."
        )
    
    def _manejar_alarma_activada(self, mensaje: str):
        """Muestra un mensaje cuando se activa una alarma.
        
        Args:
            mensaje: Mensaje de la alarma configurado
        """
        QMessageBox.information(
            self.widget,
            "Alarma",
            mensaje
        )
            
    def cargar_equipos(self):
        """Carga los equipos en los combos."""
        if not self.combo_equipo_a or not self.combo_equipo_b:
            return
            
        self.combo_equipo_a.clear()
        self.combo_equipo_b.clear()
        
        equipos = self.db.obtener_todos_equipos()
        
        for equipo in equipos:
            # Cargar icono si existe
            if equipo['escudo_path'] and os.path.exists(equipo['escudo_path']):
                icon = QIcon(equipo['escudo_path'])
                self.combo_equipo_a.addItem(icon, equipo['nombre'], equipo['id'])
                self.combo_equipo_b.addItem(icon, equipo['nombre'], equipo['id'])
            else:
                self.combo_equipo_a.addItem(equipo['nombre'], equipo['id'])
                self.combo_equipo_b.addItem(equipo['nombre'], equipo['id'])
                
    def cargar_arbitros(self):
        """Carga los árbitros en el combo."""
        if not self.combo_arbitro:
            return
            
        self.combo_arbitro.clear()
        self.combo_arbitro.addItem("(Sin asignar)", None)
        
        arbitros = self.db.obtener_todos_arbitros()
        
        for arbitro in arbitros:
            nombre_completo = f"{arbitro['nombre']} {arbitro['apellidos']}"
            self.combo_arbitro.addItem(nombre_completo, arbitro['id'])
            
    def cargar_partidos(self):
        """Carga todos los partidos en el árbol, agrupados por eliminatoria."""
        if not self.tree_partidos:
            return
            
        self.tree_partidos.clear()
        
        # Verificar si hay torneo activo
        torneo = self.db.torneo_activo_existe()
        if not torneo:
            return
            
        # Obtener partidos del torneo
        partidos = self.db.obtener_partidos_por_torneo(torneo['id'])
        
        # Agrupar partidos por eliminatoria
        eliminatorias = {}
        for partido in partidos:
            ronda = partido['ronda']
            if ronda not in eliminatorias:
                eliminatorias[ronda] = []
            eliminatorias[ronda].append(partido)
            
        # Orden de las eliminatorias
        orden_eliminatorias = ["Previa", "Dieciseisavos", "Octavos", "Cuartos", "Semifinal", "Final"]
        
        # Crear items del árbol
        for eliminatoria in orden_eliminatorias:
            if eliminatoria not in eliminatorias:
                continue
                
            # Crear nodo padre para la eliminatoria
            item_eliminatoria = QTreeWidgetItem([eliminatoria, "", ""])
            item_eliminatoria.setExpanded(True)
            self.tree_partidos.addTopLevelItem(item_eliminatoria)
            
            # Añadir partidos de esta eliminatoria
            partidos_eliminatoria = eliminatorias[eliminatoria]
            # Ordenar por fecha y hora
            partidos_eliminatoria.sort(key=lambda p: (p['fecha'], p['hora']))
            
            for partido in partidos_eliminatoria:
                # Formatear fecha
                try:
                    fecha_obj = datetime.strptime(partido['fecha'], "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_formateada = partido['fecha']
                    
                # Obtener árbitro
                arbitro_nombre = "Sin asignar"
                if partido.get('arbitro_id'):
                    arbitro = self.db.obtener_arbitro_por_id(partido['arbitro_id'])
                    if arbitro:
                        arbitro_nombre = f"{arbitro['nombre']} {arbitro['apellidos']}"
                        
                # Crear item hijo
                vs_texto = f"{partido.get('equipo_a_nombre', 'Equipo A')} vs {partido.get('equipo_b_nombre', 'Equipo B')}"
                fecha_hora_texto = f"{fecha_formateada} {partido['hora']}"
                
                item_partido = QTreeWidgetItem([vs_texto, fecha_hora_texto, arbitro_nombre])
                item_partido.setData(0, Qt.UserRole, partido['id'])
                
                # Añadir icono del equipo A si existe
                if partido.get('equipo_a_escudo') and os.path.exists(partido['equipo_a_escudo']):
                    icon = QIcon(partido['equipo_a_escudo'])
                    item_partido.setIcon(0, icon)
                    
                item_eliminatoria.addChild(item_partido)
                
    def guardar_partido(self):
        """Guarda o actualiza un partido."""
        # Validar campos
        if not self.combo_equipo_a or not self.combo_equipo_b:
            QMessageBox.warning(self.widget, "Error", "Selecciona ambos equipos.")
            return
            
        equipo_a_id = self.combo_equipo_a.currentData()
        equipo_b_id = self.combo_equipo_b.currentData()
        
        if not equipo_a_id or not equipo_b_id:
            QMessageBox.warning(self.widget, "Error", "Debes seleccionar ambos equipos.")
            return
            
        if equipo_a_id == equipo_b_id:
            QMessageBox.warning(self.widget, "Error", "Los equipos deben ser diferentes.")
            return
            
        # Obtener datos
        fecha = self.date_fecha.date().toString("yyyy-MM-dd") if self.date_fecha else ""
        hora = self.time_hora.time().toString("HH:mm") if self.time_hora else ""
        arbitro_id = self.combo_arbitro.currentData() if self.combo_arbitro else None
        eliminatoria = self.combo_eliminatoria.currentText() if self.combo_eliminatoria else "Octavos"
        
        # Validar disponibilidad del árbitro
        if arbitro_id:
            disponible, mensaje = self.db.validar_arbitro_disponible(
                arbitro_id, fecha, hora, self.partido_editando
            )
            if not disponible:
                QMessageBox.warning(self.widget, "Error", mensaje)
                return
                
        try:
            # Verificar torneo activo
            torneo = self.db.torneo_activo_existe()
            if not torneo:
                QMessageBox.warning(self.widget, "Error", "No hay torneo activo. Crea uno primero.")
                return
                
            if self.partido_editando:
                # Actualizar partido existente
                self.db.actualizar_partido(
                    self.partido_editando,
                    equipo_a_id,
                    equipo_b_id,
                    fecha,
                    hora,
                    arbitro_id,
                    eliminatoria
                )
                QMessageBox.information(self.widget, "Éxito", "Partido actualizado correctamente.")
            else:
                # Crear nuevo partido
                # Calcular número de partido
                partidos_ronda = self.db.obtener_partidos_por_ronda(torneo['id'], eliminatoria)
                numero_partido = len(partidos_ronda) + 1
                
                self.db.crear_partido(
                    torneo['id'],
                    equipo_a_id,
                    equipo_b_id,
                    fecha,
                    hora,
                    arbitro_id,
                    eliminatoria,
                    numero_partido
                )
                QMessageBox.information(self.widget, "Éxito", "Partido creado correctamente.")
                
            # Limpiar formulario y recargar
            self.limpiar_formulario()
            self.cargar_partidos()
            
        except Exception as e:
            QMessageBox.critical(self.widget, "Error", f"Error al guardar partido: {str(e)}")
            
    def limpiar_formulario(self):
        """Limpia el formulario."""
        if self.combo_equipo_a:
            self.combo_equipo_a.setCurrentIndex(0)
        if self.combo_equipo_b:
            self.combo_equipo_b.setCurrentIndex(0)
        if self.date_fecha:
            self.date_fecha.setDate(QDate.currentDate())
        if self.time_hora:
            self.time_hora.setTime(QTime(18, 0))
        if self.combo_arbitro:
            self.combo_arbitro.setCurrentIndex(0)
        if self.combo_eliminatoria:
            self.combo_eliminatoria.setCurrentIndex(2)  # Octavos
            
        self.partido_editando = None
        
        if self.btn_guardar:
            self.btn_guardar.setText("GUARDAR")
            
    def cargar_partido_edicion(self, item: QTreeWidgetItem):
        """Carga los datos de un partido para edición."""
        # Solo cargar si es un partido (no una eliminatoria)
        partido_id = item.data(0, Qt.UserRole)
        if not partido_id:
            return
            
        # Obtener partido de la base de datos
        partido = self.db.obtener_partido_por_id(partido_id)
        if not partido:
            return
            
        self.partido_editando = partido_id
        
        # Cargar datos en el formulario
        if self.combo_equipo_a:
            index = self.combo_equipo_a.findData(partido['equipo_a_id'])
            if index >= 0:
                self.combo_equipo_a.setCurrentIndex(index)
                
        if self.combo_equipo_b:
            index = self.combo_equipo_b.findData(partido['equipo_b_id'])
            if index >= 0:
                self.combo_equipo_b.setCurrentIndex(index)
                
        if self.date_fecha and partido.get('fecha'):
            try:
                fecha = QDate.fromString(partido['fecha'], "yyyy-MM-dd")
                self.date_fecha.setDate(fecha)
            except:
                pass
                
        if self.time_hora and partido.get('hora'):
            try:
                hora = QTime.fromString(partido['hora'], "HH:mm")
                self.time_hora.setTime(hora)
            except:
                pass
                
        if self.combo_arbitro and partido.get('arbitro_id'):
            index = self.combo_arbitro.findData(partido['arbitro_id'])
            if index >= 0:
                self.combo_arbitro.setCurrentIndex(index)
            else:
                self.combo_arbitro.setCurrentIndex(0)
                
        if self.combo_eliminatoria and partido.get('ronda'):
            index = self.combo_eliminatoria.findText(partido['ronda'])
            if index >= 0:
                self.combo_eliminatoria.setCurrentIndex(index)
                
        if self.btn_guardar:
            self.btn_guardar.setText("ACTUALIZAR")
            
    def editar_partido_seleccionado(self):
        """Carga el partido seleccionado para edición."""
        if not self.tree_partidos:
            return
            
        item_actual = self.tree_partidos.currentItem()
        if not item_actual:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un partido para editar.")
            return
            
        # Verificar que es un partido (no una eliminatoria)
        partido_id = item_actual.data(0, Qt.UserRole)
        if not partido_id:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un partido específico.")
            return
            
        self.cargar_partido_edicion(item_actual)
        
    def eliminar_partido_seleccionado(self):
        """Elimina el partido seleccionado."""
        if not self.tree_partidos:
            return
            
        item_actual = self.tree_partidos.currentItem()
        if not item_actual:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un partido para eliminar.")
            return
            
        partido_id = item_actual.data(0, Qt.UserRole)
        if not partido_id:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un partido específico.")
            return
            
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self.widget,
            "Confirmar Eliminación",
            "¿Estás seguro de que quieres eliminar este partido?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                self.db.eliminar_partido(partido_id)
                QMessageBox.information(self.widget, "Éxito", "Partido eliminado correctamente.")
                self.limpiar_formulario()
                self.cargar_partidos()
            except Exception as e:
                QMessageBox.critical(self.widget, "Error", f"Error al eliminar partido: {str(e)}")
            
                self.cargar_partidos()
            except Exception as e:
                QMessageBox.critical(self.widget, "Error", f"Error al eliminar partido: {str(e)}")
