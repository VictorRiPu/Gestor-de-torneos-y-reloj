"""
Controlador de gestión de participantes (jugadores y árbitros).
Maneja la creación, edición y asignación de participantes a equipos.
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QLineEdit, QComboBox, 
                                QDateEdit, QFrame, QMessageBox, QListWidgetItem,
                                QListWidget, QCheckBox)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon
from Models.database import DatabaseManager
import os


class ParticipantesController:
    """Controlador para la pantalla de gestión de participantes."""
    
    def __init__(self, widget: QWidget, main_controller):
        """
        Inicializa el controlador de participantes.
        
        Args:
            widget: Widget de la vista de participantes
            main_controller: Controlador principal
        """
        self.widget = widget
        self.main_controller = main_controller
        self.db = DatabaseManager()
        self.participante_actual = None
        
        # Obtener widgets
        self._obtener_widgets()
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar datos iniciales
        self.cargar_equipos()
        self.cargar_participantes()
        
    def _obtener_widgets(self):
        """Obtiene referencias a los widgets."""
        # Campos comunes
        self.txt_nombre = self.widget.findChild(QLineEdit, "txtNombre")
        self.date_fecha_nacimiento = self.widget.findChild(QDateEdit, "dateFechaNacimiento")
        self.combo_curso = self.widget.findChild(QComboBox, "comboCurso")
        self.combo_tipo = self.widget.findChild(QComboBox, "comboTipo")
        
        # Frame de datos de jugador
        self.frame_datos_jugador = self.widget.findChild(QFrame, "frameDatosJugador")
        self.combo_posicion = self.widget.findChild(QComboBox, "comboPosicion")
        self.combo_equipo = self.widget.findChild(QComboBox, "comboEquipo")
        
        # Botones formulario
        self.btn_guardar = self.widget.findChild(QPushButton, "btnGuardar")
        self.btn_limpiar = self.widget.findChild(QPushButton, "btnLimpiar")
        self.btn_volver = self.widget.findChild(QPushButton, "btnVolver")
        
        # Lista de participantes
        self.txt_buscar = self.widget.findChild(QLineEdit, "txtBuscar")
        self.list_participantes = self.widget.findChild(QListWidget, "listParticipantes")
        self.btn_eliminar = self.widget.findChild(QPushButton, "btnEliminar")
        
        # Checkboxes de filtro
        self.chk_todos = self.widget.findChild(QCheckBox, "chkTodos")
        self.chk_jugadores = self.widget.findChild(QCheckBox, "chkJugadores")
        self.chk_arbitros = self.widget.findChild(QCheckBox, "chkArbitros")
        
    def _conectar_senales(self):
        """Conecta las señales."""
        # Botones formulario
        if self.btn_guardar:
            self.btn_guardar.clicked.connect(self.guardar_participante)
        if self.btn_limpiar:
            self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.main_controller.volver_a_principal)
            
        # Búsqueda
        if self.txt_buscar:
            self.txt_buscar.textChanged.connect(self.filtrar_participantes)
            
        # Checkboxes de filtro
        if self.chk_todos:
            self.chk_todos.stateChanged.connect(self.on_checkbox_todos_changed)
        if self.chk_jugadores:
            self.chk_jugadores.stateChanged.connect(self.filtrar_participantes)
        if self.chk_arbitros:
            self.chk_arbitros.stateChanged.connect(self.filtrar_participantes)
            
        # Lista - doble clic para editar
        if self.list_participantes:
            self.list_participantes.itemDoubleClicked.connect(self.editar_participante)
            
        # Botón eliminar
        if self.btn_eliminar:
            self.btn_eliminar.clicked.connect(self.eliminar_participante)
            
    def cargar_equipos(self):
        """Carga los equipos disponibles en el combo."""
        if not self.combo_equipo:
            return
            
        self.combo_equipo.clear()
        self.combo_equipo.addItem("Seleccionar equipo...", None)
        
        equipos = self.db.obtener_todos_equipos()
        for equipo in equipos:
            self.combo_equipo.addItem(equipo['nombre'], equipo['id'])
            
    def guardar_participante(self):
        """Guarda el participante en la base de datos."""
        # Validar campos comunes
        if not self.txt_nombre or not self.txt_nombre.text().strip():
            QMessageBox.warning(self.widget, "Error", "El nombre es obligatorio.")
            return
            
        nombre = self.txt_nombre.text().strip()
        fecha_nacimiento = self.date_fecha_nacimiento.date().toString("yyyy-MM-dd") if self.date_fecha_nacimiento else None
        curso = self.combo_curso.currentText() if self.combo_curso else ""
        tipo = self.combo_tipo.currentText()
        
        try:
            if tipo == "Jugador" or tipo == "Ambos":
                # Guardar como jugador
                equipo_id = self.combo_equipo.currentData() if self.combo_equipo else None
                posicion = self.combo_posicion.currentText() if self.combo_posicion else "Defensa"
                
                if self.participante_actual:
                    self.db.actualizar_jugador(
                        self.participante_actual, nombre, "", 
                        fecha_nacimiento, curso, equipo_id, posicion, 
                        1, False, 0, 0, 0
                    )
                    mensaje = "Jugador actualizado correctamente."
                else:
                    self.db.crear_jugador(
                        nombre, "", fecha_nacimiento, curso, 
                        equipo_id, posicion, 1, False, 0, 0, 0
                    )
                    mensaje = "Jugador creado correctamente."
                    
            elif tipo == "Árbitro":
                # Guardar como árbitro
                if self.participante_actual:
                    self.db.actualizar_arbitro(
                        self.participante_actual, nombre, "",
                        fecha_nacimiento, 0, "Regional"
                    )
                    mensaje = "Árbitro actualizado correctamente."
                else:
                    self.db.crear_arbitro(nombre, "", fecha_nacimiento, 0, "Regional")
                    mensaje = "Árbitro creado correctamente."
            else:
                QMessageBox.warning(self.widget, "Error", "Selecciona un tipo de participante.")
                return
                    
            QMessageBox.information(self.widget, "Éxito", mensaje)
            self.limpiar_formulario()
            self.cargar_participantes()
            
        except Exception as e:
            QMessageBox.critical(self.widget, "Error", f"Error al guardar: {str(e)}")
            
    def limpiar_formulario(self):
        """Limpia el formulario."""
        self.participante_actual = None
        
        if self.txt_nombre:
            self.txt_nombre.clear()
        if self.date_fecha_nacimiento:
            self.date_fecha_nacimiento.setDate(QDate.currentDate())
        if self.combo_curso:
            self.combo_curso.setCurrentIndex(0)
        if self.combo_tipo:
            self.combo_tipo.setCurrentIndex(0)
        if self.combo_posicion:
            self.combo_posicion.setCurrentIndex(0)
        if self.combo_equipo:
            self.combo_equipo.setCurrentIndex(0)
            
        if self.btn_guardar:
            self.btn_guardar.setText("GUARDAR PARTICIPANTE")
            
    def cargar_participantes(self):
        """Carga todos los participantes en la lista."""
        if not self.list_participantes:
            return
            
        self.list_participantes.clear()
        
        # Cargar jugadores
        jugadores = self.db.obtener_todos_jugadores()
        for jugador in jugadores:
            nombre = jugador.get('nombre', 'Sin nombre')
            curso = jugador.get('curso', 'Sin curso')
            equipo_nombre = jugador.get('equipo_nombre', 'Sin equipo')
            
            item = QListWidgetItem(f"🏃 {nombre} - {curso} - {equipo_nombre}")
            item.setData(Qt.UserRole, ('jugador', jugador['id']))
            self.list_participantes.addItem(item)
            
        # Cargar árbitros
        arbitros = self.db.obtener_todos_arbitros()
        for arbitro in arbitros:
            nombre = arbitro.get('nombre', 'Sin nombre')
            
            item = QListWidgetItem(f"⚖️ {nombre}")
            item.setData(Qt.UserRole, ('arbitro', arbitro['id']))
            self.list_participantes.addItem(item)
            
    def on_checkbox_todos_changed(self, state):
        """Maneja el cambio del checkbox 'Todos'."""
        if state == Qt.Checked:
            # Si se marca 'Todos', marcar Jugadores y Árbitros
            if self.chk_jugadores:
                self.chk_jugadores.setChecked(True)
            if self.chk_arbitros:
                self.chk_arbitros.setChecked(True)
        else:
            # Si se desmarca 'Todos', desmarcar Jugadores y Árbitros
            if self.chk_jugadores:
                self.chk_jugadores.setChecked(False)
            if self.chk_arbitros:
                self.chk_arbitros.setChecked(False)
        
        self.filtrar_participantes()
    
    def filtrar_participantes(self):
        """Filtra los participantes según el texto de búsqueda y los checkboxes."""
        if not self.list_participantes:
            return
            
        texto = self.txt_buscar.text().lower() if self.txt_buscar else ""
        
        # Obtener estados de los checkboxes
        mostrar_jugadores = self.chk_jugadores.isChecked() if self.chk_jugadores else True
        mostrar_arbitros = self.chk_arbitros.isChecked() if self.chk_arbitros else True
        
        for i in range(self.list_participantes.count()):
            item = self.list_participantes.item(i)
            texto_item = item.text().lower()
            tipo, _ = item.data(Qt.UserRole)
            
            # Verificar texto
            cumple_texto = texto in texto_item if texto else True
            
            # Verificar tipo
            cumple_tipo = False
            if tipo == 'jugador' and mostrar_jugadores:
                cumple_tipo = True
            elif tipo == 'arbitro' and mostrar_arbitros:
                cumple_tipo = True
            
            # Mostrar solo si cumple ambas condiciones
            item.setHidden(not (cumple_texto and cumple_tipo))
            
    def editar_participante(self, item: QListWidgetItem):
        """Carga los datos de un participante para edición."""
        tipo, participante_id = item.data(Qt.UserRole)
        self.participante_actual = participante_id
        
        if tipo == 'jugador':
            jugador = self.db.obtener_jugador_por_id(participante_id)
            if not jugador:
                return
                
            # Cargar datos básicos
            if self.txt_nombre:
                self.txt_nombre.setText(jugador.get('nombre', ''))
            if self.combo_curso:
                index = self.combo_curso.findText(jugador.get('curso', ''))
                if index >= 0:
                    self.combo_curso.setCurrentIndex(index)
            if self.date_fecha_nacimiento and jugador.get('fecha_nacimiento'):
                fecha = QDate.fromString(jugador['fecha_nacimiento'], "yyyy-MM-dd")
                self.date_fecha_nacimiento.setDate(fecha)
                
            # Seleccionar tipo jugador
            if self.combo_tipo:
                self.combo_tipo.setCurrentText("Jugador")
                
            # Cargar datos específicos
            if self.combo_equipo and jugador.get('equipo_id'):
                index = self.combo_equipo.findData(jugador['equipo_id'])
                if index >= 0:
                    self.combo_equipo.setCurrentIndex(index)
            if self.combo_posicion:
                index = self.combo_posicion.findText(jugador.get('posicion', 'Defensa'))
                if index >= 0:
                    self.combo_posicion.setCurrentIndex(index)
                    
        else:  # árbitro
            arbitro = self.db.obtener_arbitro_por_id(participante_id)
            if not arbitro:
                return
                
            # Cargar datos
            if self.txt_nombre:
                self.txt_nombre.setText(arbitro.get('nombre', ''))
            if self.date_fecha_nacimiento and arbitro.get('fecha_nacimiento'):
                fecha = QDate.fromString(arbitro['fecha_nacimiento'], "yyyy-MM-dd")
                self.date_fecha_nacimiento.setDate(fecha)
                
            # Seleccionar tipo árbitro
            if self.combo_tipo:
                self.combo_tipo.setCurrentText("Árbitro")
            
    def eliminar_participante(self):
        """Elimina el participante seleccionado."""
        if not self.list_participantes:
            return
            
        item = self.list_participantes.currentItem()
        if not item:
            QMessageBox.warning(self.widget, "Error", "Selecciona un participante para eliminar.")
            return
            
        tipo, participante_id = item.data(Qt.UserRole)
        
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self.widget,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este participante?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                if tipo == 'jugador':
                    self.db.eliminar_jugador(participante_id)
                    QMessageBox.information(self.widget, "Éxito", "Jugador eliminado correctamente.")
                else:
                    self.db.eliminar_arbitro(participante_id)
                    QMessageBox.information(self.widget, "Éxito", "Árbitro eliminado correctamente.")
                    
                self.cargar_participantes()
                
            except Exception as e:
                QMessageBox.critical(self.widget, "Error", f"Error al eliminar: {str(e)}")
