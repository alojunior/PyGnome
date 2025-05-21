import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QRadioButton, QButtonGroup, QFormLayout,
                              QDoubleSpinBox, QLineEdit, QPushButton, QFileDialog,
                              QCheckBox, QSpinBox, QListWidget, QListWidgetItem,
                              QScrollArea, QTabWidget, QSplitter, QFrame)
from PySide6.QtCore import Qt, Slot

class WindConfigWidget(QWidget):
    """Widget para configuração de vento (WindMover)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(25)  # Bastante espaço entre seções
        
        # Tipo de entrada de vento
        self.wind_type_group = QButtonGroup(self)
        type_box = QGroupBox("Tipo de Entrada de Vento")
        type_layout = QVBoxLayout()
        type_layout.setContentsMargins(10, 20, 10, 20)
        type_layout.setSpacing(15)
        
        self.constant_radio = QRadioButton("Vento Constante")
        self.file_radio = QRadioButton("Arquivo de Vento")
        self.constant_radio.setChecked(True)
        
        self.wind_type_group.addButton(self.constant_radio, 1)
        self.wind_type_group.addButton(self.file_radio, 2)
        
        type_layout.addWidget(self.constant_radio)
        type_layout.addWidget(self.file_radio)
        type_box.setLayout(type_layout)
        
        # Parâmetros de vento constante
        self.constant_group = QGroupBox("Parâmetros de Vento Constante")
        constant_layout = QFormLayout()
        constant_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        constant_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        constant_layout.setContentsMargins(10, 20, 10, 20)
        constant_layout.setHorizontalSpacing(20)
        constant_layout.setVerticalSpacing(15)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0, 100)
        self.speed_spin.setValue(5.0)
        self.speed_spin.setSuffix(" m/s")
        
        self.direction_spin = QDoubleSpinBox()
        self.direction_spin.setRange(0, 360)
        self.direction_spin.setValue(0.0)
        self.direction_spin.setSuffix("°")
        
        constant_layout.addRow("Velocidade:", self.speed_spin)
        constant_layout.addRow("Direção (de onde vem):", self.direction_spin)
        self.constant_group.setLayout(constant_layout)
        
        # Configuração de arquivo
        self.file_group = QGroupBox("Arquivo de Vento")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(10, 20, 10, 20)
        file_layout.setSpacing(15)
        
        file_input_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Caminho para o arquivo de vento...")
        self.file_input.setReadOnly(True)
        
        self.browse_button = QPushButton("Procurar...")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_input_layout.addWidget(self.file_input)
        file_input_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_input_layout)
        self.file_format_label = QLabel("Formatos suportados: netCDF, OSSM, texto")
        file_layout.addWidget(self.file_format_label)
        
        # Aviso de funcionalidade incompleta
        self.warning_label = QLabel("Nota: A funcionalidade de arquivo de vento está em desenvolvimento.")
        self.warning_label.setStyleSheet("color: #e74c3c; font-style: italic;")
        file_layout.addWidget(self.warning_label)
        
        self.file_group.setLayout(file_layout)
        self.file_group.setEnabled(False)
        
        # Configurações de windage (arrasto pelo vento)
        self.windage_group = QGroupBox("Configurações de Windage")
        windage_layout = QFormLayout()
        windage_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        windage_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        windage_layout.setContentsMargins(10, 20, 10, 20)
        windage_layout.setHorizontalSpacing(20)
        windage_layout.setVerticalSpacing(15)
        
        self.windage_min_spin = QDoubleSpinBox()
        self.windage_min_spin.setRange(0, 10)
        self.windage_min_spin.setValue(1.0)
        self.windage_min_spin.setSingleStep(0.1)
        self.windage_min_spin.setSuffix(" %")
        
        self.windage_max_spin = QDoubleSpinBox()
        self.windage_max_spin.setRange(0, 10)
        self.windage_max_spin.setValue(4.0)
        self.windage_max_spin.setSingleStep(0.1)
        self.windage_max_spin.setSuffix(" %")
        
        self.windage_persist_spin = QSpinBox()
        self.windage_persist_spin.setRange(0, 86400)  # 0 segundos a 24 horas
        self.windage_persist_spin.setValue(900)  # 15 minutos padrão
        self.windage_persist_spin.setSuffix(" segundos")
        self.windage_persist_spin.setSpecialValueText("Infinito")
        
        windage_layout.addRow("Windage Mínimo:", self.windage_min_spin)
        windage_layout.addRow("Windage Máximo:", self.windage_max_spin)
        windage_layout.addRow("Persistência:", self.windage_persist_spin)
        
        self.windage_group.setLayout(windage_layout)
        
        # Conectar eventos
        self.constant_radio.toggled.connect(self.toggle_input_type)
        self.file_radio.toggled.connect(self.toggle_input_type)
        
        # Adicionar tudo ao layout principal com espaçamentos
        layout.addWidget(type_box)
        layout.addSpacing(10)
        layout.addWidget(self.constant_group)
        layout.addSpacing(10)
        layout.addWidget(self.file_group)
        layout.addSpacing(10)
        layout.addWidget(self.windage_group)
        layout.addStretch(1)
        
    def browse_file(self):
        """Abrir diálogo para selecionar arquivo de vento"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Vento", "", 
            "Todos os Arquivos (*);;NetCDF (*.nc);;Texto (*.txt)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
    
    def toggle_input_type(self, checked):
        """Alternar entre vento constante e arquivo"""
        if self.constant_radio.isChecked():
            self.constant_group.setEnabled(True)
            self.file_group.setEnabled(False)
        else:
            self.constant_group.setEnabled(False)
            self.file_group.setEnabled(True)
            
    def get_config(self):
        """Retorna a configuração atual do vento"""
        config = {
            'type': 'wind',
            'enabled': True
        }
        
        if self.constant_radio.isChecked():
            config['constant'] = True
            config['speed'] = self.speed_spin.value()
            config['direction'] = self.direction_spin.value()
        else:
            config['constant'] = False
            config['file'] = self.file_input.text()
            
        config['windage_range'] = [self.windage_min_spin.value() / 100.0, 
                                self.windage_max_spin.value() / 100.0]
        config['windage_persist'] = self.windage_persist_spin.value()
        
        return config


class CurrentConfigWidget(QWidget):
    """Widget para configuração de correntes (CurrentMover)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(25)  # Bastante espaço entre seções
        
        # Tipo de entrada de corrente
        self.current_type_group = QButtonGroup(self)
        type_box = QGroupBox("Tipo de Entrada de Corrente")
        type_layout = QVBoxLayout()
        type_layout.setContentsMargins(10, 20, 10, 20)
        type_layout.setSpacing(15)
        
        self.constant_radio = QRadioButton("Corrente Constante")
        self.file_radio = QRadioButton("Arquivo de Corrente")
        self.file_radio.setChecked(True)
        
        self.current_type_group.addButton(self.constant_radio, 1)
        self.current_type_group.addButton(self.file_radio, 2)
        
        type_layout.addWidget(self.constant_radio)
        type_layout.addWidget(self.file_radio)
        type_box.setLayout(type_layout)
        
        # Parâmetros de corrente constante
        self.constant_group = QGroupBox("Parâmetros de Corrente Constante")
        constant_layout = QFormLayout()
        constant_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        constant_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        constant_layout.setContentsMargins(10, 20, 10, 20)
        constant_layout.setHorizontalSpacing(20)
        constant_layout.setVerticalSpacing(15)
        
        self.u_speed_spin = QDoubleSpinBox()
        self.u_speed_spin.setRange(-10, 10)
        self.u_speed_spin.setValue(0.2)
        self.u_speed_spin.setSuffix(" m/s")
        
        self.v_speed_spin = QDoubleSpinBox()
        self.v_speed_spin.setRange(-10, 10)
        self.v_speed_spin.setValue(0.0)
        self.v_speed_spin.setSuffix(" m/s")
        
        constant_layout.addRow("Componente U (Leste):", self.u_speed_spin)
        constant_layout.addRow("Componente V (Norte):", self.v_speed_spin)
        self.constant_group.setLayout(constant_layout)
        self.constant_group.setEnabled(False)
        
        # Configuração de arquivo
        self.file_group = QGroupBox("Arquivo de Corrente")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(10, 20, 10, 20)
        file_layout.setSpacing(15)
        
        file_input_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Caminho para o arquivo de corrente...")
        self.file_input.setReadOnly(True)
        
        self.browse_button = QPushButton("Procurar...")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_input_layout.addWidget(self.file_input)
        file_input_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_input_layout)
        self.file_format_label = QLabel("Formatos suportados: netCDF, CATS")
        file_layout.addWidget(self.file_format_label)
        
        # Aviso de funcionalidade incompleta
        self.warning_label = QLabel("Nota: A funcionalidade de arquivo de corrente está em desenvolvimento.")
        self.warning_label.setStyleSheet("color: #e74c3c; font-style: italic;")
        file_layout.addWidget(self.warning_label)
        
        self.file_group.setLayout(file_layout)
        
        # Conectar eventos
        self.constant_radio.toggled.connect(self.toggle_input_type)
        self.file_radio.toggled.connect(self.toggle_input_type)
        
        # Adicionar tudo ao layout principal com espaçamentos
        layout.addWidget(type_box)
        layout.addSpacing(10)
        layout.addWidget(self.constant_group)
        layout.addSpacing(10)
        layout.addWidget(self.file_group)
        layout.addStretch(1)
        
    def browse_file(self):
        """Abrir diálogo para selecionar arquivo de corrente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Corrente", "", 
            "Todos os Arquivos (*);;NetCDF (*.nc)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
    
    def toggle_input_type(self, checked):
        """Alternar entre corrente constante e arquivo"""
        if self.constant_radio.isChecked():
            self.constant_group.setEnabled(True)
            self.file_group.setEnabled(False)
        else:
            self.constant_group.setEnabled(False)
            self.file_group.setEnabled(True)
            
    def get_config(self):
        """Retorna a configuração atual da corrente"""
        config = {
            'type': 'current',
            'enabled': True
        }
        
        if self.constant_radio.isChecked():
            config['constant'] = True
            config['u'] = self.u_speed_spin.value()
            config['v'] = self.v_speed_spin.value()
        else:
            config['constant'] = False
            config['file'] = self.file_input.text()
            
        return config


class DiffusionConfigWidget(QWidget):
    """Widget para configuração de difusão (RandomMover)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(25)  # Bastante espaço entre seções
        
        # Ativar/desativar difusão
        self.enable_checkbox = QCheckBox("Ativar Difusão")
        self.enable_checkbox.setChecked(True)
        self.enable_checkbox.toggled.connect(self.toggle_enabled)
        
        # Parâmetros de difusão
        self.params_group = QGroupBox("Parâmetros de Difusão")
        params_layout = QFormLayout()
        params_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        params_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        params_layout.setContentsMargins(10, 20, 10, 20)
        params_layout.setHorizontalSpacing(20)
        params_layout.setVerticalSpacing(15)
        
        self.diffusion_coef_spin = QDoubleSpinBox()
        self.diffusion_coef_spin.setRange(0, 1000000)
        self.diffusion_coef_spin.setValue(100000)
        self.diffusion_coef_spin.setSingleStep(10000)
        self.diffusion_coef_spin.setSuffix(" cm²/s")
        
        self.diffusion_info = QLabel(
            "Recomendado: 10⁵-10⁶ cm²/s para costa, 10⁷ cm²/s para oceano aberto"
        )
        self.diffusion_info.setWordWrap(True)
        
        params_layout.addRow("Coeficiente de Difusão:", self.diffusion_coef_spin)
        params_layout.addRow("", self.diffusion_info)
        
        self.params_group.setLayout(params_layout)
        
        # 3D difusão (RandomMover3D)
        self.enable_3d_checkbox = QCheckBox("Usar Difusão 3D (para simulações 3D)")
        self.enable_3d_checkbox.setChecked(False)
        self.enable_3d_checkbox.toggled.connect(self.toggle_3d)
        
        self.params_3d_group = QGroupBox("Parâmetros de Difusão 3D")
        params_3d_layout = QFormLayout()
        params_3d_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        params_3d_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        params_3d_layout.setContentsMargins(10, 20, 10, 20)
        params_3d_layout.setHorizontalSpacing(20)
        params_3d_layout.setVerticalSpacing(15)
        
        self.horiz_coef_above_spin = QDoubleSpinBox()
        self.horiz_coef_above_spin.setRange(0, 1000000)
        self.horiz_coef_above_spin.setValue(100000)
        self.horiz_coef_above_spin.setSingleStep(10000)
        self.horiz_coef_above_spin.setSuffix(" cm²/s")
        
        self.horiz_coef_below_spin = QDoubleSpinBox()
        self.horiz_coef_below_spin.setRange(0, 1000000)
        self.horiz_coef_below_spin.setValue(10000)
        self.horiz_coef_below_spin.setSingleStep(1000)
        self.horiz_coef_below_spin.setSuffix(" cm²/s")
        
        self.vert_coef_above_spin = QDoubleSpinBox()
        self.vert_coef_above_spin.setRange(0, 100)
        self.vert_coef_above_spin.setValue(5)
        self.vert_coef_above_spin.setSingleStep(1)
        self.vert_coef_above_spin.setSuffix(" cm²/s")
        
        self.vert_coef_below_spin = QDoubleSpinBox()
        self.vert_coef_below_spin.setRange(0, 100)
        self.vert_coef_below_spin.setValue(0.5)
        self.vert_coef_below_spin.setSingleStep(0.1)
        self.vert_coef_below_spin.setSuffix(" cm²/s")
        
        self.mixed_layer_depth_spin = QDoubleSpinBox()
        self.mixed_layer_depth_spin.setRange(0, 1000)
        self.mixed_layer_depth_spin.setValue(10)
        self.mixed_layer_depth_spin.setSingleStep(1)
        self.mixed_layer_depth_spin.setSuffix(" m")
        
        params_3d_layout.addRow("Difusão Horizontal (acima da camada de mistura):", self.horiz_coef_above_spin)
        params_3d_layout.addRow("Difusão Horizontal (abaixo da camada de mistura):", self.horiz_coef_below_spin)
        params_3d_layout.addRow("Difusão Vertical (acima da camada de mistura):", self.vert_coef_above_spin)
        params_3d_layout.addRow("Difusão Vertical (abaixo da camada de mistura):", self.vert_coef_below_spin)
        params_3d_layout.addRow("Profundidade da Camada de Mistura:", self.mixed_layer_depth_spin)
        
        self.params_3d_group.setLayout(params_3d_layout)
        self.params_3d_group.setEnabled(False)
        
        # Adicionar tudo ao layout principal com espaçamentos
        layout.addWidget(self.enable_checkbox)
        layout.addSpacing(10)
        layout.addWidget(self.params_group)
        layout.addSpacing(10)
        layout.addWidget(self.enable_3d_checkbox)
        layout.addSpacing(10)
        layout.addWidget(self.params_3d_group)
        layout.addStretch(1)
        
    def toggle_enabled(self, enabled):
        """Ativar/desativar parâmetros de difusão"""
        self.params_group.setEnabled(enabled)
        self.enable_3d_checkbox.setEnabled(enabled)
        if enabled:
            self.params_3d_group.setEnabled(self.enable_3d_checkbox.isChecked())
        else:
            self.params_3d_group.setEnabled(False)
    
    def toggle_3d(self, enabled):
        """Ativar/desativar parâmetros de difusão 3D"""
        self.params_3d_group.setEnabled(enabled)
        
    def get_config(self):
        """Retorna a configuração atual da difusão"""
        if not self.enable_checkbox.isChecked():
            return None
            
        config = {
            'type': 'random',
            'enabled': True
        }
        
        if self.enable_3d_checkbox.isChecked():
            config['is_3d'] = True
            config['horizontal_diffusion_coef_above_ml'] = self.horiz_coef_above_spin.value()
            config['horizontal_diffusion_coef_below_ml'] = self.horiz_coef_below_spin.value()
            config['vertical_diffusion_coef_above_ml'] = self.vert_coef_above_spin.value()
            config['vertical_diffusion_coef_below_ml'] = self.vert_coef_below_spin.value()
            config['mixed_layer_depth'] = self.mixed_layer_depth_spin.value()
        else:
            config['is_3d'] = False
            config['diffusion_coef'] = self.diffusion_coef_spin.value()
            
        return config


class MoversConfigWidget(QWidget):
    """Widget principal para configuração de todos os movers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Criar tabs para diferentes movers
        self.tabs = QTabWidget()
        
        # Tab de WindMover
        self.wind_config = WindConfigWidget()
        self.tabs.addTab(self.wind_config, "Vento")
        
        # Tab de CurrentMover
        self.current_config = CurrentConfigWidget()
        self.tabs.addTab(self.current_config, "Corrente")
        
        # Tab de RandomMover (difusão)
        self.diffusion_config = DiffusionConfigWidget()
        self.tabs.addTab(self.diffusion_config, "Difusão")
        
        # Adicionar tabs ao layout
        layout.addWidget(self.tabs)
        
    def reset(self):
        """Redefine o widget para valores padrão"""
        # Aqui você precisaria implementar reset para cada sub-widget
        pass
        
    def get_config(self):
        """Retorna a configuração atual dos movers"""
        movers_config = []
        
        # Adicionar configuração de vento
        wind_config = self.wind_config.get_config()
        if wind_config:
            movers_config.append(wind_config)
            
        # Adicionar configuração de corrente
        current_config = self.current_config.get_config()
        if current_config:
            movers_config.append(current_config)
            
        # Adicionar configuração de difusão
        diffusion_config = self.diffusion_config.get_config()
        if diffusion_config:
            movers_config.append(diffusion_config)
            
        return movers_config