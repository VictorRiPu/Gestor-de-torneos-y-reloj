"""
Controlador de gestión de equipos.
Maneja creación, edición y eliminación de equipos.
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QLineEdit, QComboBox, 
                                QListWidget, QLabel, QColorDialog, QMessageBox,
                                QListWidgetItem)
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt
from Models.database import DatabaseManager, obtener_ruta_recurso
import os


class EquiposController:
    """Controlador para la pantalla de gestión de equipos."""
    
    def __init__(self, widget: QWidget, main_controller):
        """
        Inicializa el controlador de equipos.
        
        Args:
            widget: Widget de la vista de equipos
            main_controller: Controlador principal para navegación
        """
        self.widget = widget
        self.main_controller = main_controller
        self.db = DatabaseManager()
        
        self.color_seleccionado = "#4CAF50"  # Color por defecto
        self.escudo_seleccionado = None
        self.equipo_editando = None  # ID del equipo en edición
        
        # Obtener widgets
        self._obtener_widgets()
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar datos iniciales
        self.cargar_escudos_disponibles()
        self.cargar_lista_equipos()
        
    def _obtener_widgets(self):
        """Obtiene referencias a los widgets de la UI."""
        self.txt_nombre = self.widget.findChild(QLineEdit, "txtNombre")
        self.txt_curso = self.widget.findChild(QLineEdit, "txtCurso")
        self.btn_color = self.widget.findChild(QPushButton, "btnSeleccionarColor")
        self.combo_escudos = self.widget.findChild(QComboBox, "comboEscudos")
        self.lbl_vista_previa = self.widget.findChild(QLabel, "lblVistaPrevia")
        self.btn_guardar = self.widget.findChild(QPushButton, "btnGuardar")
        self.btn_limpiar = self.widget.findChild(QPushButton, "btnLimpiar")
        self.txt_buscar = self.widget.findChild(QLineEdit, "txtBuscar")
        self.list_equipos = self.widget.findChild(QListWidget, "listEquipos")
        self.btn_volver = self.widget.findChild(QPushButton, "btnVolver")
        self.btn_ver_jugadores = self.widget.findChild(QPushButton, "btnVerJugadores")
        self.btn_editar = self.widget.findChild(QPushButton, "btnEditar")
        self.btn_eliminar = self.widget.findChild(QPushButton, "btnEliminar")
        
    def _conectar_senales(self):
        """Conecta las señales de los widgets."""
        if self.btn_color:
            self.btn_color.clicked.connect(self.seleccionar_color)
        if self.combo_escudos:
            self.combo_escudos.currentIndexChanged.connect(self.actualizar_vista_previa)
        if self.btn_guardar:
            self.btn_guardar.clicked.connect(self.guardar_equipo)
        if self.btn_limpiar:
            self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        if self.txt_buscar:
            self.txt_buscar.textChanged.connect(self.filtrar_equipos)
        if self.list_equipos:
            self.list_equipos.itemClicked.connect(self.cargar_equipo_edicion)
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.main_controller.volver_a_principal)
        if self.btn_ver_jugadores:
            self.btn_ver_jugadores.clicked.connect(self.ver_jugadores_equipo)
        if self.btn_editar:
            self.btn_editar.clicked.connect(self.editar_equipo_seleccionado)
        if self.btn_eliminar:
            self.btn_eliminar.clicked.connect(self.eliminar_equipo_seleccionado)
            
    def cargar_escudos_disponibles(self):
        """Carga los escudos disponibles en el combobox, excluyendo los ya usados."""
        if not self.combo_escudos:
            return
            
        self.combo_escudos.clear()
        
        # Obtener escudos ya usados
        escudos_usados = self.db.obtener_escudos_usados()
        
        # Si estamos editando, permitir el escudo actual
        if self.equipo_editando:
            equipo = self.db.obtener_equipo_por_id(self.equipo_editando)
            if equipo and equipo['escudo_path'] in escudos_usados:
                escudos_usados.remove(equipo['escudo_path'])
        
        # Directorio de imágenes
        dir_imagenes = obtener_ruta_recurso("Resources/img")
        
        if os.path.exists(dir_imagenes):
            # Listar archivos SVG
            archivos = [f for f in os.listdir(dir_imagenes) 
                       if f.endswith('.svg') and f != 'fondo.jpg']
            
            for archivo in sorted(archivos):
                ruta_completa = os.path.join(dir_imagenes, archivo)
                
                # Solo agregar si no está en uso
                if ruta_completa not in escudos_usados:
                    # Agregar solo el ícono, sin texto
                    icon = QIcon(ruta_completa)
                    self.combo_escudos.addItem(icon, "", ruta_completa)
                    
    def seleccionar_color(self):
        """Abre el diálogo de selección de color."""
        color = QColorDialog.getColor(QColor(self.color_seleccionado), self.widget)
        
        if color.isValid():
            self.color_seleccionado = color.name()
            # Actualizar el botón con el color seleccionado
            if self.btn_color:
                self.btn_color.setStyleSheet(
                    f"background-color: {self.color_seleccionado}; "
                    f"color: white; font-weight: bold;"
                )
                self.btn_color.setText(f"Color: {self.color_seleccionado}")
                
    def actualizar_vista_previa(self):
        """Actualiza la vista previa del escudo seleccionado."""
        if not self.combo_escudos or not self.lbl_vista_previa:
            return
            
        ruta_escudo = self.combo_escudos.currentData()
        if ruta_escudo and os.path.exists(ruta_escudo):
            pixmap = QPixmap(ruta_escudo)
            self.lbl_vista_previa.setPixmap(
                pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.escudo_seleccionado = ruta_escudo
            
    def guardar_equipo(self):
        """Guarda o actualiza un equipo."""
        # Validar campos
        if not self.txt_nombre or not self.txt_nombre.text().strip():
            QMessageBox.warning(self.widget, "Error", "El nombre del equipo es obligatorio.")
            return
            
        if not self.txt_curso or not self.txt_curso.text().strip():
            QMessageBox.warning(self.widget, "Error", "El curso es obligatorio.")
            return
            
        if not self.escudo_seleccionado:
            QMessageBox.warning(self.widget, "Error", "Debes seleccionar un escudo.")
            return
            
        nombre = self.txt_nombre.text().strip()
        curso = self.txt_curso.text().strip()
        
        try:
            if self.equipo_editando:
                # Actualizar equipo existente
                self.db.actualizar_equipo(
                    self.equipo_editando,
                    nombre,
                    curso,
                    self.color_seleccionado,
                    self.escudo_seleccionado
                )
                QMessageBox.information(self.widget, "Éxito", "Equipo actualizado correctamente.")
            else:
                # Crear nuevo equipo
                self.db.crear_equipo(nombre, curso, self.color_seleccionado, self.escudo_seleccionado)
                QMessageBox.information(self.widget, "Éxito", "Equipo creado correctamente.")
                
            # Limpiar formulario y recargar lista
            self.limpiar_formulario()
            self.cargar_escudos_disponibles()
            self.cargar_lista_equipos()
            
        except Exception as e:
            QMessageBox.critical(self.widget, "Error", f"Error al guardar equipo: {str(e)}")
            
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        if self.txt_nombre:
            self.txt_nombre.clear()
        if self.txt_curso:
            self.txt_curso.clear()
        if self.combo_escudos:
            self.combo_escudos.setCurrentIndex(0)
        if self.lbl_vista_previa:
            self.lbl_vista_previa.clear()
            self.lbl_vista_previa.setText("Vista Previa:")
            
        self.color_seleccionado = "#4CAF50"
        self.escudo_seleccionado = None
        self.equipo_editando = None
        
        if self.btn_color:
            self.btn_color.setStyleSheet("")
            self.btn_color.setText("Seleccionar Color")
            
        if self.btn_guardar:
            self.btn_guardar.setText("GUARDAR EQUIPO")
            
    def cargar_lista_equipos(self):
        """Carga la lista de equipos registrados."""
        if not self.list_equipos:
            return
            
        # Limpiar lista
        self.list_equipos.clear()
        
        # Obtener equipos de la base de datos
        equipos = self.db.obtener_todos_equipos()
        print(f"Cargando {len(equipos)} equipos en la lista")
        
        for equipo in equipos:
            # Crear item con ícono
            item = QListWidgetItem()
            
            # Cargar ícono del escudo
            escudo_path = equipo.get('escudo_path', '')
            if escudo_path and os.path.exists(escudo_path):
                icon = QIcon(escudo_path)
                item.setIcon(icon)
                
            # Texto con información del equipo
            num_jugadores = self.db.contar_jugadores_por_equipo(equipo['id'])
            texto = f"{equipo['nombre']} - {equipo['curso']} ({num_jugadores} jugadores)"
            item.setText(texto)
            item.setData(Qt.UserRole, equipo['id'])
            
            # Añadir a la lista
            self.list_equipos.addItem(item)
            print(f"  - Añadido: {texto}")
            
    def filtrar_equipos(self):
        """Filtra los equipos según el texto de búsqueda."""
        if not self.txt_buscar or not self.list_equipos:
            return
            
        texto_busqueda = self.txt_buscar.text().strip()
        
        if texto_busqueda:
            equipos = self.db.buscar_equipos(texto_busqueda)
        else:
            equipos = self.db.obtener_todos_equipos()
            
        self.list_equipos.clear()
        
        for equipo in equipos:
            item = QListWidgetItem()
            if os.path.exists(equipo['escudo_path']):
                icon = QIcon(equipo['escudo_path'])
                item.setIcon(icon)
            num_jugadores = self.db.contar_jugadores_por_equipo(equipo['id'])
            item.setText(f"{equipo['nombre']} - {equipo['curso']} ({num_jugadores} jugadores)")
            item.setData(Qt.UserRole, equipo['id'])
            self.list_equipos.addItem(item)
            
    def cargar_equipo_edicion(self, item: QListWidgetItem):
        """
        Carga los datos de un equipo para edición.
        
        Args:
            item: Item seleccionado de la lista
        """
        equipo_id = item.data(Qt.UserRole)
        equipo = self.db.obtener_equipo_por_id(equipo_id)
        
        if not equipo:
            return
            
        self.equipo_editando = equipo_id
        
        # Cargar datos en el formulario
        if self.txt_nombre:
            self.txt_nombre.setText(equipo['nombre'])
        if self.txt_curso:
            self.txt_curso.setText(equipo['curso'])
            
        self.color_seleccionado = equipo['color']
        if self.btn_color:
            self.btn_color.setStyleSheet(
                f"background-color: {self.color_seleccionado}; color: white; font-weight: bold;"
            )
            self.btn_color.setText(f"Color: {self.color_seleccionado}")
            
        # Recargar escudos para incluir el actual
        self.cargar_escudos_disponibles()
        
        # Seleccionar el escudo del equipo
        if self.combo_escudos:
            for i in range(self.combo_escudos.count()):
                if self.combo_escudos.itemData(i) == equipo['escudo_path']:
                    self.combo_escudos.setCurrentIndex(i)
                    break
                    
        if self.btn_guardar:
            self.btn_guardar.setText("ACTUALIZAR EQUIPO")
            
    def ver_jugadores_equipo(self):
        """Muestra los jugadores del equipo seleccionado."""
        if not self.list_equipos:
            return
            
        item_actual = self.list_equipos.currentItem()
        if not item_actual:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un equipo.")
            return
            
        equipo_id = item_actual.data(Qt.UserRole)
        equipo = self.db.obtener_equipo_por_id(equipo_id)
        jugadores = self.db.obtener_jugadores_por_equipo(equipo_id)
        
        if not jugadores:
            QMessageBox.information(
                self.widget, 
                "Información", 
                f"El equipo '{equipo['nombre']}' no tiene jugadores registrados."
            )
            return
            
        # Crear mensaje con la lista de jugadores
        mensaje = f"JUGADORES DEL EQUIPO: {equipo['nombre']}\n"
        mensaje += "=" * 50 + "\n\n"
        
        for jugador in jugadores:
            capitan = " (C)" if jugador['es_capitan'] else ""
            mensaje += f"• {jugador['nombre']} {jugador['apellidos']}{capitan}\n"
            mensaje += f"  Posición: {jugador['posicion']} | Dorsal: {jugador['dorsal']} | Curso: {jugador['curso']}\n\n"
            
        QMessageBox.information(self.widget, "Jugadores del Equipo", mensaje)
        
    def editar_equipo_seleccionado(self):
        """Carga el equipo seleccionado para edición."""
        if not self.list_equipos:
            return
            
        item_actual = self.list_equipos.currentItem()
        if not item_actual:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un equipo para editar.")
            return
            
        self.cargar_equipo_edicion(item_actual)
        
    def eliminar_equipo_seleccionado(self):
        """Elimina el equipo seleccionado."""
        if not self.list_equipos:
            return
            
        item_actual = self.list_equipos.currentItem()
        if not item_actual:
            QMessageBox.warning(self.widget, "Advertencia", "Por favor, selecciona un equipo para eliminar.")
            return
            
        equipo_id = item_actual.data(Qt.UserRole)
        equipo = self.db.obtener_equipo_por_id(equipo_id)
        
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self.widget,
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar el equipo '{equipo['nombre']}'?\n\n"
            f"Esto también eliminará todos los jugadores asociados.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                self.db.eliminar_equipo(equipo_id)
                QMessageBox.information(self.widget, "Éxito", "Equipo eliminado correctamente.")
                self.limpiar_formulario()
                self.cargar_escudos_disponibles()
                self.cargar_lista_equipos()
            except Exception as e:
                QMessageBox.critical(self.widget, "Error", f"Error al eliminar equipo: {str(e)}")
