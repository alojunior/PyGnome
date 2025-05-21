import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QMessageBox, QSplitter, 
                             QStatusBar, QToolBar, QFileDialog, QMenu, QStyle,
                             QStyleFactory)
from PySide6.QtCore import Qt, Slot, QSettings, QSize, QEvent
from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QPixmap

# Importando os widgets das abas
from widgets.model_config_widget import ModelConfigWidget
from widgets.movers_config_widget import MoversConfigWidget
from widgets.spill_config_widget import SpillConfigWidget
from widgets.weathering_config_widget import WeatheringConfigWidget
from widgets.output_config_widget import OutputConfigWidget
from widgets.simulation_widget import SimulationWidget

try:
    import gnome
    import gnome.scripting as gs
    PYGNOME_AVAILABLE = True
except ImportError:
    PYGNOME_AVAILABLE = False
    print("PyGNOME não está instalado. O aplicativo funcionará em modo de demonstração.")

class MainWindow(QMainWindow):
    """Janela principal da aplicação PyGNOME Interface"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da aplicação
        self.app_settings = QSettings("NOAA", "PyGNOME Interface")
        
        # Interface
        self.initUI()
        
        # Aplicar estilo moderno
        self.apply_modern_style()
        
        # Exibir mensagem se PyGNOME não estiver disponível
        if not PYGNOME_AVAILABLE:
            QMessageBox.warning(
                self, 
                "PyGNOME não encontrado", 
                "O PyGNOME não foi encontrado no ambiente Python atual. "
                "O aplicativo funcionará em modo de demonstração, mas as simulações não serão executadas."
                "\n\nCertifique-se de que o PyGNOME está instalado no seu ambiente Python atual."
            )
            
    def initUI(self):
        """Inicializa a interface do usuário"""
        # Configurações da janela
        self.setWindowTitle("PyGNOME Interface")
        self.setMinimumSize(1000, 700)
        
        # Ícone da aplicação - usando o caminho especificado
        icon_path = r"C:\Users\Andre\Documents\Projetos\pyGNOME\PyGnome\py_gnome\scripts\gnome_gui\resources\gnome_icon.png"
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
        else:
            # Fallback para ícone padrão caso o arquivo não seja encontrado
            app_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
            self.setWindowIcon(app_icon)
            print(f"Aviso: Ícone não encontrado: {icon_path}")
        
        # Menu principal
        self.create_menu()
        
        # Barra de ferramentas
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # Criar abas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Aba 1: Configuração do Modelo
        model_icon_path = os.path.join(os.path.dirname(__file__), "resources", "model_icon.png")
        model_icon = QIcon(model_icon_path) if os.path.exists(model_icon_path) else self.style().standardIcon(QStyle.SP_FileIcon)
        self.model_config_widget = ModelConfigWidget()
        self.tabs.addTab(self.model_config_widget, model_icon, "Modelo")
        
        # Aba 2: Configuração dos Movers
        movers_icon_path = os.path.join(os.path.dirname(__file__), "resources", "movers_icon.png")
        movers_icon = QIcon(movers_icon_path) if os.path.exists(movers_icon_path) else self.style().standardIcon(QStyle.SP_DirIcon)
        self.movers_config_widget = MoversConfigWidget()
        self.tabs.addTab(self.movers_config_widget, movers_icon, "Movers")
        
        # Aba 3: Configuração do Derramamento
        spill_icon_path = os.path.join(os.path.dirname(__file__), "resources", "spill_icon.png")
        spill_icon = QIcon(spill_icon_path) if os.path.exists(spill_icon_path) else self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.spill_config_widget = SpillConfigWidget()
        self.tabs.addTab(self.spill_config_widget, spill_icon, "Derramamento")
        
        # Aba 4: Configuração do Intemperismo
        weathering_icon_path = os.path.join(os.path.dirname(__file__), "resources", "weathering_icon.png")
        weathering_icon = QIcon(weathering_icon_path) if os.path.exists(weathering_icon_path) else self.style().standardIcon(QStyle.SP_TrashIcon)
        self.weathering_config_widget = WeatheringConfigWidget()
        self.tabs.addTab(self.weathering_config_widget, weathering_icon, "Intemperismo")
        
        # Aba 5: Configuração das Saídas
        output_icon_path = os.path.join(os.path.dirname(__file__), "resources", "output_icon.png")
        output_icon = QIcon(output_icon_path) if os.path.exists(output_icon_path) else self.style().standardIcon(QStyle.SP_DialogSaveButton)
        self.output_config_widget = OutputConfigWidget()
        self.tabs.addTab(self.output_config_widget, output_icon, "Saídas")
        
        # Aba 6: Simulação
        simulation_icon_path = os.path.join(os.path.dirname(__file__), "resources", "simulation_icon.png")
        simulation_icon = QIcon(simulation_icon_path) if os.path.exists(simulation_icon_path) else self.style().standardIcon(QStyle.SP_MediaPlay)
        self.simulation_widget = SimulationWidget()
        self.tabs.addTab(self.simulation_widget, simulation_icon, "Simulação")
        
        # Adicionar abas ao layout principal
        main_layout.addWidget(self.tabs)
        
        # Configurar barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("Pronto")
        
        # Conectar sinais e slots
        self.tabs.currentChanged.connect(self.tab_changed)
        
        # Conectar botão de simulação
        self.simulation_widget.run_button.clicked.connect(self.run_simulation)
    
    def create_menu(self):
        """Cria o menu principal"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        menu_file = menubar.addMenu("&Arquivo")
        
        # Ação Novo
        action_new = QAction(self.style().standardIcon(QStyle.SP_FileIcon), "&Novo", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self.new_project)
        menu_file.addAction(action_new)
        
        # Ação Abrir
        action_open = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "&Abrir...", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.open_project)
        menu_file.addAction(action_open)
        
        # Ação Salvar
        action_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "&Salvar", self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self.save_project)
        menu_file.addAction(action_save)
        
        # Ação Salvar Como
        action_save_as = QAction(self.style().standardIcon(QStyle.SP_DriveFDIcon), "Salvar &Como...", self)
        action_save_as.setShortcut("Ctrl+Shift+S")
        action_save_as.triggered.connect(self.save_project_as)
        menu_file.addAction(action_save_as)
        
        menu_file.addSeparator()
        
        # Ação Sair
        action_exit = QAction(self.style().standardIcon(QStyle.SP_DialogCloseButton), "&Sair", self)
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)
        menu_file.addAction(action_exit)
        
        # Menu Ajuda
        menu_help = menubar.addMenu("A&juda")
        
        # Ação Sobre
        action_about = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), "&Sobre", self)
        action_about.triggered.connect(self.show_about)
        menu_help.addAction(action_about)
        
    def create_toolbar(self):
        """Cria a barra de ferramentas"""
        self.toolbar = QToolBar("Barra de Ferramentas Principal")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Ação Novo Projeto
        action_new = QAction(self.style().standardIcon(QStyle.SP_FileIcon), "Novo", self)
        action_new.triggered.connect(self.new_project)
        self.toolbar.addAction(action_new)
        
        # Ação Abrir Projeto
        action_open = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "Abrir", self)
        action_open.triggered.connect(self.open_project)
        self.toolbar.addAction(action_open)
        
        # Ação Salvar Projeto
        action_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Salvar", self)
        action_save.triggered.connect(self.save_project)
        self.toolbar.addAction(action_save)
        
        self.toolbar.addSeparator()
        
        # Ação Executar Simulação
        action_run = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Executar", self)
        action_run.triggered.connect(self.run_simulation)
        self.toolbar.addAction(action_run)
        
        # Ação Parar Simulação
        action_stop = QAction(self.style().standardIcon(QStyle.SP_MediaStop), "Parar", self)
        action_stop.triggered.connect(self.stop_simulation)
        self.toolbar.addAction(action_stop)
    
    def apply_modern_style(self):
        """Aplica um estilo moderno e bonito à interface"""
        
        # Paleta de cores moderna com azul-petróleo como cor predominante
        colors = {
            'primary': '#0369A1',         # Azul-petróleo principal
            'primary_dark': '#075985',    # Azul-petróleo escuro
            'primary_light': '#38BDF8',   # Azul-petróleo claro
            'accent': '#059669',          # Verde esmeralda
            'accent_dark': '#047857',     # Verde esmeralda escuro
            'dark': '#1F2937',            # Cinza antracite
            'dark_gray': '#374151',       # Cinza antracite mais claro
            'light': '#FFFFFF',           # Branco
            'gray_light': '#F1F2F6',      # Cinza muito claro
            'gray': '#D1D5DB',            # Cinza claro
            'gray_dark': '#6B7280',       # Cinza médio
            'text_dark': '#1F2937',       # Texto escuro
            'text_light': '#FFFFFF',      # Texto claro
            'danger': '#EF4444',          # Vermelho
            'title_text': '#60A5FA',      # Azul claro para títulos
        }
        
        # Aplicar o estilo no aplicativo
        self.setStyleSheet(f"""
            /* Janela Principal */
            QMainWindow {{
                background-color: {colors['primary']};
            }}
            
            /* Widgets Gerais */
            QWidget {{
                background-color: {colors['primary']};
                color: {colors['text_light']};
            }}
            
            /* Barra de Menu */
            QMenuBar {{
                background-color: {colors['primary']};
                color: {colors['text_light']};
                border-bottom: 1px solid {colors['primary_dark']};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 10px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors['primary_dark']};
                color: {colors['text_light']};
            }}
            
            /* Menus */
            QMenu {{
                background-color: {colors['primary_dark']};
                color: {colors['text_light']};
                border: 1px solid {colors['primary_dark']};
                padding: 5px;
            }}
            
            QMenu::item {{
                padding: 5px 25px 5px 30px;
                border-radius: 3px;
                margin: 2px;
            }}
            
            QMenu::item:selected {{
                background-color: {colors['primary']};
                color: {colors['text_light']};
            }}
            
            /* Barra de Status */
            QStatusBar {{
                background-color: {colors['primary']};
                color: {colors['text_light']};
                border-top: 1px solid {colors['primary_dark']};
                padding: 3px;
            }}
            
            /* Barra de Ferramentas */
            QToolBar {{
                background-color: {colors['primary']};
                border-bottom: 1px solid {colors['primary_dark']};
                spacing: 6px;
                padding: 3px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border-radius: 4px;
                padding: 5px;
                color: {colors['text_light']};
            }}
            
            QToolButton:hover {{
                background-color: {colors['primary_dark']};
            }}
            
            QToolButton:pressed {{
                background-color: {colors['primary_light']};
            }}
            
            /* Abas */
            QTabWidget::pane {{
                border: 1px solid {colors['primary_dark']};
                border-radius: 4px;
                background-color: {colors['dark']};
                top: -1px;
            }}
            
            QTabBar::tab {{
                background: {colors['primary_light']};
                border: 1px solid {colors['primary_dark']};
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 6em;
                margin-right: 1px;
                color: {colors['text_dark']};
            }}
            
            QTabBar::tab:selected {{
                background: {colors['primary']};
                color: {colors['text_light']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background: {colors['primary_light']};
                color: {colors['text_dark']};
            }}
            
            /* GroupBox */
            QGroupBox {{
                border: 1px solid {colors['primary_dark']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                background-color: {colors['dark']};
                color: {colors['text_light']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {colors['title_text']};
                background-color: {colors['dark']};
            }}
            
            /* Botões */
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['text_light']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_dark']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary_light']};
                color: {colors['text_dark']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['gray']};
                color: {colors['gray_dark']};
            }}
            
            /* Botão Executar Simulação */
            #run_button {{
                background-color: {colors['accent']};
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            #run_button:hover {{
                background-color: {colors['accent_dark']};
            }}
            
            /* Botão Parar Simulação */
            #stop_button {{
                background-color: {colors['danger']};
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            /* Campos de Entrada */
            QLineEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit, QComboBox {{
                background-color: {colors['light']};
                color: {colors['text_dark']};
                border: 1px solid {colors['primary_dark']};
                border-radius: 4px;
                padding: 6px;
                min-height: 20px;
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            /* Checkbox e Radio Button */
            QCheckBox, QRadioButton {{
                spacing: 8px;
                background-color: transparent;
                color: {colors['text_light']};
            }}
            
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                background-color: {colors['light']};
                border: 1px solid {colors['primary_dark']};
            }}
            
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {colors['primary']};
            }}
            
            /* Labels */
            QLabel {{
                background-color: transparent;
                color: {colors['text_light']};
            }}
            
            /* Cabeçalhos dos GroupBox */
            QLabel[isHeader=true] {{
                color: {colors['title_text']};
                font-weight: bold;
                font-size: 14px;
                background-color: transparent;
            }}
            
            /* Area de Texto */
            QTextEdit {{
                background-color: {colors['light']};
                color: {colors['text_dark']};
                border: 1px solid {colors['primary_dark']};
                border-radius: 4px;
            }}
            
            /* Barra de Progresso */
            QProgressBar {{
                border: 1px solid {colors['primary_dark']};
                border-radius: 4px;
                text-align: center;
                background-color: {colors['dark_gray']};
                height: 20px;
                color: {colors['text_light']};
            }}
            
            QProgressBar::chunk {{
                background-color: {colors['primary']};
                width: 10px;
                border-radius: 2px;
            }}
            
            /* Scroll Bar */
            QScrollBar:vertical {{
                background-color: {colors['dark_gray']};
                width: 12px;
                margin: 10px 0 10px 0;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['primary']};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {colors['dark_gray']};
                height: 12px;
                margin: 0 10px 0 10px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors['primary']};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            /* Título no centro das abas */
            QLabel[type="tab_title"] {{
                font-weight: bold;
                font-size: 16px;
                color: {colors['title_text']};
                background-color: transparent;
            }}
            
            /* Output Widget específico */
            #output_dir_input, QTableWidget {{
                background-color: {colors['light']};
                color: {colors['text_dark']};
                border: 1px solid {colors['primary_dark']};
                border-radius: 3px;
                padding: 4px;
                margin: 2px;
            }}
            
            QFrame.format_frame {{
                background-color: {colors['dark_gray']};
                border: 1px solid {colors['primary_dark']};
                border-radius: 6px;
                padding: 10px;
                margin: 5px 0;
            }}
            
            QLabel[tab="output"] {{
                color: {colors['text_light']};
                font-weight: bold;
                background-color: transparent;
            }}
        """)
    
    @Slot(int)
    def tab_changed(self, index):
        """Manipulador quando a aba atual é alterada"""
        tab_name = self.tabs.tabText(index)
        self.status_bar.showMessage(f"Aba atual: {tab_name}")
        
        # Se a aba de simulação for selecionada, preparar os dados
        if index == 5:  # Índice da aba de simulação
            self.prepare_simulation_data()
            
    def new_project(self):
        """Cria um novo projeto"""
        reply = QMessageBox.question(
            self, "Novo Projeto", 
            "Deseja criar um novo projeto? Todas as alterações não salvas serão perdidas.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Resetar todas as configurações
            self.model_config_widget.reset()
            self.movers_config_widget.reset()
            self.spill_config_widget.reset()
            self.weathering_config_widget.reset()
            self.output_config_widget.reset()
            self.simulation_widget.reset()
            
            self.status_bar.showMessage("Novo projeto criado")
            
    def open_project(self):
        """Abre um projeto existente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto", "", "Arquivos de Projeto PyGNOME (*.pygui);;Todos os Arquivos (*)"
        )
        
        if file_path:
            # Implementar a lógica para carregar o projeto
            self.status_bar.showMessage(f"Projeto carregado: {file_path}")
            
    def save_project(self):
        """Salva o projeto atual"""
        # Verificar se já existe um arquivo de projeto
        if hasattr(self, 'current_project_file') and self.current_project_file:
            # Implementar a lógica para salvar o projeto
            self.status_bar.showMessage(f"Projeto salvo: {self.current_project_file}")
        else:
            # Se não existir, chamar salvar como
            self.save_project_as()
            
    def save_project_as(self):
        """Salva o projeto atual com um novo nome"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Projeto Como", "", "Arquivos de Projeto PyGNOME (*.pygui);;Todos os Arquivos (*)"
        )
        
        if file_path:
            # Garantir que a extensão seja .pygui
            if not file_path.endswith('.pygui'):
                file_path += '.pygui'
                
            # Salvar o caminho do arquivo atual
            self.current_project_file = file_path
            
            # Implementar a lógica para salvar o projeto
            self.status_bar.showMessage(f"Projeto salvo como: {file_path}")
            
    def prepare_simulation_data(self):
        """Prepara os dados para simulação"""
        # Coletar configurações de todas as abas
        model_config = self.model_config_widget.get_config()
        movers_config = self.movers_config_widget.get_config()
        spill_config = self.spill_config_widget.get_config()
        weathering_config = self.weathering_config_widget.get_config()
        output_config = self.output_config_widget.get_config()
        
        # Combinar todas as configurações
        simulation_config = {
            'model': model_config,
            'movers': movers_config,
            'spill': spill_config,
            'weatherers': weathering_config,
            'output': output_config
        }
        
        # Passar a configuração para o widget de simulação
        self.simulation_widget.set_simulation_config(simulation_config)
            
    def run_simulation(self):
        """Executa a simulação"""
        # Mudar para a aba de simulação
        self.tabs.setCurrentIndex(5)
        
        # Preparar os dados para simulação
        self.prepare_simulation_data()
        
        # Iniciar a simulação
        self.simulation_widget.start_simulation()
    
    def stop_simulation(self):
        """Para a simulação em execução"""
        if hasattr(self, 'simulation_widget'):
            self.simulation_widget.stop_simulation()
        
    def show_about(self):
        """Exibe a caixa de diálogo Sobre"""
        QMessageBox.about(
            self, 
            "Sobre PyGNOME Interface",
            "<h1>PyGNOME Interface</h1>"
            "<p>Uma interface gráfica para o PyGNOME (General NOAA Operational Modeling Environment)</p>"
            "<p>Versão: 1.0</p>"
            "<p>Desenvolvido com PySide6</p>"
        )

# Função principal que será chamada para iniciar a aplicação
def main():
    app = QApplication(sys.argv)
    
    # Criar e mostrar a janela principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()