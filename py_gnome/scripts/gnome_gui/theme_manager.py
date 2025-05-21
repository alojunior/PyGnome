import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QStyleFactory
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPalette, QColor, QIcon

class ThemeManager:
    """Gerenciador de temas para a aplicação PyGNOME Interface"""
    
    # Cores do tema claro
    LIGHT_THEME = {
        # Cores principais
        'window_background': '#f0f4f8',
        'content_background': '#ffffff',
        'primary_color': '#2c3e50',
        'secondary_color': '#3498db',
        'accent_color': '#27ae60',
        'warning_color': '#e74c3c',
        
        # Cores de texto
        'text_primary': '#2c3e50',
        'text_secondary': '#34495e',
        'text_muted': '#7f8c8d',
        'text_inverted': '#ffffff',
        
        # Cores de bordas e separadores
        'border': '#dcdde1',
        'border_light': '#ecf0f1',
        'border_focus': '#3498db',
        
        # Cores de estados
        'hover': '#ecf0f1',
        'selected': '#3498db',
        'disabled_bg': '#f8f9fa',
        'disabled_text': '#95a5a6',
        
        # Cores de cabeçalhos
        'header_background': '#3498db',
        'header_text': '#ffffff',
        'subheader_background': '#bdc3c7',
        
        # Cores de controle
        'button_background': '#2c3e50',
        'button_hover': '#34495e',
        'button_pressed': '#1c2833',
        'button_text': '#ffffff',
        
        # Cores para elementos específicos
        'success_button_background': '#27ae60',
        'success_button_hover': '#2ecc71',
        'success_button_pressed': '#229954',
        
        'danger_button_background': '#e74c3c',
        'danger_button_hover': '#f75d4d',
        'danger_button_pressed': '#c0392b',
        
        'group_title_background': '#ecf0f1',
        'group_title_text': '#2c3e50',
        
        'console_background': '#1e1e1e',
        'console_text': '#f0f0f0',
        
        'table_header_background': '#e0e0e0',
        'table_alternate_row': '#f5f5f5',
    }
    
    # Cores do tema escuro
    DARK_THEME = {
        # Cores principais
        'window_background': '#1f2937',
        'content_background': '#2c3e50',
        'primary_color': '#ecf0f1',
        'secondary_color': '#3498db',
        'accent_color': '#2ecc71',
        'warning_color': '#e74c3c',
        
        # Cores de texto
        'text_primary': '#ecf0f1',
        'text_secondary': '#bdc3c7',
        'text_muted': '#95a5a6',
        'text_inverted': '#2c3e50',
        
        # Cores de bordas e separadores
        'border': '#34495e',
        'border_light': '#2c3e50',
        'border_focus': '#3498db',
        
        # Cores de estados
        'hover': '#34495e',
        'selected': '#3498db',
        'disabled_bg': '#2c3e50',
        'disabled_text': '#7f8c8d',
        
        # Cores de cabeçalhos
        'header_background': '#2c3e50',
        'header_text': '#3498db',
        'subheader_background': '#34495e',
        
        # Cores de controle
        'button_background': '#3498db',
        'button_hover': '#2980b9',
        'button_pressed': '#1b6698',
        'button_text': '#ffffff',
        
        # Cores para elementos específicos
        'success_button_background': '#27ae60',
        'success_button_hover': '#2ecc71',
        'success_button_pressed': '#229954',
        
        'danger_button_background': '#e74c3c',
        'danger_button_hover': '#f75d4d',
        'danger_button_pressed': '#c0392b',
        
        'group_title_background': '#34495e',
        'group_title_text': '#3498db',
        
        'console_background': '#1a1a1a',
        'console_text': '#f0f0f0',
        
        'table_header_background': '#34495e',
        'table_alternate_row': '#2c3e50',
    }
    
    @staticmethod
    def get_theme_colors(dark_mode=False):
        """Retorna as cores do tema atual"""
        return ThemeManager.DARK_THEME if dark_mode else ThemeManager.LIGHT_THEME
    
    @staticmethod
    def apply_theme_to_app(app, dark_mode=False):
        """Aplica o tema selecionado à aplicação"""
        if dark_mode:
            # Aplicar tema escuro nativo do Qt
            app.setStyle("Fusion")
            palette = QPalette()
            
            # Cores gerais
            palette.setColor(QPalette.Window, QColor(ThemeManager.DARK_THEME['window_background']))
            palette.setColor(QPalette.WindowText, QColor(ThemeManager.DARK_THEME['text_primary']))
            palette.setColor(QPalette.Base, QColor(ThemeManager.DARK_THEME['content_background']))
            palette.setColor(QPalette.AlternateBase, QColor(ThemeManager.DARK_THEME['table_alternate_row']))
            palette.setColor(QPalette.ToolTipBase, QColor(ThemeManager.DARK_THEME['content_background']))
            palette.setColor(QPalette.ToolTipText, QColor(ThemeManager.DARK_THEME['text_primary']))
            palette.setColor(QPalette.Text, QColor(ThemeManager.DARK_THEME['text_primary']))
            palette.setColor(QPalette.Button, QColor(ThemeManager.DARK_THEME['button_background']))
            palette.setColor(QPalette.ButtonText, QColor(ThemeManager.DARK_THEME['button_text']))
            palette.setColor(QPalette.BrightText, Qt.red)
            
            # Cores de destaque
            palette.setColor(QPalette.Link, QColor(ThemeManager.DARK_THEME['secondary_color']))
            palette.setColor(QPalette.Highlight, QColor(ThemeManager.DARK_THEME['selected']))
            palette.setColor(QPalette.HighlightedText, QColor(ThemeManager.DARK_THEME['text_inverted']))
            
            # Aplicar palette
            app.setPalette(palette)
        else:
            # Voltar para o tema padrão
            app.setStyle("Fusion")
            app.setPalette(app.style().standardPalette())
    
    @staticmethod
    def get_group_box_style(dark_mode=False):
        """Retorna o estilo para QGroupBox"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 12px;
                border: 1px solid {colors['border']};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {colors['secondary_color']};
            }}
        """
    
    @staticmethod
    def get_header_style(dark_mode=False):
        """Retorna o estilo para cabeçalhos"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QLabel[isHeader=true] {{
                background-color: {colors['header_background']};
                color: {colors['header_text']};
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
            }}
        """
    
    @staticmethod
    def get_button_style(dark_mode=False, type="normal"):
        """Retorna o estilo para botões"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        
        if type == "success":
            bg = colors['success_button_background']
            hover = colors['success_button_hover']
            pressed = colors['success_button_pressed']
        elif type == "danger":
            bg = colors['danger_button_background']
            hover = colors['danger_button_hover']
            pressed = colors['danger_button_pressed']
        else:
            bg = colors['button_background']
            hover = colors['button_hover']
            pressed = colors['button_pressed']
            
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {colors['button_text']};
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
        """
        
    @staticmethod
    def get_gradient_button_style(dark_mode=False, type="normal"):
        """Retorna o estilo para botões com gradiente"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        
        if type == "success":
            bg_start = colors['success_button_hover']
            bg_end = colors['success_button_background']
            hover_start = colors['success_button_hover']
            hover_end = colors['success_button_hover']
            pressed_start = colors['success_button_pressed']
            pressed_end = colors['success_button_background']
        elif type == "danger":
            bg_start = colors['danger_button_hover']
            bg_end = colors['danger_button_background']
            hover_start = colors['danger_button_hover']
            hover_end = colors['danger_button_hover']
            pressed_start = colors['danger_button_pressed']
            pressed_end = colors['danger_button_background']
        else:
            bg_start = colors['button_hover']
            bg_end = colors['button_background']
            hover_start = colors['button_hover']
            hover_end = colors['button_hover']
            pressed_start = colors['button_pressed']
            pressed_end = colors['button_background']
            
        return f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 {bg_start}, stop:1 {bg_end});
                color: {colors['button_text']};
                border-radius: 4px;
                border: none;
                padding: 5px;
                min-height: 25px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 {pressed_start}, stop:1 {pressed_end});
            }}
            QPushButton:disabled {{
                background-color: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
        """
    
    @staticmethod
    def get_input_style(dark_mode=False):
        """Retorna o estilo para campos de entrada"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QLineEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit, QComboBox {{
                background-color: {colors['content_background']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 2px 5px;
                min-height: 25px;
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateTimeEdit:hover, QComboBox:hover {{
                border: 1px solid {colors['border_focus']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus {{
                border: 1px solid {colors['selected']};
            }}
            QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QDateTimeEdit:disabled, QComboBox:disabled {{
                background-color: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
        """
    
    @staticmethod
    def get_checkbox_style(dark_mode=False):
        """Retorna o estilo para checkboxes"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QCheckBox {{
                spacing: 5px;
                color: {colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 1px solid {colors['border']};
                background-color: {colors['content_background']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                border: 1px solid {colors['secondary_color']};
                background-color: {colors['secondary_color']};
                border-radius: 3px;
            }}
            QCheckBox:disabled {{
                color: {colors['disabled_text']};
            }}
            QCheckBox::indicator:disabled {{
                border: 1px solid {colors['disabled_text']};
                background-color: {colors['disabled_bg']};
            }}
        """
    
    @staticmethod
    def get_radio_style(dark_mode=False):
        """Retorna o estilo para radio buttons"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QRadioButton {{
                spacing: 5px;
                color: {colors['text_primary']};
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 1px solid {colors['border']};
                background-color: {colors['content_background']};
                border-radius: 9px;
            }}
            QRadioButton::indicator:checked {{
                border: 1px solid {colors['secondary_color']};
                background-color: {colors['content_background']};
                border-radius: 9px;
            }}
            QRadioButton::indicator:checked:enabled {{
                image: url(resources/check-circle.png);
            }}
            QRadioButton:disabled {{
                color: {colors['disabled_text']};
            }}
        """
    
    @staticmethod
    def get_table_style(dark_mode=False):
        """Retorna o estilo para tabelas"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QTableWidget {{
                background-color: {colors['content_background']}; 
                alternate-background-color: {colors['table_alternate_row']}; 
                gridline-color: {colors['border']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QTableWidget::item {{
                padding: 5px;
                color: {colors['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {colors['table_header_background']};
                padding: 5px;
                border: 1px solid {colors['border']};
                color: {colors['text_primary']};
                font-weight: bold;
            }}
        """
    
    @staticmethod
    def get_tab_style(dark_mode=False):
        """Retorna o estilo para abas"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['content_background']};
                padding: 5px;
            }}
            QTabBar::tab {{
                background: {colors['window_background']};
                padding: 8px 15px;
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                color: {colors['text_primary']};
            }}
            QTabBar::tab:selected {{
                background: {colors['content_background']};
                border-bottom-color: {colors['content_background']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {colors['hover']};
            }}
        """
    
    @staticmethod
    def get_progress_bar_style(dark_mode=False):
        """Retorna o estilo para barras de progresso"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                text-align: center;
                background-color: {colors['window_background']};
                height: 25px;
                color: {colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                             stop:0 {colors['secondary_color']}, stop:1 #2980b9);
                width: 10px;
                border-radius: 2px;
            }}
        """
    
    @staticmethod
    def get_console_style(dark_mode=False):
        """Retorna o estilo para console de log"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QTextEdit {{
                background-color: {colors['console_background']};
                color: {colors['console_text']};
                font-family: Consolas, Courier New, monospace;
                font-size: 10pt;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px;
            }}
        """
    
    @staticmethod
    def get_section_header_style(dark_mode=False):
        """Retorna o estilo para cabeçalhos de seção"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        return f"""
            QLabel[sectionHeader=true] {{
                background-color: {colors['header_background']};
                color: {colors['header_text']};
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 3px;
                min-height: 20px;
            }}
        """
    
    @staticmethod
    def get_frame_style(dark_mode=False, type="normal"):
        """Retorna o estilo para frames"""
        colors = ThemeManager.get_theme_colors(dark_mode)
        
        if type == "content":
            return f"""
                QFrame {{
                    background-color: {colors['content_background']};
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                }}
            """
        elif type == "highlighted":
            return f"""
                QFrame {{
                    background-color: {colors['hover']};
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                }}
            """
        else:
            return f"""
                QFrame {{
                    background-color: {colors['window_background']};
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                }}
            """
            
    @staticmethod
    def apply_theme_to_widget(widget, dark_mode=False):
        """Aplica o tema atual a um widget específico"""
        # Esse método seria chamado para cada widget específico (ModelConfigWidget, SpillConfigWidget, etc.)
        # implementando a lógica específica para cada tipo de widget
        pass