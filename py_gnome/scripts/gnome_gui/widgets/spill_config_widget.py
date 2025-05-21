import os
import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                              QGroupBox, QLabel, QDateTimeEdit, QSpinBox, 
                              QDoubleSpinBox, QComboBox, QCheckBox, QRadioButton,
                              QButtonGroup, QFileDialog, QLineEdit, QPushButton,
                              QFrame, QScrollArea, QSizePolicy, QSpacerItem, QGridLayout)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont

class SpillConfigWidget(QWidget):
    """Widget para configuração de derramamento (Spill)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        # Layout principal com espaçamento adequado
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # Espaçamento entre grupos
        
        # Área de scroll para permitir visualização em telas menores
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)  # Espaçamento entre grupos
        
        # =====================================================
        # SEÇÃO 1: PARÂMETROS BÁSICOS DO DERRAMAMENTO
        # =====================================================
        basic_group = QGroupBox("Parâmetros Básicos do Derramamento")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        basic_layout = QFormLayout()
        basic_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        basic_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        basic_layout.setContentsMargins(15, 20, 15, 15)
        basic_layout.setHorizontalSpacing(15)
        basic_layout.setVerticalSpacing(12)
        
        # Posição com layout melhorado
        position_frame = QFrame()
        position_layout = QGridLayout(position_frame)
        position_layout.setContentsMargins(0, 0, 0, 0)
        position_layout.setHorizontalSpacing(10)
        position_layout.setVerticalSpacing(0)
        
        # Usando grid para melhor alinhamento dos campos
        lon_label = QLabel("Longitude:")
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setValue(-144)
        self.lon_spin.setDecimals(5)
        self.lon_spin.setSuffix("°")
        self.lon_spin.setMinimumHeight(30)
        
        lat_label = QLabel("Latitude:")
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setValue(48.5)
        self.lat_spin.setDecimals(5)
        self.lat_spin.setSuffix("°")
        self.lat_spin.setMinimumHeight(30)
        
        depth_label = QLabel("Profundidade:")
        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0, 10000)
        self.depth_spin.setValue(0)
        self.depth_spin.setSuffix(" m")
        self.depth_spin.setMinimumHeight(30)
        
        position_layout.addWidget(lon_label, 0, 0)
        position_layout.addWidget(self.lon_spin, 0, 1)
        position_layout.addWidget(lat_label, 0, 2)
        position_layout.addWidget(self.lat_spin, 0, 3)
        position_layout.addWidget(depth_label, 0, 4)
        position_layout.addWidget(self.depth_spin, 0, 5)
        
        # Ajuste das proporções do grid
        position_layout.setColumnStretch(1, 2)  # Longitude
        position_layout.setColumnStretch(3, 2)  # Latitude
        position_layout.setColumnStretch(5, 2)  # Profundidade
        
        basic_layout.addRow("Posição:", position_frame)
        
        # Tempo de lançamento com melhor estilo
        self.release_datetime = QDateTimeEdit(QDateTime.currentDateTime())
        self.release_datetime.setCalendarPopup(True)
        self.release_datetime.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.release_datetime.setMinimumHeight(30)
        self.release_datetime.setButtonSymbols(QDateTimeEdit.PlusMinus)
        basic_layout.addRow("Tempo de Lançamento:", self.release_datetime)
        
        # Tipo de lançamento com layout melhorado
        release_type_frame = QFrame()
        release_type_layout = QHBoxLayout(release_type_frame)
        release_type_layout.setContentsMargins(0, 0, 0, 0)
        release_type_layout.setSpacing(20)
        
        self.release_type_group = QButtonGroup(self)
        
        self.instant_release_radio = QRadioButton("Lançamento Instantâneo")
        self.instant_release_radio.setChecked(True)
        self.instant_release_radio.setMinimumHeight(30)
        
        self.continuous_release_radio = QRadioButton("Lançamento Contínuo")
        self.continuous_release_radio.setMinimumHeight(30)
        
        self.release_type_group.addButton(self.instant_release_radio, 1)
        self.release_type_group.addButton(self.continuous_release_radio, 2)
        
        release_type_layout.addWidget(self.instant_release_radio)
        release_type_layout.addWidget(self.continuous_release_radio)
        release_type_layout.addStretch(1)
        
        basic_layout.addRow("Tipo de Lançamento:", release_type_frame)
        
        # Duração do lançamento
        self.release_duration_spin = QSpinBox()
        self.release_duration_spin.setRange(1, 720)
        self.release_duration_spin.setValue(24)
        self.release_duration_spin.setSuffix(" horas")
        self.release_duration_spin.setEnabled(False)
        self.release_duration_spin.setMinimumHeight(30)
        basic_layout.addRow("Duração do Lançamento:", self.release_duration_spin)
        
        # Conectar tipo de lançamento para ativar/desativar duração
        self.instant_release_radio.toggled.connect(self.toggle_release_duration)
        
        # Quantidade com layout melhorado
        quantity_frame = QFrame()
        quantity_layout = QHBoxLayout(quantity_frame)
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_layout.setSpacing(10)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 1000000)
        self.amount_spin.setValue(1000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setMinimumHeight(30)
        
        self.units_combo = QComboBox()
        self.units_combo.addItems(["bbl", "gal", "m³", "L", "ton"])
        self.units_combo.setMinimumHeight(30)
        self.units_combo.setMaximumWidth(100)
        
        quantity_layout.addWidget(self.amount_spin)
        quantity_layout.addWidget(self.units_combo)
        quantity_layout.addStretch(1)
        
        basic_layout.addRow("Quantidade:", quantity_frame)
        
        # Número de elementos
        self.num_elements_spin = QSpinBox()
        self.num_elements_spin.setRange(10, 100000)
        self.num_elements_spin.setValue(1000)
        self.num_elements_spin.setSingleStep(100)
        self.num_elements_spin.setMinimumHeight(30)
        basic_layout.addRow("Número de Elementos:", self.num_elements_spin)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # =====================================================
        # SEÇÃO 2: SUBSTÂNCIA DERRAMADA
        # =====================================================
        substance_group = QGroupBox("Substância Derramada")
        substance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        substance_layout = QFormLayout()
        substance_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        substance_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        substance_layout.setContentsMargins(15, 20, 15, 15)
        substance_layout.setHorizontalSpacing(15)
        substance_layout.setVerticalSpacing(12)
        
        # Tipo de substância com layout melhorado
        substance_type_frame = QFrame()
        substance_type_layout = QHBoxLayout(substance_type_frame)
        substance_type_layout.setContentsMargins(0, 0, 0, 0)
        substance_type_layout.setSpacing(20)
        
        self.substance_type_group = QButtonGroup(self)
        
        self.conservative_radio = QRadioButton("Traçador Conservativo (Sem Intemperismo)")
        self.conservative_radio.setChecked(True)
        self.conservative_radio.setMinimumHeight(30)
        
        self.oil_radio = QRadioButton("Óleo (Com Intemperismo)")
        self.oil_radio.setMinimumHeight(30)
        
        self.substance_type_group.addButton(self.conservative_radio, 1)
        self.substance_type_group.addButton(self.oil_radio, 2)
        
        substance_type_layout.addWidget(self.conservative_radio)
        substance_type_layout.addWidget(self.oil_radio)
        substance_type_layout.addStretch(1)
        
        substance_layout.addRow("Tipo de Substância:", substance_type_frame)
        
        # Arquivo de óleo com layout melhorado
        oil_file_frame = QFrame()
        oil_file_layout = QHBoxLayout(oil_file_frame)
        oil_file_layout.setContentsMargins(0, 0, 0, 0)
        oil_file_layout.setSpacing(10)
        
        self.oil_file_input = QLineEdit()
        self.oil_file_input.setPlaceholderText("Selecione um arquivo de óleo...")
        self.oil_file_input.setReadOnly(True)
        self.oil_file_input.setMinimumHeight(30)
        
        self.oil_browse_button = QPushButton("Procurar...")
        self.oil_browse_button.setMinimumHeight(30)
        self.oil_browse_button.setMinimumWidth(100)
        self.oil_browse_button.clicked.connect(self.browse_oil_file)
        
        oil_file_layout.addWidget(self.oil_file_input)
        oil_file_layout.addWidget(self.oil_browse_button)
        
        substance_layout.addRow("Arquivo de Óleo:", oil_file_frame)
        
        # Desativar seção de óleo se o tipo for conservativo
        self.oil_file_input.setEnabled(False)
        self.oil_browse_button.setEnabled(False)
        
        # Conectar mudança de tipo de substância
        self.conservative_radio.toggled.connect(self.toggle_substance_type)
        
        substance_group.setLayout(substance_layout)
        scroll_layout.addWidget(substance_group)
        
        # =====================================================
        # SEÇÃO 3: CONFIGURAÇÕES AVANÇADAS
        # =====================================================
        advanced_group = QGroupBox("Configurações Avançadas")
        advanced_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        advanced_layout = QFormLayout()
        advanced_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        advanced_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        advanced_layout.setContentsMargins(15, 20, 15, 15)
        advanced_layout.setHorizontalSpacing(15)
        advanced_layout.setVerticalSpacing(12)
        
        # Incerteza na quantidade
        self.amount_uncertainty_spin = QDoubleSpinBox()
        self.amount_uncertainty_spin.setRange(0, 0.5)
        self.amount_uncertainty_spin.setValue(0)
        self.amount_uncertainty_spin.setSingleStep(0.01)
        self.amount_uncertainty_spin.setMinimumHeight(30)
        advanced_layout.addRow("Escala de Incerteza na Quantidade:", self.amount_uncertainty_spin)
        
        # Distribuição inicial
        self.initial_distribution_combo = QComboBox()
        self.initial_distribution_combo.addItems(["Uniforme", "Normal", "Lognormal"])
        self.initial_distribution_combo.setMinimumHeight(30)
        advanced_layout.addRow("Distribuição Inicial:", self.initial_distribution_combo)
        
        # Configuração de fração/tamanho das partículas - melhor alinhamento
        droplet_checkbox_frame = QFrame()
        droplet_checkbox_layout = QHBoxLayout(droplet_checkbox_frame)
        droplet_checkbox_layout.setContentsMargins(0, 0, 0, 0)
        droplet_checkbox_layout.setSpacing(0)
        
        self.use_droplet_size = QCheckBox("Configurar tamanho das gotículas")
        self.use_droplet_size.setChecked(False)
        self.use_droplet_size.toggled.connect(self.toggle_droplet_size)
        self.use_droplet_size.setMinimumHeight(30)
        
        droplet_checkbox_layout.addWidget(self.use_droplet_size)
        droplet_checkbox_layout.addStretch(1)
        
        advanced_layout.addRow("", droplet_checkbox_frame)
        
        # Tamanho mínimo e máximo das gotículas
        droplet_size_frame = QFrame()
        droplet_size_layout = QGridLayout(droplet_size_frame)
        droplet_size_layout.setContentsMargins(0, 0, 0, 0)
        droplet_size_layout.setHorizontalSpacing(10)
        droplet_size_layout.setVerticalSpacing(0)
        
        min_label = QLabel("Mín:")
        self.min_size_spin = QDoubleSpinBox()
        self.min_size_spin.setRange(1, 1000)
        self.min_size_spin.setValue(10)
        self.min_size_spin.setSuffix(" μm")
        self.min_size_spin.setEnabled(False)
        self.min_size_spin.setMinimumHeight(30)
        
        max_label = QLabel("Máx:")
        self.max_size_spin = QDoubleSpinBox()
        self.max_size_spin.setRange(1, 5000)
        self.max_size_spin.setValue(300)
        self.max_size_spin.setSuffix(" μm")
        self.max_size_spin.setEnabled(False)
        self.max_size_spin.setMinimumHeight(30)
        
        droplet_size_layout.addWidget(min_label, 0, 0)
        droplet_size_layout.addWidget(self.min_size_spin, 0, 1)
        droplet_size_layout.addWidget(max_label, 0, 2)
        droplet_size_layout.addWidget(self.max_size_spin, 0, 3)
        
        # Ajuste das proporções do grid
        droplet_size_layout.setColumnStretch(1, 2)  # Mínimo
        droplet_size_layout.setColumnStretch(3, 2)  # Máximo
        
        advanced_layout.addRow("Tamanho das Gotículas:", droplet_size_frame)
        
        advanced_group.setLayout(advanced_layout)
        scroll_layout.addWidget(advanced_group)
        
        # Adicionar espaçador para empurrar tudo para cima
        scroll_layout.addStretch(1)
        
        # Finalizar configuração
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
    def toggle_release_duration(self, checked):
        """Ativar/desativar duração do lançamento com base no tipo"""
        self.release_duration_spin.setEnabled(not checked)
        
    def toggle_substance_type(self, checked):
        """Ativar/desativar opções de óleo com base no tipo de substância"""
        # Se checked=True, significa que o botão "Conservativo" está selecionado
        enable_oil = not checked
        self.oil_file_input.setEnabled(enable_oil)
        self.oil_browse_button.setEnabled(enable_oil)
        
    def toggle_droplet_size(self, checked):
        """Ativar/desativar campos de tamanho de gotículas"""
        self.min_size_spin.setEnabled(checked)
        self.max_size_spin.setEnabled(checked)
        
    def browse_oil_file(self):
        """Abrir diálogo para selecionar arquivo de óleo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Óleo", "", 
            "Arquivos de Óleo (*.json);;Todos os Arquivos (*)"
        )
        
        if file_path:
            self.oil_file_input.setText(file_path)
            
    def reset(self):
        """Redefine o widget para valores padrão"""
        self.lon_spin.setValue(-144)
        self.lat_spin.setValue(48.5)
        self.depth_spin.setValue(0)
        self.release_datetime.setDateTime(QDateTime.currentDateTime())
        self.instant_release_radio.setChecked(True)
        self.release_duration_spin.setValue(24)
        self.release_duration_spin.setEnabled(False)
        self.amount_spin.setValue(1000)
        self.units_combo.setCurrentIndex(0)  # "bbl"
        self.num_elements_spin.setValue(1000)
        self.conservative_radio.setChecked(True)
        self.oil_file_input.clear()
        self.oil_file_input.setEnabled(False)
        self.oil_browse_button.setEnabled(False)
        self.amount_uncertainty_spin.setValue(0)
        self.initial_distribution_combo.setCurrentIndex(0)  # "Uniforme"
        self.use_droplet_size.setChecked(False)
        self.min_size_spin.setValue(10)
        self.min_size_spin.setEnabled(False)
        self.max_size_spin.setValue(300)
        self.max_size_spin.setEnabled(False)
        
    def get_config(self):
        """Retorna a configuração atual do derramamento"""
        # Converter QDateTime para string no formato YYYY-MM-DDThh:mm:ss
        release_time_str = self.release_datetime.dateTime().toString("yyyy-MM-ddThh:mm:ss")
        
        # Criar configuração básica
        config = {
            'start_position': (self.lon_spin.value(), self.lat_spin.value(), self.depth_spin.value()),
            'release_time': release_time_str,
            'num_elements': self.num_elements_spin.value(),
            'amount': self.amount_spin.value(),
            'units': self.units_combo.currentText(),
            'amount_uncertainty_scale': self.amount_uncertainty_spin.value(),
        }
        
        # Configuração de lançamento contínuo
        if self.continuous_release_radio.isChecked():
            # Adicionar duração em horas para o final do lançamento
            config['continuous'] = True
            config['release_duration'] = self.release_duration_spin.value()
        else:
            config['continuous'] = False
            
        # Tipo de substância
        if self.conservative_radio.isChecked():
            config['substance_type'] = 'non_weathering'
        else:
            config['substance_type'] = 'oil'
            config['oil_file'] = self.oil_file_input.text()
            
        # Distribuição inicial
        distribution_types = ["uniform", "normal", "lognormal"]
        config['initial_distribution'] = distribution_types[self.initial_distribution_combo.currentIndex()]
        
        # Configuração de tamanho de gotículas
        if self.use_droplet_size.isChecked():
            config['droplet_size'] = {
                'min': self.min_size_spin.value(),
                'max': self.max_size_spin.value()
            }
        
        return config
        
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
                QDoubleSpinBox, QSpinBox, QDateTimeEdit, QComboBox, QLineEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    border-radius: 3px;
                    padding: 2px 5px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QRadioButton, QCheckBox {
                    color: #ecf0f1;
                }
                QRadioButton::indicator, QCheckBox::indicator {
                    width: 13px;
                    height: 13px;
                }
                QRadioButton::indicator::unchecked, QCheckBox::indicator::unchecked {
                    border: 1px solid #7f8c8d;
                    background-color: #34495e;
                }
                QRadioButton::indicator::checked, QCheckBox::indicator::checked {
                    border: 1px solid #7f8c8d;
                    background-color: #3498db;
                }
            """)
        else:
            # Tema claro - reset de volta ao padrão
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            # Manter apenas o estilo mínimo necessário para garantir consistência