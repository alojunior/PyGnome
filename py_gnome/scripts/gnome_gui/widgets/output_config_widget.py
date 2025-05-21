import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                              QGroupBox, QLabel, QCheckBox, QSpinBox, 
                              QComboBox, QLineEdit, QPushButton, QFileDialog,
                              QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                              QScrollArea, QSizePolicy, QGridLayout, QStackedWidget,
                              QDoubleSpinBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QSize, QMargins
from PySide6.QtGui import QColor, QBrush, QFont, QIcon, QPixmap

class OutputConfigWidget(QWidget):
    """Widget para configuração das saídas (Outputters)"""
    
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
        # SEÇÃO 1: DIRETÓRIO DE SAÍDA
        # =====================================================
        output_group = QGroupBox("Diretório de Saída")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(15, 20, 15, 15)
        output_layout.setSpacing(10)
        
        # Seleção de diretório de saída
        dir_frame = QFrame()
        dir_layout = QHBoxLayout(dir_frame)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.setSpacing(10)
        
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Diretório para salvar resultados...")
        self.output_dir_input.setText(os.path.join(os.getcwd(), "output"))
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setMinimumHeight(30)
        
        self.output_dir_button = QPushButton("Procurar...")
        self.output_dir_button.setMinimumHeight(30)
        self.output_dir_button.setMinimumWidth(100)
        self.output_dir_button.clicked.connect(self.browse_output_dir)
        
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(self.output_dir_button)
        
        output_layout.addWidget(dir_frame)
        
        # Informações sobre o diretório
        info_label = QLabel("Todos os arquivos de saída serão salvos neste diretório. Certifique-se de que você tenha permissão de escrita.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #2c3e50; font-style: italic;")
        output_layout.addWidget(info_label)
        
        output_group.setLayout(output_layout)
        scroll_layout.addWidget(output_group)
        
        # =====================================================
        # SEÇÃO 2: FORMATOS DE SAÍDA
        # =====================================================
        formats_group = QGroupBox("Formatos de Saída")
        formats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        formats_layout = QVBoxLayout()
        formats_layout.setContentsMargins(15, 20, 15, 15)
        formats_layout.setSpacing(15)
        
        # ---- NetCDF ----
        netcdf_frame = QFrame()
        netcdf_frame.setFrameStyle(QFrame.StyledPanel)
        netcdf_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        netcdf_layout = QVBoxLayout(netcdf_frame)
        netcdf_layout.setContentsMargins(10, 10, 10, 10)
        netcdf_layout.setSpacing(10)
        
        # Título com checkbox
        netcdf_header = QHBoxLayout()
        self.netcdf_check = QCheckBox("NetCDF (Dados de Partículas)")
        self.netcdf_check.setChecked(True)
        self.netcdf_check.toggled.connect(self.toggle_netcdf_options)
        self.netcdf_check.setStyleSheet("font-weight: bold;")
        self.netcdf_check.setMinimumHeight(30)
        
        netcdf_header.addWidget(self.netcdf_check)
        netcdf_header.addStretch(1)
        
        netcdf_layout.addLayout(netcdf_header)
        
        # Configurações específicas do NetCDF
        netcdf_config = QFormLayout()
        netcdf_config.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        netcdf_config.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        netcdf_config.setContentsMargins(20, 0, 0, 0)
        netcdf_config.setHorizontalSpacing(15)
        netcdf_config.setVerticalSpacing(10)
        
        self.netcdf_timestep_spin = QSpinBox()
        self.netcdf_timestep_spin.setRange(1, 24)
        self.netcdf_timestep_spin.setValue(1)
        self.netcdf_timestep_spin.setSuffix(" hora(s)")
        self.netcdf_timestep_spin.setMinimumHeight(30)
        
        self.netcdf_data_combo = QComboBox()
        self.netcdf_data_combo.addItems(["Padrão", "Mínimo", "Máximo"])
        self.netcdf_data_combo.setMinimumHeight(30)
        
        netcdf_config.addRow("Intervalo de Saída:", self.netcdf_timestep_spin)
        netcdf_config.addRow("Quantidade de Dados:", self.netcdf_data_combo)
        
        netcdf_layout.addLayout(netcdf_config)
        formats_layout.addWidget(netcdf_frame)
        
        # ---- Imagens (GIF/PNG) ----
        renderer_frame = QFrame()
        renderer_frame.setFrameStyle(QFrame.StyledPanel)
        renderer_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        renderer_layout = QVBoxLayout(renderer_frame)
        renderer_layout.setContentsMargins(10, 10, 10, 10)
        renderer_layout.setSpacing(10)
        
        # Título com checkbox
        renderer_header = QHBoxLayout()
        self.renderer_check = QCheckBox("Imagens (GIF/PNG)")
        self.renderer_check.setChecked(True)
        self.renderer_check.toggled.connect(self.toggle_renderer_options)
        self.renderer_check.setStyleSheet("font-weight: bold;")
        self.renderer_check.setMinimumHeight(30)
        
        renderer_header.addWidget(self.renderer_check)
        renderer_header.addStretch(1)
        
        renderer_layout.addLayout(renderer_header)
        
        # Configurações específicas do Renderer
        renderer_config = QFormLayout()
        renderer_config.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        renderer_config.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        renderer_config.setContentsMargins(20, 0, 0, 0)
        renderer_config.setHorizontalSpacing(15)
        renderer_config.setVerticalSpacing(10)
        
        self.renderer_timestep_spin = QSpinBox()
        self.renderer_timestep_spin.setRange(1, 24)
        self.renderer_timestep_spin.setValue(6)
        self.renderer_timestep_spin.setSuffix(" hora(s)")
        self.renderer_timestep_spin.setMinimumHeight(30)
        
        # Tamanho da imagem
        size_frame = QFrame()
        size_layout = QGridLayout(size_frame)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setHorizontalSpacing(10)
        size_layout.setVerticalSpacing(0)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 4000)
        self.width_spin.setValue(800)
        self.width_spin.setSuffix(" px")
        self.width_spin.setMinimumHeight(30)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 4000)
        self.height_spin.setValue(600)
        self.height_spin.setSuffix(" px")
        self.height_spin.setMinimumHeight(30)
        
        size_layout.addWidget(self.width_spin, 0, 0)
        size_layout.addWidget(QLabel("×"), 0, 1)
        size_layout.addWidget(self.height_spin, 0, 2)
        size_layout.setColumnStretch(0, 1)
        size_layout.setColumnStretch(2, 1)
        
        # Formato da imagem
        self.image_format_combo = QComboBox()
        self.image_format_combo.addItems(["GIF", "PNG", "JPG"])
        self.image_format_combo.setMinimumHeight(30)
        
        # Criar GIF animado
        self.create_gif_check = QCheckBox("Criar GIF animado ao final")
        self.create_gif_check.setChecked(True)
        self.create_gif_check.setMinimumHeight(30)
        
        renderer_config.addRow("Intervalo de Saída:", self.renderer_timestep_spin)
        renderer_config.addRow("Tamanho:", size_frame)
        renderer_config.addRow("Formato:", self.image_format_combo)
        renderer_config.addRow("", self.create_gif_check)
        
        renderer_layout.addLayout(renderer_config)
        formats_layout.addWidget(renderer_frame)
        
        # ---- KMZ ----
        kmz_frame = QFrame()
        kmz_frame.setFrameStyle(QFrame.StyledPanel)
        kmz_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        kmz_layout = QVBoxLayout(kmz_frame)
        kmz_layout.setContentsMargins(10, 10, 10, 10)
        kmz_layout.setSpacing(10)
        
        # Título com checkbox
        kmz_header = QHBoxLayout()
        self.kmz_check = QCheckBox("KMZ (Google Earth)")
        self.kmz_check.setChecked(False)
        self.kmz_check.toggled.connect(self.toggle_kmz_options)
        self.kmz_check.setStyleSheet("font-weight: bold;")
        self.kmz_check.setMinimumHeight(30)
        
        kmz_header.addWidget(self.kmz_check)
        kmz_header.addStretch(1)
        
        kmz_layout.addLayout(kmz_header)
        
        # Configurações específicas do KMZ
        kmz_config = QFormLayout()
        kmz_config.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        kmz_config.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        kmz_config.setContentsMargins(20, 0, 0, 0)
        kmz_config.setHorizontalSpacing(15)
        kmz_config.setVerticalSpacing(10)
        
        self.kmz_timestep_spin = QSpinBox()
        self.kmz_timestep_spin.setRange(1, 24)
        self.kmz_timestep_spin.setValue(6)
        self.kmz_timestep_spin.setSuffix(" hora(s)")
        self.kmz_timestep_spin.setMinimumHeight(30)
        self.kmz_timestep_spin.setEnabled(False)
        
        kmz_config.addRow("Intervalo de Saída:", self.kmz_timestep_spin)
        
        # Descrição
        kmz_desc = QLabel("Gera um arquivo KMZ que pode ser aberto no Google Earth ou outros visualizadores compatíveis.")
        kmz_desc.setWordWrap(True)
        kmz_desc.setStyleSheet("color: #2c3e50; font-style: italic;")
        kmz_layout.addLayout(kmz_config)
        kmz_layout.addWidget(kmz_desc)
        
        formats_layout.addWidget(kmz_frame)
        
        # ---- ERMA ----
        erma_frame = QFrame()
        erma_frame.setFrameStyle(QFrame.StyledPanel)
        erma_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        erma_layout = QVBoxLayout(erma_frame)
        erma_layout.setContentsMargins(10, 10, 10, 10)
        erma_layout.setSpacing(10)
        
        # Título com checkbox
        erma_header = QHBoxLayout()
        self.erma_check = QCheckBox("ERMA (Environmental Response Management Application)")
        self.erma_check.setChecked(False)
        self.erma_check.toggled.connect(self.toggle_erma_options)
        self.erma_check.setStyleSheet("font-weight: bold;")
        self.erma_check.setMinimumHeight(30)
        
        erma_header.addWidget(self.erma_check)
        erma_header.addStretch(1)
        
        erma_layout.addLayout(erma_header)
        
        # Configurações específicas do ERMA
        erma_config = QFormLayout()
        erma_config.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        erma_config.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        erma_config.setContentsMargins(20, 0, 0, 0)
        erma_config.setHorizontalSpacing(15)
        erma_config.setVerticalSpacing(10)
        
        self.erma_timestep_spin = QSpinBox()
        self.erma_timestep_spin.setRange(1, 24)
        self.erma_timestep_spin.setValue(6)
        self.erma_timestep_spin.setSuffix(" hora(s)")
        self.erma_timestep_spin.setMinimumHeight(30)
        self.erma_timestep_spin.setEnabled(False)
        
        erma_config.addRow("Intervalo de Saída:", self.erma_timestep_spin)
        
        # Descrição
        erma_desc = QLabel("Gera arquivos compatíveis com o sistema ERMA da NOAA para gerenciamento de respostas ambientais.")
        erma_desc.setWordWrap(True)
        erma_desc.setStyleSheet("color: #2c3e50; font-style: italic;")
        erma_layout.addLayout(erma_config)
        erma_layout.addWidget(erma_desc)
        
        formats_layout.addWidget(erma_frame)
        
        formats_group.setLayout(formats_layout)
        scroll_layout.addWidget(formats_group)
        
        # =====================================================
        # SEÇÃO 3: VARIÁVEIS A SALVAR
        # =====================================================
        variables_group = QGroupBox("Variáveis a Salvar")
        variables_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        variables_layout = QVBoxLayout()
        variables_layout.setContentsMargins(15, 20, 15, 15)
        variables_layout.setSpacing(15)
        
        # Tabela de variáveis
        self.variables_table = QTableWidget(8, 2)
        self.variables_table.setHorizontalHeaderLabels(["Variável", "Salvar"])
        self.variables_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.variables_table.setMinimumHeight(240)
        self.variables_table.setAlternatingRowColors(True)
        self.variables_table.setStyleSheet("""
            QTableWidget {
                background-color: white; 
                alternate-background-color: #f5f5f5; 
                gridline-color: #ddd;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # Preencher a tabela com variáveis específicas do PyGNOME
        variables = [
            "Posição", 
            "Idade", 
            "Massa", 
            "Densidade", 
            "Diâmetro", 
            "Viscosidade", 
            "Tipo de óleo",
            "Estado (superfície/afundado/encalhado)"
        ]
        
        for i, var in enumerate(variables):
            # Criar a célula de nome da variável
            item = QTableWidgetItem(var)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.variables_table.setItem(i, 0, item)
            
            # Criar a célula com checkbox
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)
            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(Qt.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            
            check_layout.addWidget(checkbox)
            self.variables_table.setCellWidget(i, 1, check_widget)
            
        self.variables_table.resizeRowsToContents()
        variables_layout.addWidget(self.variables_table)
        
        # Opção para salvar todas as variáveis
        save_all_frame = QFrame()
        save_all_layout = QHBoxLayout(save_all_frame)
        save_all_layout.setContentsMargins(0, 0, 0, 0)
        save_all_layout.setSpacing(0)
        
        self.save_all_variables = QCheckBox("Salvar todas as variáveis disponíveis")
        self.save_all_variables.setChecked(False)
        self.save_all_variables.toggled.connect(self.toggle_save_all_variables)
        self.save_all_variables.setMinimumHeight(30)
        
        save_all_layout.addWidget(self.save_all_variables)
        save_all_layout.addStretch(1)
        
        variables_layout.addWidget(save_all_frame)
        
        variables_group.setLayout(variables_layout)
        scroll_layout.addWidget(variables_group)
        
        # =====================================================
        # SEÇÃO 4: CONFIGURAÇÕES AVANÇADAS
        # =====================================================
        advanced_group = QGroupBox("Configurações Avançadas de Saída")
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
        advanced_layout.setVerticalSpacing(15)
        
        # Frequência de saída
        self.output_frequency_combo = QComboBox()
        self.output_frequency_combo.addItems(["Todos os passos de tempo", "Apenas último passo", "Personalizado"])
        self.output_frequency_combo.setMinimumHeight(30)
        self.output_frequency_combo.currentIndexChanged.connect(self.toggle_custom_frequency)
        
        # Personalizar frequência
        self.custom_frequency_spin = QSpinBox()
        self.custom_frequency_spin.setRange(1, 100)
        self.custom_frequency_spin.setValue(10)
        self.custom_frequency_spin.setSuffix(" passos")
        self.custom_frequency_spin.setMinimumHeight(30)
        self.custom_frequency_spin.setEnabled(False)
        
        # Compressão para NetCDF
        compression_frame = QFrame()
        compression_layout = QHBoxLayout(compression_frame)
        compression_layout.setContentsMargins(0, 0, 0, 0)
        compression_layout.setSpacing(0)
        
        self.compression_check = QCheckBox("Usar compressão para arquivos NetCDF")
        self.compression_check.setChecked(True)
        self.compression_check.setMinimumHeight(30)
        
        compression_layout.addWidget(self.compression_check)
        compression_layout.addStretch(1)
        
        # Sobrescrever arquivos
        overwrite_frame = QFrame()
        overwrite_layout = QHBoxLayout(overwrite_frame)
        overwrite_layout.setContentsMargins(0, 0, 0, 0)
        overwrite_layout.setSpacing(0)
        
        self.overwrite_check = QCheckBox("Sobrescrever arquivos existentes")
        self.overwrite_check.setChecked(True)
        self.overwrite_check.setMinimumHeight(30)
        
        overwrite_layout.addWidget(self.overwrite_check)
        overwrite_layout.addStretch(1)
        
        advanced_layout.addRow("Frequência de Saída:", self.output_frequency_combo)
        advanced_layout.addRow("Intervalo Personalizado:", self.custom_frequency_spin)
        advanced_layout.addRow("", compression_frame)
        advanced_layout.addRow("", overwrite_frame)
        
        advanced_group.setLayout(advanced_layout)
        scroll_layout.addWidget(advanced_group)
        
        # Adicionar espaçador para empurrar tudo para cima
        scroll_layout.addStretch(1)
        
        # Finalizar configuração
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
    def browse_output_dir(self):
        """Abrir diálogo para selecionar diretório de saída"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Diretório de Saída", 
            self.output_dir_input.text()
        )
        
        if dir_path:
            self.output_dir_input.setText(dir_path)
            
    def toggle_netcdf_options(self, enabled):
        """Ativar/desativar opções de NetCDF"""
        self.netcdf_timestep_spin.setEnabled(enabled)
        self.netcdf_data_combo.setEnabled(enabled)
        
    def toggle_renderer_options(self, enabled):
        """Ativar/desativar opções de Renderer"""
        self.renderer_timestep_spin.setEnabled(enabled)
        self.width_spin.setEnabled(enabled)
        self.height_spin.setEnabled(enabled)
        self.image_format_combo.setEnabled(enabled)
        self.create_gif_check.setEnabled(enabled)
        
    def toggle_kmz_options(self, enabled):
        """Ativar/desativar opções de KMZ"""
        self.kmz_timestep_spin.setEnabled(enabled)
        
    def toggle_erma_options(self, enabled):
        """Ativar/desativar opções de ERMA"""
        self.erma_timestep_spin.setEnabled(enabled)
        
    def toggle_save_all_variables(self, checked):
        """Ativar/desativar todas as variáveis"""
        for i in range(self.variables_table.rowCount()):
            widget = self.variables_table.cellWidget(i, 1)
            if widget:
                # Acessar o checkbox dentro do layout do widget
                layout = widget.layout()
                checkbox = layout.itemAt(0).widget()
                if checkbox and isinstance(checkbox, QCheckBox):
                    checkbox.setChecked(checked)
                    checkbox.setEnabled(not checked)
    
    def toggle_custom_frequency(self, index):
        """Ativar/desativar configuração de frequência personalizada"""
        self.custom_frequency_spin.setEnabled(index == 2)  # 2 = "Personalizado"
                
    def reset(self):
        """Redefine o widget para valores padrão"""
        self.output_dir_input.setText(os.path.join(os.getcwd(), "output"))
        
        self.netcdf_check.setChecked(True)
        self.netcdf_timestep_spin.setValue(1)
        self.netcdf_data_combo.setCurrentIndex(0)
        
        self.renderer_check.setChecked(True)
        self.renderer_timestep_spin.setValue(6)
        self.width_spin.setValue(800)
        self.height_spin.setValue(600)
        self.image_format_combo.setCurrentIndex(0)
        self.create_gif_check.setChecked(True)
        
        self.kmz_check.setChecked(False)
        self.kmz_timestep_spin.setValue(6)
        self.kmz_timestep_spin.setEnabled(False)
        
        self.erma_check.setChecked(False)
        self.erma_timestep_spin.setValue(6)
        self.erma_timestep_spin.setEnabled(False)
        
        self.save_all_variables.setChecked(False)
        for i in range(self.variables_table.rowCount()):
            widget = self.variables_table.cellWidget(i, 1)
            if widget:
                # Acessar o checkbox dentro do layout do widget
                layout = widget.layout()
                checkbox = layout.itemAt(0).widget()
                if checkbox and isinstance(checkbox, QCheckBox):
                    checkbox.setChecked(True)
                    checkbox.setEnabled(True)
                
        self.output_frequency_combo.setCurrentIndex(0)
        self.custom_frequency_spin.setValue(10)
        self.custom_frequency_spin.setEnabled(False)
        self.compression_check.setChecked(True)
        self.overwrite_check.setChecked(True)
                
    def get_config(self):
        """Retorna a configuração atual das saídas"""
        config = {
            'output_dir': self.output_dir_input.text(),
            'netcdf': {
                'enabled': self.netcdf_check.isChecked(),
                'output_timestep': self.netcdf_timestep_spin.value() * 3600,  # Em segundos
                'data_level': ['standard', 'minimum', 'maximum'][self.netcdf_data_combo.currentIndex()]
            },
            'renderer': {
                'enabled': self.renderer_check.isChecked(),
                'output_timestep': self.renderer_timestep_spin.value() * 3600,  # Em segundos
                'size': (self.width_spin.value(), self.height_spin.value()),
                'format': self.image_format_combo.currentText().lower(),
                'create_gif': self.create_gif_check.isChecked()
            },
            'kml': {
                'enabled': self.kmz_check.isChecked(),
                'output_timestep': self.kmz_timestep_spin.value() * 3600  # Em segundos
            },
            'erma': {
                'enabled': self.erma_check.isChecked(),
                'output_timestep': self.erma_timestep_spin.value() * 3600  # Em segundos
            },
            'variables': self._get_selected_variables(),
            'advanced': {
                'output_frequency': ['all', 'last', 'custom'][self.output_frequency_combo.currentIndex()],
                'custom_frequency': self.custom_frequency_spin.value() if self.output_frequency_combo.currentIndex() == 2 else None,
                'compression': self.compression_check.isChecked(),
                'overwrite': self.overwrite_check.isChecked()
            }
        }
        
        return config
        
    def _get_selected_variables(self):
        """Retorna lista de variáveis selecionadas para salvar"""
        if self.save_all_variables.isChecked():
            return "all"
            
        selected = []
        variables = [
            "position", 
            "age", 
            "mass", 
            "density", 
            "diameter", 
            "viscosity", 
            "oil_type",
            "status"
        ]
        
        for i, var_name in enumerate(variables):
            widget = self.variables_table.cellWidget(i, 1)
            if widget:
                # Acessar o checkbox dentro do layout do widget
                layout = widget.layout()
                checkbox = layout.itemAt(0).widget()
                if checkbox and isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    selected.append(var_name)
                
        return selected
        
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
                QCheckBox, QRadioButton {
                    color: #ecf0f1;
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
                QFrame {
                    background-color: #34495e;
                    border: 1px solid #2c3e50;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QTableWidget {
                    background-color: #2c3e50; 
                    alternate-background-color: #34495e; 
                    gridline-color: #7f8c8d;
                    border: 1px solid #7f8c8d;
                }
                QTableWidget::item {
                    color: #ecf0f1;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                }
                QScrollBar:vertical {
                    background-color: #2c3e50;
                    width: 14px;
                    margin: 14px 0 14px 0;
                }
                QScrollBar::handle:vertical {
                    background-color: #3498db;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """)
            
            # Ajustar estilos específicos para frames
            for frame in self.findChildren(QFrame):
                if frame.frameStyle() == QFrame.StyledPanel:
                    frame.setStyleSheet("""
                        background-color: #34495e;
                        border: 1px solid #2c3e50;
                        border-radius: 5px;
                    """)
                    
            # Ajustar estilos específicos para labels informativos
            for child in self.findChildren(QLabel):
                if "font-style: italic;" in child.styleSheet():
                    child.setStyleSheet("color: #bdc3c7; font-style: italic;")
        else:
            # Tema claro - resetar para o padrão
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            
            # Restaurar estilos específicos para frames
            for frame in self.findChildren(QFrame):
                if frame.frameStyle() == QFrame.StyledPanel:
                    frame.setStyleSheet("""
                        background-color: #f8f8f8;
                        border-radius: 5px;
                        border: 1px solid #ddd;
                    """)
                    
            # Restaurar estilos específicos para labels informativos
            for child in self.findChildren(QLabel):
                if "font-style: italic;" in child.styleSheet():
                    child.setStyleSheet("color: #2c3e50; font-style: italic;")
                    
            # Restaurar estilo da tabela
            self.variables_table.setStyleSheet("""
                QTableWidget {
                    background-color: white; 
                    alternate-background-color: #f5f5f5; 
                    gridline-color: #ddd;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                QHeaderView::section {
                    background-color: #e0e0e0;
                    padding: 5px;
                    border: 1px solid #ddd;
                    font-weight: bold;
                }
            """)