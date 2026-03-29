"""
Dialogs Module
Custom dialogs for the Video Repurposing Application
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QSlider,
    QSpinBox,
    QColorDialog,
    QFileDialog,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter


class URLDialog(QDialog):
    """Dialog for entering YouTube or Twitter/X URL"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Download from URL")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # URL input
        layout.addWidget(QLabel("Enter YouTube or Twitter/X URL:"))

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://www.youtube.com/watch?v=... or https://x.com/.../status/..."
        )
        layout.addWidget(self.url_input)

        # Quality selection
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(
            ["Best (recommended)", "Best video + audio", "1080p", "720p", "480p"]
        )
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()

        layout.addLayout(quality_layout)

        # Info text
        info_label = QLabel(
            "Note: Video will be downloaded to the exports folder. "
            "Large videos may take some time."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.accept)
        self.download_btn.setDefault(True)
        button_layout.addWidget(self.download_btn)

        layout.addLayout(button_layout)

    def get_url(self) -> str:
        """Get the entered URL"""
        return self.url_input.text().strip()

    def get_quality(self) -> str:
        """Get selected quality"""
        quality_map = {
            "Best (recommended)": "best",
            "Best video + audio": "bestvideo+bestaudio",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "best[height<=480]",
        }
        return quality_map.get(self.quality_combo.currentText(), "best")


class ExportDialog(QDialog):
    """Dialog for clip export options"""

    def __init__(self, clip_title: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Export Clip")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Clip info
        layout.addWidget(QLabel(f"Exporting: {clip_title}"))

        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                "Instagram Reels (9:16, 90s)",
                "YouTube Shorts (9:16, 60s)",
                "TikTok (9:16, 3min)",
                "Landscape (16:9)",
                "Square (1:1)",
            ]
        )
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Options
        self.subtitles_check = QPushButton("Add subtitles")
        self.subtitles_check.setCheckable(True)
        self.subtitles_check.setChecked(True)
        layout.addWidget(self.subtitles_check)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.accept)
        export_btn.setDefault(True)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

    def get_format(self) -> str:
        """Get selected format"""
        formats = {
            "Instagram Reels (9:16, 90s)": "reels",
            "YouTube Shorts (9:16, 60s)": "shorts",
            "TikTok (9:16, 3min)": "tiktok",
            "Landscape (16:9)": "landscape",
            "Square (1:1)": "square",
        }
        return formats.get(self.format_combo.currentText(), "reels")


class SettingsDialog(QDialog):
    """Settings dialog for app configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # AI Settings
        ai_group_layout = QVBoxLayout()
        ai_group_layout.addWidget(QLabel("<b>AI Settings</b>"))

        # Whisper model
        whisper_layout = QHBoxLayout()
        whisper_layout.addWidget(QLabel("Whisper Model:"))

        self.whisper_combo = QComboBox()
        self.whisper_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.whisper_combo.setCurrentText("small")
        whisper_layout.addWidget(self.whisper_combo)

        info_label = QLabel(
            "(smaller = faster; medium/large recommended for Hindi & non-English)"
        )
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        whisper_layout.addWidget(info_label)

        ai_group_layout.addLayout(whisper_layout)

        # LLM provider
        llm_layout = QHBoxLayout()
        llm_layout.addWidget(QLabel("LLM Provider:"))

        self.llm_combo = QComboBox()
        self.llm_combo.addItems(
            ["OpenAI", "Anthropic", "Ollama", "None (rule-based only)"]
        )
        llm_layout.addWidget(self.llm_combo)

        ai_group_layout.addLayout(llm_layout)

        layout.addLayout(ai_group_layout)

        # Output Settings
        output_group_layout = QVBoxLayout()
        output_group_layout.addWidget(QLabel("<b>Output Settings</b>"))

        output_dir_label = QLabel("Output Directory: exports/")
        output_group_layout.addWidget(output_dir_label)

        layout.addLayout(output_group_layout)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            "whisper_model": self.whisper_combo.currentText(),
            "llm_provider": self.llm_combo.currentText().lower(),
        }


class EditClipDialog(QDialog):
    """Dialog for editing a detected clip's properties"""

    def __init__(self, clip_data: dict, max_duration: float = 0, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Clip")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setText(clip_data.get("title", ""))
        self.title_input.setMaxLength(200)
        layout.addWidget(self.title_input)

        # Timing
        timing_group = QGroupBox("Timing")
        timing_layout = QHBoxLayout()

        timing_layout.addWidget(QLabel("Start (s):"))
        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0, max_duration if max_duration > 0 else 99999)
        self.start_spin.setDecimals(2)
        self.start_spin.setSingleStep(0.5)
        self.start_spin.setValue(clip_data.get("start_time", 0))
        timing_layout.addWidget(self.start_spin)

        timing_layout.addWidget(QLabel("End (s):"))
        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(0, max_duration if max_duration > 0 else 99999)
        self.end_spin.setDecimals(2)
        self.end_spin.setSingleStep(0.5)
        self.end_spin.setValue(clip_data.get("end_time", 0))
        timing_layout.addWidget(self.end_spin)

        self.duration_label = QLabel("")
        timing_layout.addWidget(self.duration_label)

        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)

        # Update duration label on value change
        self.start_spin.valueChanged.connect(self._update_duration)
        self.end_spin.valueChanged.connect(self._update_duration)
        self._update_duration()

        # Hook text
        layout.addWidget(QLabel("Hook (first 3 seconds):"))
        self.hook_input = QTextEdit()
        self.hook_input.setPlainText(clip_data.get("hook", ""))
        self.hook_input.setMaximumHeight(80)
        layout.addWidget(self.hook_input)

        # Reason / Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(clip_data.get("reason", ""))
        self.notes_input.setMaximumHeight(60)
        layout.addWidget(self.notes_input)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _update_duration(self):
        duration = self.end_spin.value() - self.start_spin.value()
        self.duration_label.setText(f"({duration:.1f}s)")

    def get_edited_data(self) -> dict:
        """Return the edited clip data"""
        return {
            "title": self.title_input.text().strip(),
            "start_time": self.start_spin.value(),
            "end_time": self.end_spin.value(),
            "hook": self.hook_input.toPlainText().strip(),
            "reason": self.notes_input.toPlainText().strip(),
        }


class CaptionPresetCard(QFrame):
    """Visual card for a caption preset style (shows preview of how text looks)"""

    clicked = Signal(str)  # emits preset key when clicked

    def __init__(self, key: str, preset: dict, parent=None):
        super().__init__(parent)
        self.preset_key = key
        self.preset = preset
        self._selected = False
        self.setFixedSize(220, 80)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        bg = "#3a3a3a" if self._selected else "#2a2a2a"
        border = "#ffffff" if self._selected else "#444444"
        self.setStyleSheet(f"""
            CaptionPresetCard {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 10px;
            }}
        """)

    def setSelected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.preset_key)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        preset = self.preset
        x, y, w, h = (
            self.rect().x(),
            self.rect().y(),
            self.rect().width(),
            self.rect().height(),
        )

        # Draw name at top
        painter.setPen(QColor("#888888"))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(x + 10, y + 16, preset["name"])

        # Draw sample text with the preset style
        sample_text = "TO GET STARTED"
        if preset.get("enabled") is False:
            sample_text = "No captions"
            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Arial", 11))
            painter.drawText(x + 10, y + 50, sample_text)
        else:
            font = QFont(preset["font"], preset["font_size"])
            font.setWeight(
                QFont.Bold if preset["font_weight"] == "bold" else QFont.Normal
            )
            font.setPixelSize(22)

            text_x = x + 10
            text_y = y + 55

            # Draw shadow
            shadow_offset = preset.get("shadow_offset", 0)
            if shadow_offset > 0:
                painter.setPen(QColor(preset["shadow_color"]))
                painter.setFont(font)
                painter.drawText(
                    text_x + shadow_offset, text_y + shadow_offset, sample_text
                )

            # Draw outline
            if preset["outline_width"] > 0:
                pen = QPainter()
                outline_color = QColor(preset["outline_color"])
                painter.setPen(outline_color)
                painter.setFont(font)
                for dx in range(-preset["outline_width"], preset["outline_width"] + 1):
                    for dy in range(
                        -preset["outline_width"], preset["outline_width"] + 1
                    ):
                        if dx != 0 or dy != 0:
                            painter.drawText(text_x + dx, text_y + dy, sample_text)

            # Draw highlight word (simulated - second word in different color)
            if preset.get("word_highlight"):
                painter.setPen(QColor(preset["font_color"]))
                painter.setFont(font)
                painter.drawText(text_x, text_y, "TO ")

                highlight_pen = painter.pen()
                highlight_pen.setColor(QColor(preset["highlight_color"]))
                painter.setPen(highlight_pen)
                metrics = painter.fontMetrics()
                word_width = metrics.horizontalAdvance("TO ")
                painter.drawText(text_x + word_width, text_y, "GET STARTED")
            else:
                painter.setPen(QColor(preset["font_color"]))
                painter.setFont(font)
                painter.drawText(text_x, text_y, sample_text)

        painter.end()


class LogoUploadWidget(QWidget):
    """Widget for uploading/selecting and positioning a logo"""

    logoChanged = Signal(str)  # emits logo path when changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Logo preview
        self.preview_label = QLabel("No logo")
        self.preview_label.setFixedSize(60, 60)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            "border: 1px dashed #666; border-radius: 5px; color: #666; background: #2a2a2a;"
        )
        layout.addWidget(self.preview_label)

        # Controls
        controls = QVBoxLayout()

        btn_row = QHBoxLayout()
        upload_btn = QPushButton("Upload Logo")
        upload_btn.clicked.connect(self._upload_logo)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_logo)
        btn_row.addWidget(upload_btn)
        btn_row.addWidget(remove_btn)
        controls.addLayout(btn_row)

        # Position selector
        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("Position:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(
            ["Bottom Left", "Bottom Right", "Top Left", "Top Right"]
        )
        self.pos_combo.setCurrentIndex(0)
        pos_row.addWidget(self.pos_combo)
        controls.addLayout(pos_row)

        # Size slider
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 300)
        self.size_slider.setValue(150)
        self.size_slider.valueChanged.connect(self._update_size_label)
        size_row.addWidget(self.size_slider)
        self.size_label = QLabel("150px")
        self.size_label.setFixedWidth(40)
        size_row.addWidget(self.size_label)
        controls.addLayout(size_row)

        # Opacity slider
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self._update_opacity_label)
        opacity_row.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("80%")
        self.opacity_label.setFixedWidth(40)
        opacity_row.addWidget(self.opacity_label)
        controls.addLayout(opacity_row)

        layout.addLayout(controls)

    def _update_size_label(self, value):
        self.size_label.setText(f"{value}px")

    def _update_opacity_label(self, value):
        self.opacity_label.setText(f"{value}%")

    def _upload_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.svg);;All Files (*)",
        )
        if path:
            self.logo_path = path
            pixmap = QPixmap(path).scaled(
                56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(pixmap)
            self.logoChanged.emit(path)

    def _remove_logo(self):
        self.logo_path = ""
        self.preview_label.setText("No logo")
        self.preview_label.setPixmap(QPixmap())
        self.logoChanged.emit("")

    def get_settings(self) -> dict:
        positions = ["bottom_left", "bottom_right", "top_left", "top_right"]
        return {
            "logo_path": self.logo_path,
            "position": positions[self.pos_combo.currentIndex()],
            "width": self.size_slider.value(),
            "opacity": self.opacity_slider.value() / 100.0,
        }


class StylePanel(QWidget):
    """Right-side style panel with Presets, Font, Effects tabs (Descript-like UI)"""

    styleChanged = Signal(dict)  # emits current style settings

    def __init__(self, presets: dict = None, parent=None):
        super().__init__(parent)
        self.presets = presets or {}
        self.current_preset_key = ""
        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(260)
        self.setStyleSheet("""
            StylePanel {
                background-color: #1e1e1e;
                border-left: 1px solid #333;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #888888;
                padding: 8px 16px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #ffffff;
            }
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #444;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        title_bar = QLabel("Style")
        title_bar.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 12px; "
            "border-bottom: 1px solid #333; color: #fff;"
        )
        main_layout.addWidget(title_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_presets_tab(), "Presets")
        self.tabs.addTab(self._create_font_tab(), "Font")
        self.tabs.addTab(self._create_effects_tab(), "Effects")
        main_layout.addWidget(self.tabs)

    def _create_presets_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(6)

        self.preset_cards = {}
        for key, preset in self.presets.items():
            card = CaptionPresetCard(key, preset)
            card.clicked.connect(self._on_preset_selected)
            container_layout.addWidget(card, alignment=Qt.AlignCenter)
            self.preset_cards[key] = card

        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return tab

    def _create_font_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)

        # Font family
        layout.addWidget(QLabel("Font Family:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(
            [
                "Arial",
                "Impact",
                "Helvetica",
                "Georgia",
                "Verdana",
                "Trebuchet MS",
                "Comic Sans MS",
                "Courier New",
            ]
        )
        self.font_combo.currentTextChanged.connect(self._on_font_changed)
        layout.addWidget(self.font_combo)

        # Font size
        layout.addWidget(QLabel("Font Size:"))
        size_row = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(16, 80)
        self.font_size_slider.setValue(42)
        self.font_size_slider.valueChanged.connect(self._on_font_size_changed)
        size_row.addWidget(self.font_size_slider)
        self.font_size_label = QLabel("42px")
        self.font_size_label.setFixedWidth(40)
        size_row.addWidget(self.font_size_label)
        layout.addLayout(size_row)

        # Font color
        layout.addWidget(QLabel("Font Color:"))
        color_row = QHBoxLayout()
        self.font_color_btn = QPushButton("#FFFFFF")
        self.font_color_btn.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.font_color_btn.clicked.connect(lambda: self._pick_color("font_color"))
        color_row.addWidget(self.font_color_btn)
        layout.addLayout(color_row)

        # Bold toggle
        self.bold_btn = QPushButton("Bold")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(True)
        self.bold_btn.clicked.connect(self._on_bold_changed)
        layout.addWidget(self.bold_btn)

        layout.addStretch()
        return tab

    def _create_effects_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)

        # Outline
        layout.addWidget(QLabel("Outline Width:"))
        outline_row = QHBoxLayout()
        self.outline_slider = QSlider(Qt.Horizontal)
        self.outline_slider.setRange(0, 8)
        self.outline_slider.setValue(3)
        self.outline_slider.valueChanged.connect(self._on_outline_changed)
        outline_row.addWidget(self.outline_slider)
        self.outline_label = QLabel("3px")
        self.outline_label.setFixedWidth(30)
        outline_row.addWidget(self.outline_label)
        layout.addLayout(outline_row)

        # Outline color
        layout.addWidget(QLabel("Outline Color:"))
        oc_row = QHBoxLayout()
        self.outline_color_btn = QPushButton("#000000")
        self.outline_color_btn.setStyleSheet("background-color: #000000; color: #fff;")
        self.outline_color_btn.clicked.connect(
            lambda: self._pick_color("outline_color")
        )
        oc_row.addWidget(self.outline_color_btn)
        layout.addLayout(oc_row)

        # Background
        layout.addWidget(QLabel("Background Color:"))
        bg_row = QHBoxLayout()
        self.bg_color_btn = QPushButton("None")
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        bg_row.addWidget(self.bg_color_btn)
        layout.addLayout(bg_row)

        # Background opacity
        layout.addWidget(QLabel("Background Opacity:"))
        bgop_row = QHBoxLayout()
        self.bg_opacity_slider = QSlider(Qt.Horizontal)
        self.bg_opacity_slider.setRange(0, 100)
        self.bg_opacity_slider.setValue(70)
        self.bg_opacity_slider.valueChanged.connect(self._on_bg_opacity_changed)
        bgop_row.addWidget(self.bg_opacity_slider)
        self.bg_opacity_label = QLabel("70%")
        self.bg_opacity_label.setFixedWidth(35)
        bgop_row.addWidget(self.bg_opacity_label)
        layout.addLayout(bgop_row)

        # Highlight color (for word highlight)
        layout.addWidget(QLabel("Highlight Color:"))
        hc_row = QHBoxLayout()
        self.highlight_color_btn = QPushButton("#00FF00")
        self.highlight_color_btn.setStyleSheet(
            "background-color: #00FF00; color: #000;"
        )
        self.highlight_color_btn.clicked.connect(
            lambda: self._pick_color("highlight_color")
        )
        hc_row.addWidget(self.highlight_color_btn)
        layout.addLayout(hc_row)

        # Word highlight toggle
        self.word_highlight_btn = QPushButton("Word-by-Word Highlight")
        self.word_highlight_btn.setCheckable(True)
        self.word_highlight_btn.setChecked(True)
        layout.addWidget(self.word_highlight_btn)

        # Shadow
        layout.addWidget(QLabel("Shadow:"))
        shadow_row = QHBoxLayout()
        self.shadow_slider = QSlider(Qt.Horizontal)
        self.shadow_slider.setRange(0, 10)
        self.shadow_slider.setValue(3)
        self.shadow_slider.valueChanged.connect(self._on_shadow_changed)
        shadow_row.addWidget(self.shadow_slider)
        self.shadow_label = QLabel("3px")
        self.shadow_label.setFixedWidth(30)
        shadow_row.addWidget(self.shadow_label)
        layout.addLayout(shadow_row)

        layout.addStretch()
        return tab

    def _on_preset_selected(self, key: str):
        self.current_preset_key = key
        for k, card in self.preset_cards.items():
            card.setSelected(k == key)

        preset = self.presets.get(key, {})
        # Update font tab controls
        font_idx = self.font_combo.findText(preset.get("font", "Arial"))
        if font_idx >= 0:
            self.font_combo.setCurrentIndex(font_idx)
        self.font_size_slider.setValue(preset.get("font_size", 42))
        self.bold_btn.setChecked(preset.get("font_weight") == "bold")

        # Update effects tab controls
        self.outline_slider.setValue(preset.get("outline_width", 3))
        self.bg_opacity_slider.setValue(int(preset.get("bg_opacity", 0.7) * 100))
        self.shadow_slider.setValue(preset.get("shadow_offset", 3))
        self.word_highlight_btn.setChecked(preset.get("word_highlight", True))

        self.styleChanged.emit(self.get_current_style())

    def _on_font_changed(self, text):
        self.styleChanged.emit(self.get_current_style())

    def _on_font_size_changed(self, value):
        self.font_size_label.setText(f"{value}px")
        self.styleChanged.emit(self.get_current_style())

    def _on_bold_changed(self, checked):
        self.styleChanged.emit(self.get_current_style())

    def _on_outline_changed(self, value):
        self.outline_label.setText(f"{value}px")
        self.styleChanged.emit(self.get_current_style())

    def _on_bg_opacity_changed(self, value):
        self.bg_opacity_label.setText(f"{value}%")
        self.styleChanged.emit(self.get_current_style())

    def _on_shadow_changed(self, value):
        self.shadow_label.setText(f"{value}px")
        self.styleChanged.emit(self.get_current_style())

    def _pick_color(self, attr: str):
        color = QColorDialog.getColor(QColor("#ffffff"), self, "Pick Color")
        if color.isValid():
            hex_color = color.name()
            btn = getattr(self, f"{attr}_btn", None)
            if btn:
                btn.setText(hex_color)
                btn.setStyleSheet(f"background-color: {hex_color}; color: #fff;")
            self.styleChanged.emit(self.get_current_style())

    def get_current_style(self) -> dict:
        return {
            "preset": self.current_preset_key,
            "font": self.font_combo.currentText(),
            "font_size": self.font_size_slider.value(),
            "font_weight": "bold" if self.bold_btn.isChecked() else "normal",
            "outline_width": self.outline_slider.value(),
            "bg_opacity": self.bg_opacity_slider.value() / 100.0,
            "shadow_offset": self.shadow_slider.value(),
            "word_highlight": self.word_highlight_btn.isChecked(),
            "font_color": self.font_color_btn.text(),
            "outline_color": self.outline_color_btn.text(),
            "bg_color": None
            if self.bg_color_btn.text() == "None"
            else self.bg_color_btn.text(),
            "highlight_color": self.highlight_color_btn.text(),
        }


class PostDialog(QDialog):
    """Dialog for posting video to Twitter/X"""

    def __init__(self, clip_title: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Post to Twitter/X")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Post to Twitter / X"))
        layout.addWidget(QLabel("Clip: " + clip_title))

        # Tweet text
        layout.addWidget(QLabel("Tweet Text:"))
        self.tweet_text = QTextEdit()
        self.tweet_text.setMaximumHeight(100)
        self.tweet_text.setPlainText(clip_title)
        layout.addWidget(self.tweet_text)

        # Hashtags
        layout.addWidget(QLabel("Hashtags:"))
        self.hashtags_input = QLineEdit()
        self.hashtags_input.setPlaceholderText("#viral #trending #shorts")
        layout.addWidget(self.hashtags_input)

        # Account info
        account_group = QGroupBox("Twitter/X Account")
        account_layout = QVBoxLayout()
        self.account_label = QLabel("Not connected. Click below to authenticate.")
        account_layout.addWidget(self.account_label)
        self.connect_btn = QPushButton("Connect Twitter/X Account")
        account_layout.addWidget(self.connect_btn)
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        self.post_btn = QPushButton("Post Video")
        self.post_btn.setDefault(True)
        self.post_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.post_btn)
        layout.addLayout(btn_row)

    def get_post_data(self) -> dict:
        return {
            "tweet_text": self.tweet_text.toPlainText().strip(),
            "hashtags": self.hashtags_input.text().strip(),
        }


class SubtitleStyleDialog(QDialog):
    """Dialog for customizing subtitle appearance"""

    def __init__(self, current_style: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subtitle Style")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        current = current_style or {}

        # Background color
        layout.addWidget(QLabel("Background Color:"))
        bg_row = QHBoxLayout()
        self.bg_color_btn = QPushButton(current.get("bg_color", "None") or "None")
        self.bg_color_btn.clicked.connect(self._pick_bg_color)
        bg_row.addWidget(self.bg_color_btn)
        layout.addLayout(bg_row)

        # Background opacity
        layout.addWidget(QLabel("Background Opacity:"))
        bgop_row = QHBoxLayout()
        self.bg_opacity_slider = QSlider(Qt.Horizontal)
        self.bg_opacity_slider.setRange(0, 100)
        self.bg_opacity_slider.setValue(int(current.get("bg_opacity", 0.6) * 100))
        bgop_row.addWidget(self.bg_opacity_slider)
        self.bg_opacity_label = QLabel(f"{self.bg_opacity_slider.value()}%")
        bgop_row.addWidget(self.bg_opacity_label)
        self.bg_opacity_slider.valueChanged.connect(
            lambda v: self.bg_opacity_label.setText(f"{v}%")
        )
        layout.addLayout(bgop_row)

        # Font
        layout.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Impact", "Helvetica", "Georgia", "Verdana"])
        self.font_combo.setCurrentText(current.get("font", "Arial"))
        layout.addWidget(self.font_combo)

        # Font size
        layout.addWidget(QLabel("Font Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(12, 80)
        self.font_size.setValue(current.get("font_size", 32))
        layout.addWidget(self.font_size)

        # Font color
        layout.addWidget(QLabel("Font Color:"))
        self.font_color_btn = QPushButton(current.get("font_color", "#FFFFFF"))
        self.font_color_btn.clicked.connect(self._pick_font_color)
        layout.addWidget(self.font_color_btn)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        save_btn = QPushButton("Apply")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _pick_bg_color(self):
        color = QColorDialog.getColor(QColor("#000000"), self, "Background Color")
        if color.isValid():
            self.bg_color_btn.setText(color.name())
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def _pick_font_color(self):
        color = QColorDialog.getColor(QColor("#FFFFFF"), self, "Font Color")
        if color.isValid():
            self.font_color_btn.setText(color.name())
            self.font_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def get_style(self) -> dict:
        bg_text = self.bg_color_btn.text()
        return {
            "bg_color": None if bg_text == "None" else bg_text,
            "bg_opacity": self.bg_opacity_slider.value() / 100.0,
            "font": self.font_combo.currentText(),
            "font_size": self.font_size.value(),
            "font_color": self.font_color_btn.text(),
        }
