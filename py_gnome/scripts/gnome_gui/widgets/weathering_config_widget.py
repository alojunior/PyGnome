import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                              QGroupBox, QLabel, QCheckBox, QDoubleSpinBox, 
                              QComboBox, QSpinBox, QButtonGroup, QRadioButton,
                              QFrame, QScrollArea, QSizePolicy, QPushButton,
                              QFileDialog, QLineEdit)
from PySide6.QtCore import Qt

class WeatheringConfigWidget(QWidget):
    """Widget para configuração de processos de intemperismo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        # Layout principal com espaçamento adequado
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(25)  # Bastante espaço entre seções
        
        # Área de scroll para permitir visualização em telas menores
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(25)
        
        # =====================================================
        # SEÇÃO 1: ATIVAÇÃO DE INTEMPERISMO
        # =====================================================
        activation_group = QGroupBox("Ativação de Processos de Intemperismo")
        activation_layout = QFormLayout()
        activation_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        activation_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        activation_layout.setContentsMargins(10, 20, 10, 20)
        activation_layout.setHorizontalSpacing(20)
        activation_layout.setVerticalSpacing(15)
        
        # Ativar/desativar intemperismo
        self.weathering_enabled = QCheckBox("Ativar Processos de Intemperismo")
        self.weathering_enabled.setChecked(False)
        self.weathering_enabled.setMinimumHeight(30)
        self.weathering_enabled.toggled.connect(self.toggle_weathering)
        activation_layout.addRow("", self.weathering_enabled)
        
        # Nota informativa
        note_label = QLabel("Nota: Processos de intemperismo só funcionarão se o tipo de substância for definido como 'Óleo' na aba de Derramamento.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #c0392b; font-style: italic;")
        activation_layout.addRow("", note_label)
        
        activation_group.setLayout(activation_layout)
        scroll_layout.addWidget(activation_group)
        
        # =====================================================
        # SEÇÃO 2: PROCESSOS DE INTEMPERISMO
        # =====================================================
        processes_group = QGroupBox("Processos de Intemperismo")
        processes_layout = QFormLayout()
        processes_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        processes_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        processes_layout.setContentsMargins(10, 20, 10, 20)
        processes_layout.setHorizontalSpacing(20)
        processes_layout.setVerticalSpacing(15)
        
        # Evaporação
        self.evaporation_checkbox = QCheckBox("Evaporação")
        self.evaporation_checkbox.setChecked(True)
        self.evaporation_checkbox.setEnabled(False)
        self.evaporation_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.evaporation_checkbox)
        
        # Dispersão natural
        self.dispersion_checkbox = QCheckBox("Dispersão Natural")
        self.dispersion_checkbox.setChecked(True)
        self.dispersion_checkbox.setEnabled(False)
        self.dispersion_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.dispersion_checkbox)
        
        # Emulsificação (mousse)
        self.emulsification_checkbox = QCheckBox("Emulsificação (Mousse)")
        self.emulsification_checkbox.setChecked(True)
        self.emulsification_checkbox.setEnabled(False)
        self.emulsification_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.emulsification_checkbox)
        
        # Dissolução
        self.dissolution_checkbox = QCheckBox("Dissolução")
        self.dissolution_checkbox.setChecked(False)
        self.dissolution_checkbox.setEnabled(False)
        self.dissolution_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.dissolution_checkbox)
        
        # Sedimentação
        self.sedimentation_checkbox = QCheckBox("Sedimentação")
        self.sedimentation_checkbox.setChecked(False)
        self.sedimentation_checkbox.setEnabled(False)
        self.sedimentation_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.sedimentation_checkbox)
        
        # Biodegradação
        self.biodegradation_checkbox = QCheckBox("Biodegradação")
        self.biodegradation_checkbox.setChecked(False)
        self.biodegradation_checkbox.setEnabled(False)
        self.biodegradation_checkbox.setMinimumHeight(30)
        processes_layout.addRow("", self.biodegradation_checkbox)
        
        processes_group.setLayout(processes_layout)
        scroll_layout.addWidget(processes_group)
        
        # =====================================================
        # SEÇÃO 3: PARÂMETROS AMBIENTAIS
        # =====================================================
        env_group = QGroupBox("Parâmetros Ambientais para Intemperismo")
        env_layout = QFormLayout()
        env_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        env_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        env_layout.setContentsMargins(10, 20, 10, 20)
        env_layout.setHorizontalSpacing(20)
        env_layout.setVerticalSpacing(15)
        
        # Temperatura da água
        self.water_temp_spin = QDoubleSpinBox()
        self.water_temp_spin.setRange(-2, 40)
        self.water_temp_spin.setValue(15.0)
        self.water_temp_spin.setSuffix(" °C")
        self.water_temp_spin.setDecimals(1)
        self.water_temp_spin.setEnabled(False)
        self.water_temp_spin.setMinimumHeight(30)
        env_layout.addRow("Temperatura da Água:", self.water_temp_spin)
        
        # Salinidade
        self.salinity_spin = QDoubleSpinBox()
        self.salinity_spin.setRange(0, 40)
        self.salinity_spin.setValue(35.0)
        self.salinity_spin.setSuffix(" ppt")
        self.salinity_spin.setDecimals(1)
        self.salinity_spin.setEnabled(False)
        self.salinity_spin.setMinimumHeight(30)
        env_layout.addRow("Salinidade:", self.salinity_spin)
        
        # Tipo de sedimento
        self.sediment_combo = QComboBox()
        self.sediment_combo.addItems(["Areia Fina", "Areia Média", "Areia Grossa", "Cascalho", "Rocha", "Lama"])
        self.sediment_combo.setEnabled(False)
        self.sediment_combo.setMinimumHeight(30)
        env_layout.addRow("Tipo de Sedimento de Fundo:", self.sediment_combo)
        
        # Concentração de sedimento suspenso
        self.sediment_conc_spin = QDoubleSpinBox()
        self.sediment_conc_spin.setRange(0, 5000)
        self.sediment_conc_spin.setValue(5.0)
        self.sediment_conc_spin.setSuffix(" mg/L")
        self.sediment_conc_spin.setDecimals(1)
        self.sediment_conc_spin.setEnabled(False)
        self.sediment_conc_spin.setMinimumHeight(30)
        env_layout.addRow("Concentração de Sedimento Suspenso:", self.sediment_conc_spin)
        
        # Concentração de COD (Carbono Orgânico Dissolvido)
        self.doc_spin = QDoubleSpinBox()
        self.doc_spin.setRange(0, 50)
        self.doc_spin.setValue(1.0)
        self.doc_spin.setSuffix(" mg/L")
        self.doc_spin.setDecimals(1)
        self.doc_spin.setEnabled(False)
        self.doc_spin.setMinimumHeight(30)
        env_layout.addRow("Carbono Orgânico Dissolvido (COD):", self.doc_spin)
        
        env_group.setLayout(env_layout)
        scroll_layout.addWidget(env_group)
        
        # =====================================================
        # SEÇÃO 4: CONFIGURAÇÕES AVANÇADAS DE INTEMPERISMO
        # =====================================================
        advanced_group = QGroupBox("Configurações Avançadas de Intemperismo")
        advanced_layout = QFormLayout()
        advanced_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        advanced_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        advanced_layout.setContentsMargins(10, 20, 10, 20)
        advanced_layout.setHorizontalSpacing(20)
        advanced_layout.setVerticalSpacing(15)
        
        # Taxa de biodegradação
        self.biodeg_rate_spin = QDoubleSpinBox()
        self.biodeg_rate_spin.setRange(0.001, 0.1)
        self.biodeg_rate_spin.setValue(0.01)
        self.biodeg_rate_spin.setSingleStep(0.001)
        self.biodeg_rate_spin.setDecimals(4)
        self.biodeg_rate_spin.setEnabled(False)
        self.biodeg_rate_spin.setMinimumHeight(30)
        advanced_layout.addRow("Taxa de Biodegradação (1/hora):", self.biodeg_rate_spin)
        
        # Conteúdo máximo de água na emulsão
        self.emulsion_water_content_spin = QDoubleSpinBox()
        self.emulsion_water_content_spin.setRange(0, 0.9)
        self.emulsion_water_content_spin.setValue(0.7)
        self.emulsion_water_content_spin.setSingleStep(0.05)
        self.emulsion_water_content_spin.setDecimals(2)
        self.emulsion_water_content_spin.setEnabled(False)
        self.emulsion_water_content_spin.setMinimumHeight(30)
        advanced_layout.addRow("Conteúdo Máximo de Água na Emulsão:", self.emulsion_water_content_spin)
        
        # Uso de dados de vento/ondas de arquivo
        self.wave_data_frame = QFrame()
        wave_data_layout = QHBoxLayout(self.wave_data_frame)
        wave_data_layout.setContentsMargins(0, 0, 0, 0)
        wave_data_layout.setSpacing(10)
        
        self.wave_data_combo = QComboBox()
        self.wave_data_combo.addItems(["Usar altura de onda constante", "Calcular ondas a partir do vento", "Usar arquivo de ondas"])
        self.wave_data_combo.setEnabled(False)
        self.wave_data_combo.setMinimumHeight(30)
        self.wave_data_combo.currentIndexChanged.connect(self.toggle_wave_options)
        
        wave_data_layout.addWidget(self.wave_data_combo)
        wave_data_layout.addStretch(1)
        
        advanced_layout.addRow("Fonte de Dados de Ondas:", self.wave_data_frame)
        
        # Altura de onda constante
        self.wave_height_spin = QDoubleSpinBox()
        self.wave_height_spin.setRange(0, 10)
        self.wave_height_spin.setValue(1.0)
        self.wave_height_spin.setSuffix(" m")
        self.wave_height_spin.setDecimals(2)
        self.wave_height_spin.setEnabled(False)
        self.wave_height_spin.setMinimumHeight(30)
        advanced_layout.addRow("Altura de Onda Constante:", self.wave_height_spin)
        
        # Arquivo de ondas
        self.wave_file_frame = QFrame()
        wave_file_layout = QHBoxLayout(self.wave_file_frame)
        wave_file_layout.setContentsMargins(0, 0, 0, 0)
        wave_file_layout.setSpacing(10)
        
        self.wave_file_input = QLineEdit()
        self.wave_file_input.setPlaceholderText("Selecione um arquivo de dados de ondas...")
        self.wave_file_input.setReadOnly(True)
        self.wave_file_input.setEnabled(False)
        self.wave_file_input.setMinimumHeight(30)
        
        self.wave_browse_button = QPushButton("Procurar...")
        self.wave_browse_button.setMinimumHeight(30)
        self.wave_browse_button.setEnabled(False)
        self.wave_browse_button.clicked.connect(self.browse_wave_file)
        
        wave_file_layout.addWidget(self.wave_file_input)
        wave_file_layout.addWidget(self.wave_browse_button)
        
        advanced_layout.addRow("Arquivo de Ondas:", self.wave_file_frame)
        
        advanced_group.setLayout(advanced_layout)
        scroll_layout.addWidget(advanced_group)
        
        # Finalizar configuração
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def toggle_weathering(self, enabled):
        """Ativa/desativa todas as opções de intemperismo"""
        # Ativar/desativar processos
        self.evaporation_checkbox.setEnabled(enabled)
        self.dispersion_checkbox.setEnabled(enabled)
        self.emulsification_checkbox.setEnabled(enabled)
        self.dissolution_checkbox.setEnabled(enabled)
        self.sedimentation_checkbox.setEnabled(enabled)
        self.biodegradation_checkbox.setEnabled(enabled)
        
        # Ativar/desativar parâmetros ambientais
        self.water_temp_spin.setEnabled(enabled)
        self.salinity_spin.setEnabled(enabled)
        self.sediment_combo.setEnabled(enabled)
        self.sediment_conc_spin.setEnabled(enabled)
        self.doc_spin.setEnabled(enabled)
        
        # Ativar/desativar configurações avançadas
        self.biodeg_rate_spin.setEnabled(enabled and self.biodegradation_checkbox.isChecked())
        self.emulsion_water_content_spin.setEnabled(enabled and self.emulsification_checkbox.isChecked())
        self.wave_data_combo.setEnabled(enabled)
        
        # Ativar/desativar opções de ondas
        if enabled:
            self.toggle_wave_options(self.wave_data_combo.currentIndex())
        else:
            self.wave_height_spin.setEnabled(False)
            self.wave_file_input.setEnabled(False)
            self.wave_browse_button.setEnabled(False)
        
    def toggle_wave_options(self, index):
        """Alterna opções conforme a seleção de dados de onda"""
        # Se o intemperismo não estiver habilitado, não faz nada
        if not self.weathering_enabled.isChecked():
            return
            
        if index == 0:  # Onda constante
            self.wave_height_spin.setEnabled(True)
            self.wave_file_input.setEnabled(False)
            self.wave_browse_button.setEnabled(False)
        elif index == 1:  # Calcular do vento
            self.wave_height_spin.setEnabled(False)
            self.wave_file_input.setEnabled(False)
            self.wave_browse_button.setEnabled(False)
        else:  # Arquivo de ondas
            self.wave_height_spin.setEnabled(False)
            self.wave_file_input.setEnabled(True)
            self.wave_browse_button.setEnabled(True)
    
    def browse_wave_file(self):
        """Abre diálogo para selecionar arquivo de ondas"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Dados de Ondas", "", 
            "Arquivos NetCDF (*.nc);;Todos os Arquivos (*)"
        )
        
        if file_path:
            self.wave_file_input.setText(file_path)
    
    def reset(self):
        """Redefine o widget para valores padrão"""
        # Desativar intemperismo
        self.weathering_enabled.setChecked(False)
        
        # Resetar processos
        self.evaporation_checkbox.setChecked(True)
        self.dispersion_checkbox.setChecked(True)
        self.emulsification_checkbox.setChecked(True)
        self.dissolution_checkbox.setChecked(False)
        self.sedimentation_checkbox.setChecked(False)
        self.biodegradation_checkbox.setChecked(False)
        
        # Resetar parâmetros ambientais
        self.water_temp_spin.setValue(15.0)
        self.salinity_spin.setValue(35.0)
        self.sediment_combo.setCurrentIndex(0)
        self.sediment_conc_spin.setValue(5.0)
        self.doc_spin.setValue(1.0)
        
        # Resetar configurações avançadas
        self.biodeg_rate_spin.setValue(0.01)
        self.emulsion_water_content_spin.setValue(0.7)
        self.wave_data_combo.setCurrentIndex(0)
        self.wave_height_spin.setValue(1.0)
        self.wave_file_input.clear()
        
        # Desativar todos os controles relacionados a intemperismo
        self.toggle_weathering(False)
    
    def get_config(self):
        """Retorna a configuração atual de intemperismo"""
        config = {
            'enabled': self.weathering_enabled.isChecked()
        }
        
        if config['enabled']:
            # Adicionar processos ativos
            config.update({
                'evaporation': self.evaporation_checkbox.isChecked(),
                'dispersion': self.dispersion_checkbox.isChecked(),
                'emulsification': self.emulsification_checkbox.isChecked(),
                'dissolution': self.dissolution_checkbox.isChecked(),
                'sedimentation': self.sedimentation_checkbox.isChecked(),
                'biodegradation': self.biodegradation_checkbox.isChecked()
            })
            
            # Adicionar parâmetros ambientais
            config.update({
                'water_temp': self.water_temp_spin.value(),
                'salinity': self.salinity_spin.value(),
                'sediment_type': self.sediment_combo.currentText(),
                'sediment_concentration': self.sediment_conc_spin.value(),
                'dissolved_organic_carbon': self.doc_spin.value()
            })
            
            # Adicionar configurações avançadas
            config.update({
                'biodegradation_rate': self.biodeg_rate_spin.value(),
                'emulsion_water_content_max': self.emulsion_water_content_spin.value()
            })
            
            # Configuração de ondas
            wave_data_sources = ["constant", "from_wind", "from_file"]
            wave_data_source = wave_data_sources[self.wave_data_combo.currentIndex()]
            
            wave_config = {
                'source': wave_data_source
            }
            
            if wave_data_source == "constant":
                wave_config['height'] = self.wave_height_spin.value()
            elif wave_data_source == "from_file":
                wave_config['file'] = self.wave_file_input.text()
                
            config['wave_configuration'] = wave_config
            
        return config