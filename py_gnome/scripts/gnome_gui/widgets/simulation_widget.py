import os
import datetime
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QGroupBox, QLabel, QPushButton, QProgressBar,
                              QTextEdit, QComboBox, QTabWidget, QFileDialog,
                              QMessageBox, QCheckBox, QFrame, QScrollArea,
                              QSizePolicy, QSplitter, QStackedWidget)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QThread, QSize, QMetaObject, Q_ARG
from PySide6.QtGui import QColor, QTextCursor, QFont, QPixmap, QIcon, QPalette, QBrush, QLinearGradient

# Verificar se o PyGNOME está disponível
try:
    import gnome
    import gnome.scripting as gs
    PYGNOME_AVAILABLE = True
except ImportError:
    PYGNOME_AVAILABLE = False
    print("PyGNOME não está instalado. O aplicativo funcionará em modo de demonstração.")


class LogConsole(QTextEdit):
    """Console para exibir mensagens de log da simulação"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setMinimumHeight(250)
        
        # Melhorar aparência
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: Consolas, Courier New, monospace;
                font-size: 10pt;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        # Configurar fonte monoespaçada
        font = QFont("Consolas", 10)
        self.setFont(font)
        
        # Configurar cores para diferentes tipos de mensagens
        self.colors = {
            'info': QColor(220, 220, 220),    # Cinza claro
            'warning': QColor(255, 170, 0),   # Laranja
            'error': QColor(255, 80, 80),     # Vermelho
            'success': QColor(100, 255, 100), # Verde
            'debug': QColor(160, 160, 160)    # Cinza
        }
        
    def log(self, message, msg_type='info'):
        """Adiciona uma mensagem de log com formatação"""
        self.setTextColor(self.colors.get(msg_type, self.colors['info']))
        
        # Adicionar timestamp
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        prefix = f"[{timestamp}] "
        
        # Adicionar prefixo de tipo
        if msg_type == 'error':
            prefix += "ERRO: "
        elif msg_type == 'warning':
            prefix += "AVISO: "
        elif msg_type == 'success':
            prefix += "SUCESSO: "
        elif msg_type == 'debug':
            prefix += "DEBUG: "
            
        # Adicionar mensagem com prefixo
        self.append(prefix + message)
        
        # Rolar para o final
        self.moveCursor(QTextCursor.End)


class SimulationThread(QThread):
    """Thread para executar simulações PyGNOME em segundo plano"""
    
    # Sinais para comunicação com o widget principal
    update_progress = Signal(int, str)
    update_visualization = Signal(str)
    simulation_completed = Signal(bool, str)
    
    def __init__(self, config, output_dir):
        super().__init__()
        self.config = config
        self.output_dir = output_dir
        self.stop_requested = False
        
    def run(self):
        """Executa a simulação do PyGNOME"""
        try:
            if not PYGNOME_AVAILABLE:
                # Modo de demonstração - simulação simulada
                self.run_demo_simulation()
                return
                
            # Configurações do modelo
            model_config = self.config.get('model', {})
            start_time = model_config.get('start_time')
            duration = model_config.get('duration', 24)  # Padrão: 24 horas
            time_step = model_config.get('time_step', 900)  # Padrão: 15 minutos
            
            # Inicializar o modelo
            self.update_progress.emit(5, "Inicializando modelo...")
            model = gs.Model(
                start_time=start_time,
                duration=gs.hours(duration),
                time_step=time_step
            )
            
            # Configurar movers
            self.update_progress.emit(15, "Configurando movers...")
            movers_config = self.config.get('movers', [])
            self.setup_movers(model, movers_config)
            
            # Configurar derramamento
            self.update_progress.emit(25, "Configurando derramamento...")
            spill_config = self.config.get('spill', {})
            self.setup_spill(model, spill_config)
            
            # Configurar intemperismo se necessário
            weatherers_config = self.config.get('weatherers', {})
            if weatherers_config.get('enabled', False):
                self.update_progress.emit(35, "Configurando processos de intemperismo...")
                self.setup_weatherers(model, weatherers_config)
                
            # Configurar outputters
            self.update_progress.emit(45, "Configurando saídas...")
            output_config = self.config.get('output', {})
            self.setup_outputters(model, output_config, self.output_dir)
            
            # Preparar para a simulação
            self.update_progress.emit(50, "Preparando simulação...")
            model.setup_model_run()
            
            # Executar o modelo
            total_steps = int(duration * 3600 / time_step)
            step = 0
            
            self.update_progress.emit(55, "Iniciando simulação...")
            
            while step < total_steps and not self.stop_requested:
                # Executar um passo da simulação
                model.step()
                step += 1
                
                # Calcular o progresso
                progress = 55 + int((step / total_steps) * 45)
                self.update_progress.emit(progress, f"Executando passo {step}/{total_steps}...")
                
                # Se há imagens geradas, mostrar a mais recente
                if output_config.get('renderer', {}).get('enabled', False):
                    image_dir = os.path.join(self.output_dir, 'frames')
                    if os.path.exists(image_dir):
                        images = [f for f in os.listdir(image_dir) if f.endswith('.png') or f.endswith('.jpg')]
                        if images:
                            # Ordenar por nome (geralmente contém timestamp)
                            images.sort()
                            latest_image = os.path.join(image_dir, images[-1])
                            self.update_visualization.emit(latest_image)
            
            if self.stop_requested:
                self.update_progress.emit(100, "Simulação interrompida pelo usuário.")
                self.simulation_completed.emit(False, "Simulação interrompida pelo usuário.")
            else:
                # Finalizar a simulação
                self.update_progress.emit(99, "Finalizando simulação...")
                model.complete_run()
                
                self.update_progress.emit(100, "Simulação concluída com sucesso!")
                self.simulation_completed.emit(True, "Simulação concluída com sucesso!")
                
        except Exception as e:
            self.update_progress.emit(100, f"Erro: {str(e)}")
            self.simulation_completed.emit(False, f"Erro na simulação: {str(e)}")
    
    def setup_movers(self, model, movers_config):
        """Configura movers para o modelo"""
        for mover_config in movers_config:
            if not mover_config.get('enabled', True):
                continue
                
            mover_type = mover_config.get('type')
            
            if mover_type == 'wind':
                if mover_config.get('constant', True):
                    # Vento constante
                    speed = mover_config.get('speed', 5.0)
                    direction = mover_config.get('direction', 0.0)
                    
                    # Converter direção de (para onde vai) para (de onde vem)
                    wind_from_direction = (direction + 180) % 360
                    
                    wind = gs.constant_wind(speed, wind_from_direction)
                else:
                    # Vento de arquivo
                    wind_file = mover_config.get('file')
                    if wind_file and os.path.exists(wind_file):
                        wind = gs.Wind(filename=wind_file)
                    else:
                        continue
                        
                # Adicionar WindMover
                wind_mover = gs.WindMover(wind)
                
                # Configurar windage
                windage_range = mover_config.get('windage_range', [0.01, 0.04])
                windage_persist = mover_config.get('windage_persist', 900)
                wind_mover.windage_range = windage_range
                wind_mover.windage_persist = windage_persist
                
                model.movers += wind_mover
                
            elif mover_type == 'current':
                if mover_config.get('constant', False):
                    # Corrente constante
                    u = mover_config.get('u', 0.1)
                    v = mover_config.get('v', 0.0)
                    
                    # Criar vetor velocidade (u, v, 0)
                    current_mover = gs.SimpleMover((u, v, 0))
                else:
                    # Corrente de arquivo
                    current_file = mover_config.get('file')
                    if current_file and os.path.exists(current_file):
                        if current_file.lower().endswith('.nc'):
                            # Arquivo NetCDF
                            current = gs.GridCurrent.from_netCDF(current_file)
                            current_mover = gs.CurrentMover(current=current)
                        else:
                            # Outros formatos não suportados nesta implementação
                            continue
                    else:
                        continue
                        
                model.movers += current_mover
                
            elif mover_type == 'random':
                # Difusão
                if mover_config.get('is_3d', False):
                    # Difusão 3D
                    random_mover = gs.RandomMover3D(
                        vertical_diffusion_coef_above_ml=mover_config.get('vertical_diffusion_coef_above_ml', 5),
                        vertical_diffusion_coef_below_ml=mover_config.get('vertical_diffusion_coef_below_ml', 0.5),
                        horizontal_diffusion_coef_above_ml=mover_config.get('horizontal_diffusion_coef_above_ml', 100000),
                        horizontal_diffusion_coef_below_ml=mover_config.get('horizontal_diffusion_coef_below_ml', 10000),
                        mixed_layer_depth=mover_config.get('mixed_layer_depth', 10)
                    )
                else:
                    # Difusão 2D
                    random_mover = gs.RandomMover(
                        diffusion_coef=mover_config.get('diffusion_coef', 100000)
                    )
                    
                model.movers += random_mover
    
    def setup_spill(self, model, spill_config):
        """Configura o derramamento para o modelo"""
        if not spill_config:
            return
        
        # Parâmetros comuns
        start_position = spill_config.get('start_position', (-144.0, 48.5, 0.0))
        release_time = spill_config.get('release_time')
        num_elements = spill_config.get('num_elements', 1000)
        amount = spill_config.get('amount', 1000)
        units = spill_config.get('units', 'bbl')
        
        # Verificar se é contínuo ou instantâneo
        if spill_config.get('continuous', False):
            release_duration = spill_config.get('release_duration', 24)
            end_release_time = release_time + gs.hours(release_duration)
        else:
            end_release_time = None
        
        # Verificar tipo de substância
        if spill_config.get('substance_type') == 'oil':
            # Derramamento de óleo
            oil_file = spill_config.get('oil_file')
            if oil_file and os.path.exists(oil_file):
                substance = gs.GnomeOil(filename=oil_file)
            else:
                # Usar óleo padrão se não for especificado
                substance = None
        else:
            # Traçador conservativo
            substance = None
            
        # Criar spill
        spill = gs.surface_point_line_spill(
            release_time=release_time,
            start_position=start_position,
            num_elements=num_elements,
            end_release_time=end_release_time,
            amount=amount,
            units=units,
            substance=substance
        )
        
        # Adicionar ao modelo
        model.spills += spill
    
    def setup_weatherers(self, model, weatherers_config):
        """Configura processos de intemperismo para o modelo"""
        if not weatherers_config.get('enabled', False):
            return
            
        # Importar weatherers corretamente
        try:
            from gnome.weatherers import Evaporation, NaturalDispersion, Emulsification
            from gnome.weatherers import Dissolution, Sedimentation, Biodegradation
        except ImportError as e:
            self.update_progress.emit(100, f"Erro ao importar módulos de intemperismo: {str(e)}")
            return
            
        # Adicionar processos de intemperismo conforme configurado
        if weatherers_config.get('evaporation', False):
            model.weatherers += Evaporation()
            
        if weatherers_config.get('dispersion', False):
            model.weatherers += NaturalDispersion()
            
        if weatherers_config.get('emulsification', False):
            model.weatherers += Emulsification()
            
        if weatherers_config.get('dissolution', False):
            model.weatherers += Dissolution()
            
        if weatherers_config.get('sedimentation', False):
            model.weatherers += Sedimentation()
            
        if weatherers_config.get('biodegradation', False):
            model.weatherers += Biodegradation()
    
    def setup_outputters(self, model, output_config, output_dir):
        """Configura outputters para o modelo"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Configurar NetCDF outputter
        netcdf_config = output_config.get('netcdf', {})
        if netcdf_config.get('enabled', True):
            netcdf_file = os.path.join(output_dir, 'trajectory.nc')
            output_timestep = netcdf_config.get('output_timestep', 3600)  # Padrão: 1 hora
            
            model.outputters += gs.NetCDFOutput(
                netcdf_file,
                which_data=netcdf_config.get('data_level', 'standard'),
                output_timestep=output_timestep
            )
            
        # Configurar Renderer outputter
        renderer_config = output_config.get('renderer', {})
        if renderer_config.get('enabled', True):
            images_dir = os.path.join(output_dir, 'frames')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                
            output_timestep = renderer_config.get('output_timestep', 21600)  # Padrão: 6 horas
            size = renderer_config.get('size', (800, 600))
            
            try:
                # Verificar se o Renderer requer um mapa
                import inspect
                renderer_params = inspect.signature(gs.Renderer.__init__).parameters
                
                renderer_kwargs = {
                    'output_timestep': output_timestep,
                    'size': size,
                    'draw_ontop': 'forecast',
                    'formats': ['.png']
                }
                
                # Verificar como configurar o Renderer com base na assinatura
                if 'map_filename' in renderer_params:
                    # Neste caso, o primeiro parâmetro é o map_filename
                    # Não incluir no kwargs, passar como primeiro argumento
                    frame_path = os.path.join(images_dir, 'frame')
                    renderer = gs.Renderer(None, output_dir=frame_path, **renderer_kwargs)
                else:
                    # Usar como primeiro argumento o caminho para frames
                    frame_path = os.path.join(images_dir, 'frame')
                    renderer = gs.Renderer(frame_path, **renderer_kwargs)
                
                model.outputters += renderer
            except Exception as e:
                self.update_progress.emit(55, f"Aviso: Não foi possível configurar o renderizador: {str(e)}")
                self.update_progress.emit(55, "Continuando sem renderização visual.")
            
        # Configurar KML outputter
        kml_config = output_config.get('kml', {})
        if kml_config.get('enabled', False):
            kml_file = os.path.join(output_dir, 'trajectory.kmz')
            output_timestep = kml_config.get('output_timestep', 21600)  # Padrão: 6 horas
            
            model.outputters += gs.KMZOutput(
                kml_file,
                output_timestep=output_timestep
            )
    
    def run_demo_simulation(self):
        """Executa uma simulação de demonstração quando o PyGNOME não está disponível"""
        total_steps = 20
        
        # Simular fase de inicialização
        self.update_progress.emit(5, "Inicializando modelo (modo demo)...")
        self.msleep(500)
        
        self.update_progress.emit(15, "Configurando movers (modo demo)...")
        self.msleep(500)
        
        self.update_progress.emit(25, "Configurando derramamento (modo demo)...")
        self.msleep(500)
        
        self.update_progress.emit(35, "Configurando processos de intemperismo (modo demo)...")
        self.msleep(500)
        
        self.update_progress.emit(45, "Configurando saídas (modo demo)...")
        self.msleep(500)
        
        self.update_progress.emit(50, "Preparando simulação (modo demo)...")
        self.msleep(1000)
        
        # Simular passos da simulação
        for step in range(total_steps):
            if self.stop_requested:
                self.update_progress.emit(100, "Simulação de demonstração interrompida.")
                self.simulation_completed.emit(False, "Simulação de demonstração interrompida.")
                return
                
            progress = 55 + int((step + 1) / total_steps * 45)
            self.update_progress.emit(progress, f"Executando passo {step+1}/{total_steps} (modo demo)...")
            self.msleep(1000)  # Cada passo leva 1 segundo em modo demo
        
        self.update_progress.emit(100, "Simulação de demonstração concluída!")
        self.simulation_completed.emit(True, "Simulação de demonstração concluída!")
    
    def stop(self):
        """Solicita parada da simulação"""
        self.stop_requested = True


class SimulationWidget(QWidget):
    """Widget para controle e visualização da simulação"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.simulation_config = {}
        self.simulation_running = False
        self.simulation_thread = None
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation_time)
        self.simulation_start_time = None
        
        # Lista para armazenar animações da barra de progresso
        self.progress_animations = []
        
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # Espaçamento entre grupos
        
        # =====================================================
        # SEÇÃO 1: CONTROLES DE SIMULAÇÃO
        # =====================================================
        controls_group = QGroupBox("Controles de Simulação")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(15, 20, 15, 15)
        controls_layout.setSpacing(20)
        
        # Botões de controle
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Botão Iniciar
        self.run_button = QPushButton("▶ Iniciar Simulação")
        self.run_button.setObjectName("run_button")  # Para estilização específica
        self.run_button.setMinimumWidth(200)
        self.run_button.setMinimumHeight(40)
        self.run_button.clicked.connect(self.start_simulation)
        
        # Botão Parar
        self.stop_button = QPushButton("⏹ Parar Simulação")
        self.stop_button.setObjectName("stop_button")  # Para estilização específica
        self.stop_button.setMinimumWidth(200)
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_simulation)
        
        # Botão para Simulação Teste
        self.test_button = QPushButton("🧪 Executar Simulação Teste")
        self.test_button.setMinimumWidth(200)
        self.test_button.setMinimumHeight(40)
        self.test_button.clicked.connect(self.run_test_simulation)
        self.test_button.setStyleSheet("""
            background-color: #8B5CF6;
            color: white;
            font-weight: bold;
        """)
        
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.test_button)
        
        # Opções de simulação
        options_frame = QFrame()
        options_layout = QFormLayout(options_frame)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(10)
        
        # Viewport de simulação
        self.viewport_combo = QComboBox()
        self.viewport_combo.addItems(["2D (Padrão)", "3D (Experimental)"])
        self.viewport_combo.setMinimumHeight(30)
        self.viewport_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 150px;
                background-color: white;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #bdc3c7;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
        """)
        
        # Exibir gráficos em tempo real
        self.realtime_graphs = QCheckBox("Exibir gráficos em tempo real")
        self.realtime_graphs.setChecked(True)
        self.realtime_graphs.setMinimumHeight(30)
        self.realtime_graphs.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #bdc3c7;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #3498db;
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # Salvar log
        self.save_log = QCheckBox("Salvar log da simulação")
        self.save_log.setChecked(True)
        self.save_log.setMinimumHeight(30)
        self.save_log.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #bdc3c7;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #3498db;
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        options_layout.addRow("Visualização:", self.viewport_combo)
        options_layout.addRow("", self.realtime_graphs)
        options_layout.addRow("", self.save_log)
        
        # Adicionar botões e opções ao layout
        controls_layout.addWidget(buttons_frame)
        controls_layout.addWidget(options_frame)
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # =====================================================
        # SEÇÃO 2: PROGRESSO DA SIMULAÇÃO
        # =====================================================
        progress_group = QGroupBox("Progresso da Simulação")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(15, 20, 15, 15)
        progress_layout.setSpacing(15)
        
        # Barra de progresso aprimorada
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% concluído")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
                background-color: #ecf0f1;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #3498db, stop:1 #2980b9);
                width: 10px;
                border-radius: 2px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status da simulação
        self.progress_label = QLabel("Simulação pronta para iniciar")
        self.progress_label.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
            border: 1px solid #ecf0f1;
        """)
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        # Timer da simulação
        self.time_label = QLabel("Tempo de simulação: 00:00:00")
        self.time_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
            border: 1px solid #ecf0f1;
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.time_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # =====================================================
        # SEÇÃO 3: ABAS DE RESULTADOS
        # =====================================================
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dcdde1;
                border-radius: 3px;
            }
        """)
        
        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(5, 5, 5, 5)
        results_layout.setSpacing(5)
        
        # Abas de resultados
        self.results_tabs = QTabWidget()
        self.results_tabs.setDocumentMode(True)
        
        # CORREÇÃO: Estilos de abas corrigidos para melhor visibilidade durante hover
        self.results_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                padding: 5px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 15px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                color: #2c3e50; /* Cor do texto definida explicitamente */
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                color: #2c3e50; /* Mantém a mesma cor do texto */
            }
            QTabBar::tab:hover:!selected {
                background: #d6dbdf;
                color: #2c3e50; /* Garante que o texto permaneça visível durante hover */
            }
        """)
        
        # Aba de console de log
        self.log_console = LogConsole()
        self.results_tabs.addTab(self.log_console, "Log")
        
        # Aba de resumo da simulação
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                color: #2c3e50;
            }
        """)
        summary_layout.addWidget(self.summary_text)
        self.results_tabs.addTab(self.summary_tab, "Resumo")
        
        # Aba de visualização
        self.viz_tab = QWidget()
        viz_layout = QVBoxLayout(self.viz_tab)
        self.viz_label = QLabel("A visualização será exibida aqui durante a simulação")
        self.viz_label.setAlignment(Qt.AlignCenter)
        self.viz_label.setMinimumHeight(350)
        self.viz_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px dashed #bdc3c7;
                border-radius: 3px;
                color: #7f8c8d;
                font-style: italic;
                padding: 10px;
            }
        """)
        viz_layout.addWidget(self.viz_label)
        
        # Botão para abrir visualização externa
        self.open_viz_button = QPushButton("Abrir Visualizador Externo")
        self.open_viz_button.setEnabled(False)
        self.open_viz_button.setMinimumHeight(30)
        self.open_viz_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1c2833;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #dcdde1;
            }
        """)
        self.open_viz_button.clicked.connect(self.open_external_visualizer)
        viz_layout.addWidget(self.open_viz_button)
        
        self.results_tabs.addTab(self.viz_tab, "Visualização")
        
        results_layout.addWidget(self.results_tabs)
        main_layout.addWidget(results_frame)
        
        # Inicializar console de log
        self.log_console.log("Interface PyGNOME inicializada.", "info")
        if PYGNOME_AVAILABLE:
            self.log_console.log(f"PyGNOME versão {gnome.__version__} detectado.", "success")
        else:
            self.log_console.log("PyGNOME não foi encontrado. Executando em modo de demonstração.", "warning")
            
    def run_test_simulation(self):
        """Executa uma simulação de teste com valores pré-configurados"""
        try:
            # Verificar se PyGNOME está disponível
            if not PYGNOME_AVAILABLE:
                self.log_console.log("PyGNOME não disponível. Executando em modo de demonstração.", "warning")
                self.run_demo_simulation()
                return
                
            import datetime
            import os
            import gnome
            import gnome.scripting as gs
            
            # Limpar o console de log
            self.log_console.clear()
            self.log_console.log("Iniciando simulação de teste...", "info")
            
            # Atualizar UI
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setValue(0)
            self.progress_label.setText("Iniciando simulação de teste...")
            self.simulation_start_time = datetime.datetime.now()
            self.time_label.setText("Tempo de simulação: 00:00:00")
            self.simulation_timer.start(1000)  # Atualizar a cada segundo
            
            # Limpar visualização
            self.viz_label.setText("A visualização será exibida aqui durante a simulação")
            self.viz_label.setPixmap(QPixmap())  # Limpar pixmap
            
            # Atualizar status
            self.simulation_running = True
            
            # Criar diretório de saída
            output_dir = './output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Criar diretório para frames
            images_dir = os.path.join(output_dir, 'frames')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                
            # =====================================================
            # CARREGAR MÓDULOS DE INTEMPERISMO
            # =====================================================
            try:
                from gnome.weatherers import Evaporation, NaturalDispersion, Emulsification
            except ImportError as e:
                self.log_console.log(f"Erro ao importar módulos de intemperismo: {str(e)}", "error")
                self.log_console.log("A simulação prosseguirá sem processos de intemperismo.", "warning")
                weatherers_available = False
            else:
                weatherers_available = True
            
            # =====================================================
            # CONFIGURAÇÃO DO MODELO
            # =====================================================
            self.log_console.log("Iniciando configuração do modelo...", "info")
            start_time = datetime.datetime.now()
            
            model = gs.Model(
                start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                duration=gs.hours(23),
                time_step=900,  # 15 minutos
                uncertain=False
            )
            
            # =====================================================
            # CONFIGURAÇÃO DO AMBIENTE
            # =====================================================
            self.log_console.log("Configurando ambiente...", "info")
            water = gs.Water(temperature=15.0, salinity=35.0)
            
            # CORREÇÃO: Substituindo a criação do objeto Waves
            try:
                # Tentar criar o objeto Waves sem parâmetros
                waves = gs.Waves()
                # Se for bem-sucedido, tente definir a altura da onda como propriedade
                if hasattr(waves, 'wave_height'):
                    waves.wave_height = 1.0
                self.log_console.log("- Ondas: configurado com sucesso", "info")
                model.environment += waves
            except Exception as e:
                self.log_console.log(f"- Erro ao configurar ondas: {str(e)}", "warning")
                self.log_console.log("  Continuando simulação sem o componente de ondas", "info")
            
            model.environment += water
            
            # =====================================================
            # CONFIGURAÇÃO DOS MOVERS
            # =====================================================
            self.log_console.log("Configurando movers...", "info")
            
            # Vento constante
            self.log_console.log("- Vento constante: 5 m/s, do norte", "info")
            wind = gs.constant_wind(speed=5.0, direction=0)  # do norte
            wind_mover = gs.WindMover(wind)
            wind_mover.windage_range = (0.01, 0.04)  # 1-4%
            wind_mover.windage_persist = 900
            model.movers += wind_mover
            
            # Corrente constante
            self.log_console.log("- Corrente constante: 0.2 m/s para leste", "info")
            current_mover = gs.SimpleMover(velocity=(0.2, 0.0, 0.0))  # para leste
            model.movers += current_mover
            
            # Difusão
            self.log_console.log("- Difusão: 100000 cm²/s", "info")
            diffusion_mover = gs.RandomMover(diffusion_coef=100000)  # cm²/s
            model.movers += diffusion_mover
            
            # =====================================================
            # CONFIGURAÇÃO DO DERRAMAMENTO
            # =====================================================
            self.log_console.log("Configurando derramamento...", "info")
            
            # CORREÇÃO: Usar uma abordagem mais robusta para carregar óleo
            try:
                # Tentar carregar diferentes tipos de óleo - tentar opções mais leves
                try:
                    oil = gs.GnomeOil('oil_jetfuels')  # Começar com combustível de jato (leve)
                    self.log_console.log("- Usando óleo: Jet Fuel", "info")
                except Exception as e1:
                    try:
                        oil = gs.GnomeOil('oil_diesel')  # Tentar diesel (leve a médio)
                        self.log_console.log("- Usando óleo: Diesel", "info")
                    except Exception as e2:
                        try:
                            oil = gs.GnomeOil('oil_gas')  # Tentar combustível gasoso (leve)
                            self.log_console.log("- Usando óleo: Gas Oil", "info")
                        except Exception as e3:
                            try:
                                oil = gs.GnomeOil('oil_ans_mp')  # Por último, ANS (pode ser pesado)
                                self.log_console.log("- Usando óleo: Alaska North Slope", "info")
                            except Exception as e4:
                                # Se tudo falhar, usar None (sem óleo - traçador conservativo)
                                self.log_console.log("- Usando substância não-intemperizante para demonstração", "info")
                                oil = None
            except Exception as e:
                self.log_console.log(f"Erro ao carregar óleo: {str(e)}", "warning")
                self.log_console.log("- Usando substância não-intemperizante para demonstração", "info")
                oil = None

            # CORREÇÃO: Configurar derramamento de forma robusta
            # Usar substância conservativa se não for possível usar óleo
            self.log_console.log("- Posição: -70.0°, 42.0° (Costa de Massachusetts)", "info")
            self.log_console.log("- Quantidade: 1000 barris", "info")
            self.log_console.log("- Número de elementos: 1000", "info")
            spill = gs.surface_point_line_spill(
                release_time=start_time,
                start_position=(-70.0, 42.0, 0.0),  # costa de Massachusetts
                num_elements=1000,
                amount=1000,
                units='bbl',
                substance=oil
            )
            model.spills += spill

            # CORREÇÃO: Configurar intemperismo apenas se óleo estiver disponível
            weatherers_enabled = weatherers_available and oil is not None
            if weatherers_enabled:
                self.log_console.log("Configurando processos de intemperismo...", "info")
                self.log_console.log("- Evaporação: Ativada", "info")
                model.weatherers += Evaporation()
                self.log_console.log("- Dispersão Natural: Ativada", "info")
                model.weatherers += NaturalDispersion()
                self.log_console.log("- Emulsificação: Ativada", "info")
                model.weatherers += Emulsification()
            else:
                self.log_console.log("Intemperismo desativado - usando substância não-intemperizante", "warning")
            
            # =====================================================
            # CONFIGURAÇÃO DAS SAÍDAS
            # =====================================================
            self.log_console.log("Configurando saídas...", "info")
            
            # NetCDF
            self.log_console.log("- NetCDF: trajetos a cada 1 hora", "info")
            model.outputters += gs.NetCDFOutput(
                os.path.join(output_dir, 'trajectory.nc'),
                output_timestep=gs.hours(1)
            )
            
            # CORREÇÃO: Imagens com tratamento de erro
            self.log_console.log("- Imagens: renders a cada 6 horas (800x600)", "info")
            try:
                # Algumas versões do PyGNOME podem precisar de um mapa
                import inspect
                renderer_params = inspect.signature(gs.Renderer.__init__).parameters
                
                renderer_kwargs = {
                    'output_timestep': gs.hours(6),
                    'size': (800, 600),
                    'formats': ['.png']
                }
                
                # Verificar como configurar o Renderer com base na assinatura
                if 'map_filename' in renderer_params:
                    # Neste caso, o primeiro parâmetro é o map_filename
                    # Não incluir no kwargs, passar como primeiro argumento
                    frame_path = os.path.join(images_dir, 'frame')
                    self.log_console.log(f"- Configurando renderer com prefixo: {frame_path}", "info")
                    renderer = gs.Renderer(None, output_dir=frame_path, **renderer_kwargs)
                else:
                    # Usar como primeiro argumento o caminho para frames
                    frame_path = os.path.join(images_dir, 'frame')
                    self.log_console.log(f"- Configurando renderer com prefixo: {frame_path}", "info")
                    renderer = gs.Renderer(frame_path, **renderer_kwargs)
                
                model.outputters += renderer
                self.log_console.log("- Renderer configurado com sucesso", "info")
            except Exception as e:
                self.log_console.log(f"Aviso ao configurar renderer: {str(e)}", "warning")
                self.log_console.log("Continuando simulação sem renderização visual", "info")
            
            # =====================================================
            # EXECUÇÃO DA SIMULAÇÃO
            # =====================================================
            self.log_console.log("Configurações concluídas. Iniciando simulação...", "info")
            self.progress_bar.setValue(10)
            self.progress_label.setText("Preparando simulação...")
            
            model.setup_model_run()
            
            total_steps = int(23 * 3600 / 900)  # 23 horas / 15 minutos
            for step in range(total_steps):
                if self.simulation_running == False:
                    break
                    
                model.step()
                
                progress = int(10 + (step / total_steps) * 90)
                self.progress_bar.setValue(progress)
                self.progress_label.setText(f"Simulação em andamento: passo {step+1}/{total_steps}")
                
                # Processar eventos para manter a UI responsiva
                QApplication.processEvents()
                
                # Se há imagens geradas, mostrar a mais recente
                if os.path.exists(images_dir):
                    images = [f for f in os.listdir(images_dir) if f.endswith('.png')]
                    if images:
                        latest_image = os.path.join(images_dir, sorted(images)[-1])
                        self.update_visualization(latest_image)
            
            # Finalizar simulação
            if self.simulation_running:
                model.complete_run()
                self.log_console.log("Simulação concluída com sucesso!", "success")
                self.progress_bar.setValue(100)
                self.progress_label.setText("Simulação concluída!")
                
                # Atualizar status
                self.simulation_running = False
                self.run_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.simulation_timer.stop()
            else:
                self.log_console.log("Simulação interrompida pelo usuário.", "warning")
        
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            self.log_console.log(f"Erro na simulação: {str(e)}", "error")
            self.log_console.log(f"Detalhes: {traceback_str}", "error")
            self.progress_bar.setValue(100)
            self.progress_label.setText(f"Erro: {str(e)}")
            
            # Atualizar status
            self.simulation_running = False
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.simulation_timer.stop()
            
    def run_demo_simulation(self):
        """Executa uma simulação de demonstração"""
        # Resetar UI
        self.log_console.clear()
        self.log_console.log("Iniciando simulação de demonstração...", "info")
        
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Iniciando simulação de demonstração...")
        self.simulation_start_time = datetime.datetime.now()
        self.time_label.setText("Tempo de simulação: 00:00:00")
        self.simulation_timer.start(1000)  # Atualizar a cada segundo
        
        self.simulation_running = True
        
        # Simulação em thread separada para não travar a UI
        self.simulation_thread = QThread()
        self.simulation_thread.run = self._run_demo
        self.simulation_thread.start()
    
    def _run_demo(self):
        """Thread separada para simulação de demo"""
        total_steps = 20
        
        # Simular fase de inicialização
        QMetaObject.invokeMethod(self, "_update_progress", 
                                Qt.QueuedConnection, 
                                Q_ARG(int, 5), 
                                Q_ARG(str, "Inicializando modelo (modo demo)..."))
        QThread.msleep(500)
        
        QMetaObject.invokeMethod(self, "_update_progress", 
                                Qt.QueuedConnection, 
                                Q_ARG(int, 15), 
                                Q_ARG(str, "Configurando movers (modo demo)..."))
        QThread.msleep(500)
        
        # ... restante da simulação demo ...
            
    def set_simulation_config(self, config):
        """Define a configuração da simulação"""
        self.simulation_config = config
        self.log_console.log("Configuração de simulação atualizada.", "info")
        self.update_summary()
        
    def update_summary(self):
        """Atualiza o resumo da simulação baseado na configuração atual"""
        if not self.simulation_config:
            self.summary_text.setText("Configuração de simulação não disponível.")
            return
            
        summary = "<h2>Resumo da Simulação</h2>"
        
        # Modelo
        model_config = self.simulation_config.get('model', {})
        summary += "<h3>Modelo</h3>"
        summary += f"<p><b>Tempo Inicial:</b> {model_config.get('start_time', 'Não definido')}</p>"
        summary += f"<p><b>Duração:</b> {model_config.get('duration', 0)} horas</p>"
        summary += f"<p><b>Passo de Tempo:</b> {model_config.get('time_step', 0)} segundos</p>"
        summary += f"<p><b>Método Numérico:</b> {model_config.get('num_method', 'rk2').upper()}</p>"
        
        # Movers
        movers_config = self.simulation_config.get('movers', [])
        summary += "<h3>Movers</h3>"
        if movers_config:
            summary += "<ul>"
            for mover in movers_config:
                if mover.get('type') == 'wind' and mover.get('enabled', True):
                    if mover.get('constant', False):
                        summary += f"<li>Vento Constante: {mover.get('speed', 0)} m/s, {mover.get('direction', 0)}°</li>"
                    else:
                        summary += f"<li>Vento de Arquivo: {os.path.basename(mover.get('file', 'Não definido'))}</li>"
                elif mover.get('type') == 'current' and mover.get('enabled', True):
                    if mover.get('constant', False):
                        summary += f"<li>Corrente Constante: u={mover.get('u', 0)} m/s, v={mover.get('v', 0)} m/s</li>"
                    else:
                        summary += f"<li>Corrente de Arquivo: {os.path.basename(mover.get('file', 'Não definido'))}</li>"
                elif mover.get('type') == 'random' and mover.get('enabled', True):
                    if mover.get('is_3d', False):
                        summary += "<li>Difusão 3D</li>"
                    else:
                        summary += f"<li>Difusão 2D: coef={mover.get('diffusion_coef', 0)} cm²/s</li>"
            summary += "</ul>"
        else:
            summary += "<p>Nenhum mover configurado.</p>"
        
        # Derramamento
        spill_config = self.simulation_config.get('spill', {})
        summary += "<h3>Derramamento</h3>"
        if spill_config:
            summary += f"<p><b>Posição:</b> Lon={spill_config.get('start_position', [0, 0, 0])[0]}°, Lat={spill_config.get('start_position', [0, 0, 0])[1]}°, Profundidade={spill_config.get('start_position', [0, 0, 0])[2]} m</p>"
            summary += f"<p><b>Quantidade:</b> {spill_config.get('amount', 0)} {spill_config.get('units', 'bbl')}</p>"
            summary += f"<p><b>Número de Elementos:</b> {spill_config.get('num_elements', 0)}</p>"
            summary += f"<p><b>Tipo de Lançamento:</b> {'Contínuo' if spill_config.get('continuous', False) else 'Instantâneo'}</p>"
            if spill_config.get('continuous', False):
                summary += f"<p><b>Duração do Lançamento:</b> {spill_config.get('release_duration', 0)} horas</p>"
            summary += f"<p><b>Tipo de Substância:</b> {'Óleo' if spill_config.get('substance_type') == 'oil' else 'Traçador Conservativo'}</p>"
            if spill_config.get('substance_type') == 'oil':
                summary += f"<p><b>Arquivo de Óleo:</b> {os.path.basename(spill_config.get('oil_file', 'Não definido'))}</p>"
        else:
            summary += "<p>Configuração de derramamento não disponível.</p>"
        
        # Intemperismo
        weatherers_config = self.simulation_config.get('weatherers', {})
        summary += "<h3>Processos de Intemperismo</h3>"
        if weatherers_config and weatherers_config.get('enabled', False):
            summary += "<ul>"
            if weatherers_config.get('evaporation', False):
                summary += "<li>Evaporação</li>"
            if weatherers_config.get('dispersion', False):
                summary += "<li>Dispersão Natural</li>"
            if weatherers_config.get('emulsification', False):
                summary += "<li>Emulsificação</li>"
            if weatherers_config.get('dissolution', False):
                summary += "<li>Dissolução</li>"
            if weatherers_config.get('sedimentation', False):
                summary += "<li>Sedimentação</li>"
            if weatherers_config.get('biodegradation', False):
                summary += "<li>Biodegradação</li>"
            summary += "</ul>"
        else:
            summary += "<p>Processos de intemperismo desativados.</p>"
        
        # Saídas
        output_config = self.simulation_config.get('output', {})
        summary += "<h3>Saídas</h3>"
        if output_config:
            summary += f"<p><b>Diretório:</b> {output_config.get('output_dir', 'Não definido')}</p>"
            
            summary += "<p><b>Formatos:</b></p><ul>"
            if output_config.get('netcdf', {}).get('enabled', False):
                summary += "<li>NetCDF</li>"
            if output_config.get('renderer', {}).get('enabled', False):
                summary += f"<li>Imagens ({output_config.get('renderer', {}).get('format', 'png').upper()})</li>"
            if output_config.get('kml', {}).get('enabled', False):
                summary += "<li>KMZ (Google Earth)</li>"
            if output_config.get('erma', {}).get('enabled', False):
                summary += "<li>ERMA</li>"
            summary += "</ul>"
        else:
            summary += "<p>Configuração de saídas não disponível.</p>"
        
        self.summary_text.setHtml(summary)
    
    def update_simulation_time(self):
        """Atualiza o tempo decorrido da simulação"""
        if self.simulation_start_time:
            elapsed = datetime.datetime.now() - self.simulation_start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.time_label.setText(f"Tempo de simulação: {time_str}")
    
    def start_simulation(self):
        """Inicia a simulação"""
        if self.simulation_running:
            return
            
        # Verificar se a configuração está disponível
        if not self.simulation_config:
            QMessageBox.warning(
                self, 
                "Configuração Ausente",
                "Não há configuração de simulação disponível. Configure os parâmetros antes de iniciar a simulação."
            )
            return
            
        # Recuperar configurações
        output_config = self.simulation_config.get('output', {})
        output_dir = output_config.get('output_dir', os.path.join(os.getcwd(), "output"))
        
        # Verificar se o diretório existe ou pode ser criado
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                QMessageBox.critical(
                    self,
                    "Erro de Diretório",
                    f"Não foi possível criar o diretório de saída: {str(e)}"
                )
                return
                
        # Preparar UI para simulação
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Iniciando simulação...")
        self.simulation_start_time = datetime.datetime.now()
        self.time_label.setText("Tempo de simulação: 00:00:00")
        self.simulation_timer.start(1000)  # Atualizar a cada segundo
        
        # Limpar o console de log
        self.log_console.clear()
        self.log_console.log("Iniciando nova simulação...", "info")
        
        # Limpar visualização
        self.viz_label.setText("A visualização será exibida aqui durante a simulação")
        self.viz_label.setPixmap(QPixmap())  # Limpar pixmap
        
        # Atualizar status
        self.simulation_running = True
        
        # Iniciar thread da simulação
        self.simulation_thread = SimulationThread(self.simulation_config, output_dir)
        self.simulation_thread.update_progress.connect(self.update_progress)
        self.simulation_thread.update_visualization.connect(self.update_visualization)
        self.simulation_thread.simulation_completed.connect(self.on_simulation_completed)
        self.simulation_thread.start()
        
        # Log
        self.log_console.log("Thread de simulação iniciada.", "info")
        
    def stop_simulation(self):
        """Para a simulação em execução"""
        if self.simulation_running and self.simulation_thread:
            self.progress_label.setText("Solicitando parada da simulação...")
            self.log_console.log("Solicitação de parada enviada. Aguardando conclusão...", "warning")
            self.simulation_thread.stop()
            self.simulation_running = False
            
    def update_progress(self, progress, message):
        """Atualiza o progresso da simulação"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        self.log_console.log(message, "info")
        
    def update_visualization(self, image_path):
        """Atualiza a visualização da simulação"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            
            # Verificar se a imagem foi carregada corretamente
            if not pixmap.isNull():
                # Redimensionar a imagem para caber na label
                label_size = self.viz_label.size()
                scaled_pixmap = pixmap.scaled(
                    label_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                self.viz_label.setPixmap(scaled_pixmap)
                self.viz_label.setAlignment(Qt.AlignCenter)
                
                # Ativar botão para abrir visualizador externo
                self.open_viz_button.setEnabled(True)
                
                # Log
                self.log_console.log(f"Visualização atualizada: {os.path.basename(image_path)}", "debug")
                
    def open_external_visualizer(self):
        """Abre o visualizador externo"""
        output_config = self.simulation_config.get('output', {})
        output_dir = output_config.get('output_dir', os.path.join(os.getcwd(), "output"))
        images_dir = os.path.join(output_dir, "frames")
        
        if os.path.exists(images_dir):
            # Tentar abrir o diretório de imagens
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(images_dir)
                elif os.name == 'posix':  # MacOS ou Linux
                    import subprocess
                    subprocess.call(('xdg-open', images_dir))
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Erro ao Abrir Visualizador",
                    f"Não foi possível abrir o diretório de imagens: {str(e)}"
                )
        else:
            QMessageBox.information(
                self, 
                "Diretório Não Encontrado",
                "O diretório de imagens ainda não foi criado. Execute a simulação primeiro."
            )
            
    def on_simulation_completed(self, success, message):
        """Manipula a conclusão da simulação"""
        # Parar o timer
        self.simulation_timer.stop()
        
        # Atualizar UI
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.simulation_running = False
        
        # Log
        if success:
            self.log_console.log(message, "success")
            self.progress_label.setText("Simulação concluída com sucesso!")
        else:
            self.log_console.log(message, "error")
            self.progress_label.setText("Simulação interrompida.")
    
    def reset(self):
        """Redefine o widget para valores padrão"""
        # Parar simulação se estiver em execução
        if self.simulation_running:
            self.stop_simulation()
            
        # Resetar UI
        self.progress_bar.setValue(0)
        self.progress_label.setText("Simulação pronta para iniciar")
        self.time_label.setText("Tempo de simulação: 00:00:00")
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.open_viz_button.setEnabled(False)
        
        # Limpar visualização
        self.viz_label.setText("A visualização será exibida aqui durante a simulação")
        self.viz_label.setPixmap(QPixmap())  # Limpar pixmap
        
        # Limpar console de log
        self.log_console.clear()
        self.log_console.log("Interface PyGNOME inicializada.", "info")
        if PYGNOME_AVAILABLE:
            self.log_console.log(f"PyGNOME versão {gnome.__version__} detectado.", "success")
        else:
            self.log_console.log("PyGNOME não foi encontrado. Executando em modo de demonstração.", "warning")
            
        # Resetar opções
        self.viewport_combo.setCurrentIndex(0)
        self.realtime_graphs.setChecked(True)
        self.save_log.setChecked(True)
        
        # Limpar resumo
        self.summary_text.clear()
        
    def apply_theme(self, dark_mode=False):
        """Aplica o tema (claro/escuro) ao widget"""
        if dark_mode:
            # Tema escuro
            self.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox {
                    border: 1px solid #34495e;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    color: #3498db;
                }
                QComboBox, QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    border-radius: 3px;
                }
                QProgressBar {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                   stop:0 #3498db, stop:1 #2980b9);
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QFrame {
                    background-color: #34495e;
                    border: 1px solid #2c3e50;
                }
                QTabWidget::pane {
                    border: 1px solid #2c3e50;
                    background-color: #34495e;
                }
                QTabBar::tab {
                    background: #2c3e50;
                    border: 1px solid #34495e;
                    color: #ecf0f1;
                }
                QTabBar::tab:selected {
                    background: #34495e;
                    border-bottom-color: #34495e;
                }
                QTabBar::tab:hover:!selected {
                    background: #3c5064;
                }
                QLabel {
                    background-color: transparent;
                    color: #ecf0f1;
                }
            """)
            
            # Ajustes específicos para os botões
            self.run_button.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    font-size: 14px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #27ae60, stop:1 #229954);
                    color: white;
                    border-radius: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #2ecc71, stop:1 #27ae60);
                }
                QPushButton:pressed {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #229954, stop:1 #1e8449);
                }
                QPushButton:disabled {
                    background-color: #7f8c8d;
                    color: #bdc3c7;
                }
            """)
            
            self.stop_button.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    font-size: 14px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #c0392b, stop:1 #a93226);
                    color: white;
                    border-radius: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #e74c3c, stop:1 #c0392b);
                }
                QPushButton:pressed {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                   stop:0 #a93226, stop:1 #922b21);
                }
                QPushButton:disabled {
                    background-color: #7f8c8d;
                    color: #bdc3c7;
                }
            """)
            
            # Ajuste para o label de visualização
            self.viz_label.setStyleSheet("""
                QLabel {
                    background-color: #2c3e50;
                    border: 1px dashed #7f8c8d;
                    border-radius: 3px;
                    color: #bdc3c7;
                    font-style: italic;
                    padding: 10px;
                }
            """)
            
            # Ajuste para os checkboxes
            checkbox_style = """
                QCheckBox {
                    color: #ecf0f1;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #7f8c8d;
                    background-color: #34495e;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #3498db;
                    background-color: #3498db;
                    border-radius: 3px;
                }
            """
            self.realtime_graphs.setStyleSheet(checkbox_style)
            self.save_log.setStyleSheet(checkbox_style)
            
            # Ajuste para combobox
            self.viewport_combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid #7f8c8d;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 150px;
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QComboBox:hover {
                    border: 1px solid #3498db;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 1px;
                    border-left-color: #7f8c8d;
                    border-left-style: solid;
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                    background-color: #2c3e50;
                }
                QComboBox QAbstractItemView {
                    background-color: #34495e;
                    color: #ecf0f1;
                    selection-background-color: #3498db;
                }
            """)
            
            # Ajuste para os labels de status
            self.progress_label.setStyleSheet("""
                font-weight: bold;
                color: #ecf0f1;
                background-color: #34495e;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #2c3e50;
            """)
            
            self.time_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #ecf0f1;
                background-color: #34495e;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #2c3e50;
            """)
            
            # Ajuste para o resumo da simulação
            self.summary_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    border-radius: 3px;
                    padding: 5px;
                }
            """)
            
            # CORREÇÃO: Estilos específicos para as abas no tema escuro
            self.results_tabs.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #2c3e50;
                    background-color: #34495e;
                }
                QTabBar::tab {
                    background: #2c3e50;
                    border: 1px solid #34495e;
                    color: #ecf0f1;
                    padding: 8px 15px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #34495e;
                    border-bottom-color: #34495e;
                    color: #3498db;
                }
                QTabBar::tab:hover:!selected {
                    background: #3c5064;
                    color: #ecf0f1;
                }
            """)
            
        else:
            # Tema claro - voltar para estilos definidos no initUI
            self.setStyleSheet("")
            self.initUI()
            
    # Métodos para utilização com QMetaObject.invokeMethod
    @Slot(int, str)
    def _update_progress(self, progress, message):
        """Método auxiliar para atualizar progresso a partir de outra thread"""
        self.update_progress(progress, message)