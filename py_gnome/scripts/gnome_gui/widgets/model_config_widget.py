
import os
import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox, 
                              QLabel, QDateTimeEdit, QSpinBox, 
                              QDoubleSpinBox, QComboBox, QCheckBox, QHBoxLayout,
                              QGridLayout, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QDateTime

class ModelConfigWidget(QWidget):
    """Widget para configuração do modelo PyGNOME"""
    
    def __init__(self, parent=None):
        super(ModelConfigWidget, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        # Layout principal com mais espaço entre seções
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Adicionar margens
        layout.setSpacing(25)  # Bastante espaço entre seções
        
        # =====================================================
        # SEÇÃO 1: CONFIGURAÇÕES BÁSICAS
        # =====================================================
        basic_group = QGroupBox("Configurações Básicas do Modelo")
        form_layout = QFormLayout(basic_group)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setHorizontalSpacing(20)  # Espaço entre label e campo
        form_layout.setVerticalSpacing(15)    # Espaço entre linhas
        form_layout.setContentsMargins(10, 20, 10, 20)  # Margens internas
        
        # Tempo inicial
        self.start_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_edit.setCalendarPopup(True)
        self.start_time_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
        form_layout.addRow("Tempo Inicial:", self.start_time_edit)
        
        # Duração - Solução especializada com layout em grade
        duration_frame = QFrame()
        duration_grid = QGridLayout(duration_frame)
        duration_grid.setContentsMargins(0, 0, 0, 0)
        duration_grid.setHorizontalSpacing(10)
        
        # Adicionar cada componente separadamente em um grid para garantir o alinhamento perfeito
        days_label = QLabel("Dias:")
        self.duration_days_spin = QSpinBox()
        self.duration_days_spin.setRange(0, 365)
        self.duration_days_spin.setValue(0)
        self.duration_days_spin.setSuffix(" dias")
        
        hours_label = QLabel("Horas:")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 23)
        self.duration_spin.setValue(23)
        self.duration_spin.setSuffix(" horas")
        
        # Posicionar em um grid de 1x4
        duration_grid.addWidget(days_label, 0, 0)
        duration_grid.addWidget(self.duration_days_spin, 0, 1)
        duration_grid.addWidget(hours_label, 0, 2)
        duration_grid.addWidget(self.duration_spin, 0, 3)
        duration_grid.setColumnStretch(4, 1)  # Última coluna recebe o stretch
        
        form_layout.addRow("Duração:", duration_frame)
        
        # Passo de tempo
        self.time_step_spin = QSpinBox()
        self.time_step_spin.setRange(1, 3600)
        self.time_step_spin.setValue(15 * 60)
        self.time_step_spin.setSuffix(" segundos")
        form_layout.addRow("Passo de Tempo:", self.time_step_spin)
        
        # Método numérico
        self.num_method_combo = QComboBox()
        self.num_method_combo.addItems(["Euler", "RK2 (Runge-Kutta 2ª ordem)", "RK4 (Runge-Kutta 4ª ordem)"])
        self.num_method_combo.setCurrentIndex(1)
        form_layout.addRow("Método Numérico:", self.num_method_combo)
        
        layout.addWidget(basic_group)
        
        # Adicionar espaçador para separar as seções
        layout.addSpacing(10)
        
        # =====================================================
        # SEÇÃO 2: CONFIGURAÇÕES DO AMBIENTE
        # =====================================================
        env_group = QGroupBox("Configurações do Ambiente")
        env_layout = QFormLayout(env_group)
        env_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        env_layout.setHorizontalSpacing(20)  # Espaço entre label e campo
        env_layout.setVerticalSpacing(15)    # Espaço entre linhas
        env_layout.setContentsMargins(10, 20, 10, 20)  # Margens internas
        
        # Temperatura da água
        self.water_temp_spin = QDoubleSpinBox()
        self.water_temp_spin.setRange(-2, 40)
        self.water_temp_spin.setValue(15.0)
        self.water_temp_spin.setSuffix(" °C")
        self.water_temp_spin.setDecimals(2)
        env_layout.addRow("Temperatura da Água:", self.water_temp_spin)
        
        # Salinidade
        self.salinity_spin = QDoubleSpinBox()
        self.salinity_spin.setRange(0, 40)
        self.salinity_spin.setValue(35.0)
        self.salinity_spin.setSuffix(" ppt")
        self.salinity_spin.setDecimals(2)
        env_layout.addRow("Salinidade:", self.salinity_spin)
        
        # Altura significativa de onda
        self.wave_height_spin = QDoubleSpinBox()
        self.wave_height_spin.setRange(0, 20)
        self.wave_height_spin.setValue(1.0)
        self.wave_height_spin.setSuffix(" m")
        self.wave_height_spin.setDecimals(2)
        env_layout.addRow("Altura Significativa de Onda:", self.wave_height_spin)
        
        # Usar modelo de ondas
        self.use_wave_model = QCheckBox("Usar modelo de ondas (se disponível)")
        self.use_wave_model.setChecked(False)
        env_layout.addRow("", self.use_wave_model)
        
        layout.addWidget(env_group)
        
        # Adicionar espaçador para separar as seções
        layout.addSpacing(10)
        
        # =====================================================
        # SEÇÃO 3: CONFIGURAÇÕES AVANÇADAS
        # =====================================================
        advanced_group = QGroupBox("Configurações Avançadas")
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        advanced_layout.setHorizontalSpacing(20)  # Espaço entre label e campo
        advanced_layout.setVerticalSpacing(15)    # Espaço entre linhas
        advanced_layout.setContentsMargins(10, 20, 10, 20)  # Margens internas
        
        # Usar profundidade 3D
        self.use_3d = QCheckBox("Usar simulação 3D (profundidade)")
        self.use_3d.setChecked(False)
        advanced_layout.addRow("", self.use_3d)
        
        # Semente aleatória
        self.random_seed_spin = QSpinBox()
        self.random_seed_spin.setRange(0, 999999)
        self.random_seed_spin.setValue(0)
        self.random_seed_spin.setSpecialValueText("Auto")
        advanced_layout.addRow("Semente Aleatória:", self.random_seed_spin)
        
        # Incerteza
        self.uncertainty_checkbox = QCheckBox("Ativar cálculo de incerteza")
        self.uncertainty_checkbox.setChecked(False)
        advanced_layout.addRow("", self.uncertainty_checkbox)
        
        # Número de iterações
        self.uncertain_iterations_spin = QSpinBox()
        self.uncertain_iterations_spin.setRange(2, 1000)
        self.uncertain_iterations_spin.setValue(10)
        self.uncertain_iterations_spin.setEnabled(False)
        advanced_layout.addRow("Número de Iterações:", self.uncertain_iterations_spin)
        
        # Conectar mudança no checkbox de incerteza
        self.uncertainty_checkbox.toggled.connect(
            self.uncertain_iterations_spin.setEnabled
        )
        
        layout.addWidget(advanced_group)
        
        # Adicionar espaço flexível no final
        layout.addStretch(1)
    
    def reset(self):
        """Redefine o widget para valores padrão"""
        self.start_time_edit.setDateTime(QDateTime.currentDateTime())
        self.duration_days_spin.setValue(0)
        self.duration_spin.setValue(23)
        self.time_step_spin.setValue(15 * 60)
        self.num_method_combo.setCurrentIndex(1)
        self.water_temp_spin.setValue(15.0)
        self.salinity_spin.setValue(35.0)
        self.wave_height_spin.setValue(1.0)
        self.use_wave_model.setChecked(False)
        self.use_3d.setChecked(False)
        self.random_seed_spin.setValue(0)
        self.uncertainty_checkbox.setChecked(False)
        self.uncertain_iterations_spin.setValue(10)
        self.uncertain_iterations_spin.setEnabled(False)
        
    def get_config(self):
        """Retorna a configuração atual do modelo"""
        # Calcular a duração total em horas
        duration_hours = self.duration_days_spin.value() * 24 + self.duration_spin.value()
        
        # Converter QDateTime para string no formato YYYY-MM-DDThh:mm:ss
        start_time_str = self.start_time_edit.dateTime().toString("yyyy-MM-ddThh:mm:ss")
        
        # Mapear índice de método numérico para string
        num_methods = ["euler", "rk2", "rk4"]
        num_method = num_methods[self.num_method_combo.currentIndex()]
        
        # Configuração do modelo
        config = {
            'start_time': start_time_str,
            'duration': duration_hours,
            'time_step': self.time_step_spin.value(),
            'num_method': num_method,
            'water_temp': self.water_temp_spin.value(),
            'salinity': self.salinity_spin.value(),
            'wave_height': self.wave_height_spin.value(),
            'use_wave_model': self.use_wave_model.isChecked(),
            'use_3d': self.use_3d.isChecked(),
            'random_seed': self.random_seed_spin.value() if self.random_seed_spin.value() > 0 else None,
            'uncertainty': {
                'enabled': self.uncertainty_checkbox.isChecked(),
                'iterations': self.uncertain_iterations_spin.value()
            }
        }
        
        return config