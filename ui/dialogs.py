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
)
from PySide6.QtCore import Signal


class URLDialog(QDialog):
    """Dialog for entering YouTube URL"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Download from URL")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # URL input
        layout.addWidget(QLabel("Enter YouTube URL:"))

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
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
