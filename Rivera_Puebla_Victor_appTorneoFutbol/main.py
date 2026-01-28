"""
Punto de entrada principal de la aplicación de Gestión de Torneos de Fútbol.
Inicializa la base de datos, carga la interfaz y arranca la aplicación.
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                               QFrame, QMenuBar, QMessageBox)
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QAction, QPalette, QPixmap, QBrush

from Models.database import DatabaseManager
from Controllers.main_controller import MainController
from generar_datos_prueba import generar_datos_prueba


class MainApp(QMainWindow):
    """Clase principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la aplicación principal."""
        super().__init__()
        
        # Configurar ventana
        self.setWindowTitle("Gestión de Torneos de Fútbol")
        self.resize(1200, 800)
        self._current_language = "es"
        
        # Inicializar base de datos
        self._inicializar_base_datos()
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Aplicar estilos
        self._aplicar_estilos()
        
        # Inicializar controlador principal
        self.main_controller = MainController(self)
        self.main_controller.establecer_idioma(self._current_language)
        
    def _inicializar_base_datos(self):
        """Inicializa la base de datos creando las tablas necesarias."""
        try:
            db = DatabaseManager()
            db.inicializar_db()
            print("Base de datos inicializada correctamente.")
            
            # Verificar si hay equipos en la base de datos
            equipos = db.obtener_todos_equipos()
            if not equipos:
                print("\nNo se encontraron equipos. Generando datos de prueba...")
                generar_datos_prueba()
                print("Datos de prueba generados correctamente.\n")
        except Exception as e:
            print(f"Error al inicializar base de datos: {e}")
            sys.exit(1)
            
    def _crear_interfaz(self):
        """Crea la interfaz principal."""
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # StackedWidget para navegación
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setObjectName("stackedWidget")

        # Página principal
        pagina_principal = self._crear_pagina_principal()
        self.stackedWidget.addWidget(pagina_principal)

        main_layout.addWidget(self.stackedWidget)

        # Crear menú
        self._crear_menu()
        
    def _crear_menu(self):
        """Crea la barra de menú."""
        menubar = self.menuBar()

        # Menú Herramientas con acceso al reloj
        menu_herramientas = menubar.addMenu("Herramientas")
        menu_herramientas.setObjectName("menuHerramientas")

        self.actionAbrirReloj = QAction("Abrir Reloj/Cronómetro", self)
        self.actionAbrirReloj.setObjectName("actionAbrirReloj")
        menu_herramientas.addAction(self.actionAbrirReloj)
        
        # Menú Ayuda
        menu_ayuda = menubar.addMenu("Ayuda")
        
        self.actionAyuda = QAction("Tutorial", self)
        self.actionAyuda.setObjectName("actionAyuda")
        menu_ayuda.addAction(self.actionAyuda)
        
        self.actionCreditos = QAction("Créditos", self)
        self.actionCreditos.setObjectName("actionCreditos")
        menu_ayuda.addAction(self.actionCreditos)

    def notificar_cambio_idioma(self, language_code: str) -> None:
        """Propaga el cambio de idioma al controlador y a los componentes reutilizables."""
        normalized = (language_code or "es").lower()
        selected = "es" if normalized.startswith("es") else "en"
        self._current_language = selected
        if hasattr(self, "main_controller"):
            self.main_controller.establecer_idioma(selected)
        
    def _crear_pagina_principal(self):
        """Crea la página principal con los botones de navegación."""
        pagina = QWidget()
        pagina.setObjectName("pagina_principal")
        
        layout = QVBoxLayout(pagina)
        
        # Título
        lblTitulo = QLabel("GESTIÓN DE TORNEOS DE FÚTBOL")
        lblTitulo.setObjectName("lblTitulo")
        lblTitulo.setAlignment(Qt.AlignCenter)
        lblTitulo.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #FFD700;
            background: rgba(30, 40, 60, 0.9);
            padding: 20px;
            border: 2px solid #4A5F7F;
            border-radius: 10px;
        """)
        layout.addWidget(lblTitulo)
        
        # Contenedor central
        contenedor = QWidget()
        contenedor_layout = QVBoxLayout(contenedor)
        contenedor_layout.setContentsMargins(50, 30, 50, 30)
        contenedor_layout.setSpacing(20)
        
        # Fila 1: Equipos/Participantes y Calendario
        fila1 = QWidget()
        fila1_layout = QHBoxLayout(fila1)
        fila1_layout.setSpacing(20)
        
        # Frame Equipos/Participantes
        frame_ep = QFrame()
        frame_ep.setObjectName("frameEquiposParticipantes")
        frame_ep_layout = QVBoxLayout(frame_ep)
        
        lbl_ep = QLabel("Gestión de Datos")
        lbl_ep.setAlignment(Qt.AlignCenter)
        lbl_ep.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        frame_ep_layout.addWidget(lbl_ep)
        
        self.btnEquipos = QPushButton("EQUIPOS")
        self.btnEquipos.setObjectName("btnEquipos")
        self.btnEquipos.setMinimumHeight(80)
        self.btnEquipos.setCursor(Qt.PointingHandCursor)
        frame_ep_layout.addWidget(self.btnEquipos)
        
        self.btnParticipantes = QPushButton("PARTICIPANTES")
        self.btnParticipantes.setObjectName("btnParticipantes")
        self.btnParticipantes.setMinimumHeight(80)
        self.btnParticipantes.setCursor(Qt.PointingHandCursor)
        frame_ep_layout.addWidget(self.btnParticipantes)
        
        fila1_layout.addWidget(frame_ep)
        
        # Frame Calendario
        frame_cal = QFrame()
        frame_cal.setObjectName("frameCalendario")
        frame_cal_layout = QVBoxLayout(frame_cal)
        
        lbl_cal = QLabel("Calendario de Partidos")
        lbl_cal.setAlignment(Qt.AlignCenter)
        lbl_cal.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        frame_cal_layout.addWidget(lbl_cal)
        
        self.btnCalendario = QPushButton("CALENDARIO")
        self.btnCalendario.setObjectName("btnCalendario")
        self.btnCalendario.setMinimumHeight(180)
        self.btnCalendario.setCursor(Qt.PointingHandCursor)
        frame_cal_layout.addWidget(self.btnCalendario)
        
        fila1_layout.addWidget(frame_cal)
        
        contenedor_layout.addWidget(fila1)
        
        # Fila 2: Resultados y Clasificación
        fila2 = QWidget()
        fila2_layout = QHBoxLayout(fila2)
        fila2_layout.setSpacing(20)
        
        # Frame Resultados
        frame_res = QFrame()
        frame_res.setObjectName("frameResultados")
        frame_res_layout = QVBoxLayout(frame_res)
        
        lbl_res = QLabel("Registro de Resultados")
        lbl_res.setAlignment(Qt.AlignCenter)
        lbl_res.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        frame_res_layout.addWidget(lbl_res)
        
        self.btnResultados = QPushButton("RESULTADOS")
        self.btnResultados.setObjectName("btnResultados")
        self.btnResultados.setMinimumHeight(180)
        self.btnResultados.setCursor(Qt.PointingHandCursor)
        frame_res_layout.addWidget(self.btnResultados)
        
        fila2_layout.addWidget(frame_res)
        
        # Frame Clasificación
        frame_clas = QFrame()
        frame_clas.setObjectName("frameClasificacion")
        frame_clas_layout = QVBoxLayout(frame_clas)
        
        lbl_clas = QLabel("Brackets y Clasificación")
        lbl_clas.setAlignment(Qt.AlignCenter)
        lbl_clas.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        frame_clas_layout.addWidget(lbl_clas)
        
        self.btnClasificacion = QPushButton("CLASIFICACIÓN")
        self.btnClasificacion.setObjectName("btnClasificacion")
        self.btnClasificacion.setMinimumHeight(180)
        self.btnClasificacion.setCursor(Qt.PointingHandCursor)
        frame_clas_layout.addWidget(self.btnClasificacion)
        
        fila2_layout.addWidget(frame_clas)
        
        contenedor_layout.addWidget(fila2)
        
        # Botones inferiores
        botones_inf = QWidget()
        botones_inf_layout = QHBoxLayout(botones_inf)
        
        self.btnNuevoTorneo = QPushButton("NUEVO TORNEO")
        self.btnNuevoTorneo.setObjectName("btnNuevoTorneo")
        self.btnNuevoTorneo.setMinimumHeight(60)
        self.btnNuevoTorneo.setCursor(Qt.PointingHandCursor)
        botones_inf_layout.addWidget(self.btnNuevoTorneo)
        
        self.btnFinalizarTorneo = QPushButton("FINALIZAR TORNEO")
        self.btnFinalizarTorneo.setObjectName("btnFinalizarTorneo")
        self.btnFinalizarTorneo.setMinimumHeight(60)
        self.btnFinalizarTorneo.setCursor(Qt.PointingHandCursor)
        self.btnFinalizarTorneo.setVisible(False)  # Oculto por defecto
        botones_inf_layout.addWidget(self.btnFinalizarTorneo)
        
        contenedor_layout.addWidget(botones_inf)
        
        layout.addWidget(contenedor)
        
        return pagina
        
    def _aplicar_estilos(self):
        """Aplica los estilos QSS a la aplicación."""
        
        # Obtener ruta absoluta de la imagen de fondo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fondo_path = os.path.join(base_dir, "Resources", "img", "fondo.jpg")
        
        # Aplicar imagen de fondo usando QPalette
        pixmap = QPixmap(fondo_path)
        if not pixmap.isNull():
            # Escalar imagen para cubrir toda la ventana manteniendo aspecto
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            print(f"Imagen de fondo aplicada desde: {fondo_path}")
        else:
            print(f"Error: No se pudo cargar la imagen de fondo desde: {fondo_path}")
        
        qss_content = """
        /* Widget central transparente para mostrar el fondo */
        QWidget#centralwidget {{
            background: transparent;
        }}
        
        /* Botones principales con mismo estilo que el título */
        QPushButton {{
            background: rgba(30, 40, 60, 0.9);
            color: #FFD700;
            border: 2px solid #4A5F7F;
            border-radius: 10px;
            padding: 15px 25px;
            font-size: 17px;
            font-weight: bold;
            min-height: 50px;
        }}
        
        QPushButton:hover {{
            background: rgba(36, 48, 72, 0.95);
            border-color: #5E78A0;
        }}
        
        QPushButton:pressed {{
            background: rgba(22, 30, 46, 0.95);
            border-color: #394860;
            padding-top: 17px;
            padding-bottom: 13px;
        }}
        
        /* Frames con sombra y borde oscuro */
        QFrame {{
            background: rgba(255, 255, 255, 1.0);
            border-radius: 20px;
            border: 4px solid #333333;
        }}
        
        QLabel {{
            color: #000000;
        }}
        
        /* Campos de texto modernos */
        QLineEdit {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            color: #000000;
        }}
        
        QLineEdit:focus {{
            border: 2px solid #4CAF50;
            background: #F1F8E9;
        }}
        
        /* ComboBox moderno */
        QComboBox {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            padding: 8px;
            min-height: 30px;
            color: #000000;
        }}
        
        QComboBox:focus {{
            border: 2px solid #4CAF50;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #4CAF50;
            margin-right: 10px;
        }}
        
        /* Listas */
        QListWidget {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            padding: 5px;
            color: #000000;
        }}
        
        QListWidget::item {{
            border-radius: 5px;
            padding: 8px;
            margin: 2px;
            color: #000000;
        }}
        
        QListWidget::item:selected {{
            background: #C8E6C9;
            color: #1B5E20;
        }}
        
        QListWidget::item:hover {{
            background: #E8F5E9;
        }}
        
        /* Tablas */
        QTableWidget {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            gridline-color: #E8F5E9;
        }}
        
        QTableWidget::item {{
            padding: 5px;
        }}
        
        QTableWidget::item:selected {{
            background: #C8E6C9;
            color: #1B5E20;
        }}
        
        /* Headers de tabla */
        QHeaderView::section {{
            background: #4CAF50;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        
        /* Scrollbars modernos */
        QScrollBar:vertical {{
            background: #E8F5E9;
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: #4CAF50;
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: #66BB6A;
        }}
        
        QScrollBar:horizontal {{
            background: #E8F5E9;
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: #4CAF50;
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: #66BB6A;
        }}
        
        /* MenuBar */
        QMenuBar {{
            background: #4CAF50;
            color: white;
            padding: 5px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 8px 15px;
            border-radius: 5px;
        }}
        
        QMenuBar::item:selected {{
            background: #66BB6A;
        }}
        
        QMenu {{
            background: white;
            border: 2px solid #4CAF50;
            border-radius: 10px;
        }}
        
        QMenu::item {{
            padding: 8px 25px;
        }}
        
        QMenu::item:selected {{
            background: #E8F5E9;
            color: #1B5E20;
        }}        
        /* RadioButtons y CheckBoxes */
        QRadioButton {{
            color: #000000;
            font-size: 14px;
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid #4CAF50;
            background: white;
        }}
        
        QRadioButton::indicator:checked {{
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                       fx:0.5, fy:0.5, stop:0 #4CAF50, stop:0.6 #4CAF50, stop:0.7 white);
        }}
        
        QCheckBox {{
            color: #000000;
            font-size: 14px;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #4CAF50;
            background: white;
        }}
        
        QCheckBox::indicator:checked {{
            background: #4CAF50;
            image: none;
        }}
        
        /* SpinBox */
        QSpinBox {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            padding: 8px;
            color: #000000;
            font-size: 14px;
        }}
        
        QSpinBox:focus {{
            border: 2px solid #4CAF50;
        }}
        
        /* DateEdit */
        QDateEdit {{
            background: white;
            border: 2px solid #C8E6C9;
            border-radius: 10px;
            padding: 8px;
            color: #000000;
            font-size: 14px;
        }}
        
        QDateEdit:focus {{
            border: 2px solid #4CAF50;
        }}
        
        QDateEdit::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QDateEdit::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #4CAF50;
            margin-right: 10px;
        }}        """
        
        self.setStyleSheet(qss_content)
        print("Estilos aplicados correctamente.")


def main():
    """Función principal que inicia la aplicación."""
    # Crear aplicación
    app = QApplication(sys.argv)
    
    # Configurar locale español para formato de fechas
    QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Spain))
    
    # Configurar nombre y organización de la aplicación
    app.setApplicationName("Gestión de Torneos de Fútbol")
    app.setOrganizationName("Víctor Rivera Puebla")
    app.setApplicationVersion("1.0")
    
    # Crear y mostrar ventana principal
    ventana = MainApp()
    ventana.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
