"""
Main Window for Video Repurposing Application
PySide6-based desktop UI with video preview, transcript editor, and clip management
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QGroupBox,
    QComboBox,
    QCheckBox,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QFrame,
    QScrollArea,
    QListView,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PySide6.QtCore import Qt, QTimer, QUrl, Signal, Slot, QSize, QTime, QMimeData
from PySide6.QtGui import (
    QAction,
    QIcon,
    QPixmap,
    QFont,
    QColor,
    QPalette,
    QStandardItemModel,
    QStandardItem,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# Import core modules
from core import config, downloader, transcriber, clip_detector, editor_engine, renderer
from ai import llm_interface


class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    video_loaded = Signal(str)
    transcript_ready = Signal(list)
    clips_detected = Signal(list)
    export_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

        # Core components
        self.downloader: Optional[downloader.VideoDownloader] = None
        self.transcriber: Optional[transcriber.TranscriptionEngine] = None
        self.clip_detector: Optional[clip_detector.ClipDetector] = None
        self.editor: Optional[editor_engine.TranscriptEditor] = None
        self.renderer: Optional[renderer.VideoRenderer] = None
        self.llm: Optional[llm_interface.LLMInterface] = None

        # State
        self.current_video_path: Optional[Path] = None
        self.current_transcript: List[Dict[str, Any]] = []
        self.detected_clips: List[clip_detector.ClipSegment] = []
        self.source_url: Optional[str] = None
        self.youtube_subs_path: Optional[Path] = None
        self._available_srt_files: list = []
        self.current_style: dict = {}
        self.current_logo_settings: dict = {}

        # UI Components
        self.media_player: Optional[QMediaPlayer] = None
        self.audio_output: Optional[QAudioOutput] = None
        self.video_widget: Optional[QVideoWidget] = None

        # Initialize UI
        self.init_ui()
        self.init_components()

        # Set window properties
        self.setWindowTitle("Video Repurposing Studio")
        self.setMinimumSize(*config.WINDOW_MIN_SIZE)

    def init_ui(self):
        """Initialize the user interface"""

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create main content area
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Video preview and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Transcript and clips
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Bottom panel - Status and progress
        bottom_widget = self.create_bottom_panel()
        main_layout.addWidget(bottom_widget)

    def create_menu_bar(self):
        """Create application menu bar"""

        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Video...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_video_file)
        file_menu.addAction(open_action)

        download_action = QAction("&Download from URL...", self)
        download_action.setShortcut("Ctrl+D")
        download_action.triggered.connect(self.download_from_url)
        file_menu.addAction(download_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Clip...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_selected_clip)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create main toolbar"""

        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # Upload button
        upload_btn = QPushButton("📁 Open")
        upload_btn.clicked.connect(self.open_video_file)
        toolbar.addWidget(upload_btn)

        # Download from URL
        url_btn = QPushButton("🌐 From URL")
        url_btn.clicked.connect(self.download_from_url)
        toolbar.addWidget(url_btn)

        toolbar.addSeparator()

        # Language selector for transcription
        toolbar.addWidget(QLabel(" Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [
                "Auto-detect",
                "Hindi (Devanagari)",
                "English",
                "Urdu",
                "Bengali",
                "Tamil",
                "Telugu",
                "Marathi",
                "Gujarati",
                "Kannada",
                "Malayalam",
                "Punjabi",
                "Arabic",
                "Chinese",
                "Japanese",
                "Korean",
                "Spanish",
                "French",
                "German",
            ]
        )
        toolbar.addWidget(self.language_combo)

        # Transcribe button
        transcribe_btn = QPushButton("📝 Transcribe")
        transcribe_btn.clicked.connect(self.transcribe_video)
        toolbar.addWidget(transcribe_btn)

        # Detect clips button
        detect_btn = QPushButton("🎯 Detect Clips")
        detect_btn.clicked.connect(self.detect_clips)
        toolbar.addWidget(detect_btn)

        toolbar.addSeparator()

        # Export button
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_selected_clip)
        toolbar.addWidget(export_btn)

        # Post to Twitter/X button
        self.post_btn = QPushButton("🐦 Post")
        self.post_btn.clicked.connect(self.post_to_twitter)
        self.post_btn.setVisible(False)  # Hidden by default, shown after video load
        toolbar.addWidget(self.post_btn)

        # Logo button
        logo_btn = QPushButton("🖼️ Logo")
        logo_btn.clicked.connect(self.select_logo)
        toolbar.addWidget(logo_btn)

    def create_left_panel(self) -> QWidget:
        """Create left panel with video preview"""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video display group
        video_group = QGroupBox("Video Preview")
        video_layout = QVBoxLayout()

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 300)
        video_layout.addWidget(self.video_widget)

        # Playback controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)

        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)

        controls_layout.addStretch()

        # Volume
        volume_label = QLabel("🔊")
        controls_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)

        video_layout.addLayout(controls_layout)

        # Seek slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.seek_video)
        video_layout.addWidget(self.seek_slider)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # Video info group
        info_group = QGroupBox("Video Information")
        info_layout = QVBoxLayout()

        self.video_title_label = QLabel("No video loaded")
        self.video_title_label.setWordWrap(True)
        info_layout.addWidget(self.video_title_label)

        self.video_duration_label = QLabel("Duration: --")
        info_layout.addWidget(self.video_duration_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Export options group
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                "Reels (9:16)",
                "Shorts (9:16)",
                "TikTok (9:16)",
                "Landscape (16:9)",
                "Square (1:1)",
            ]
        )
        format_layout.addWidget(self.format_combo)
        export_layout.addLayout(format_layout)

        self.add_subtitles_check = QCheckBox("Add subtitles")
        self.add_subtitles_check.setChecked(True)
        export_layout.addWidget(self.add_subtitles_check)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        layout.addStretch()

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with transcript, clips, and style panel"""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        tabs = QTabWidget()

        # Transcript tab
        transcript_tab = self.create_transcript_tab()
        tabs.addTab(transcript_tab, "Transcript")

        # Clips tab
        clips_tab = self.create_clips_tab()
        tabs.addTab(clips_tab, "Detected Clips")

        # Style tab (Descript-like caption style panel)
        from ui.dialogs import StylePanel

        self.style_panel = StylePanel(config.CAPTION_PRESETS)
        self.style_panel.styleChanged.connect(self._on_style_changed)
        tabs.addTab(self.style_panel, "Style")

        layout.addWidget(tabs)

        return panel

    def _on_style_changed(self, style: dict):
        """Handle caption style changes from the StylePanel"""
        self.current_style = style
        self.status_label.setText(f"Style: {style.get('preset', 'custom')}")

    def create_transcript_tab(self) -> QWidget:
        """Create transcript editor tab"""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Transcript toolbar
        toolbar = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_transcript)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Transcript list (custom widget for editing)
        self.transcript_list = QListWidget()
        self.transcript_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.transcript_list.itemClicked.connect(self.on_transcript_click)
        layout.addWidget(self.transcript_list)

        # Segment info
        info_layout = QHBoxLayout()
        self.segment_info_label = QLabel("Click a segment to play")
        info_layout.addWidget(self.segment_info_label)
        layout.addLayout(info_layout)

        return tab

    def create_clips_tab(self) -> QWidget:
        """Create clips list tab"""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Clip detection controls
        controls = QHBoxLayout()

        detect_btn = QPushButton("🎯 Detect Viral Clips")
        detect_btn.clicked.connect(self.detect_clips)
        controls.addWidget(detect_btn)

        controls.addStretch()

        # Number of clips
        controls.addWidget(QLabel("Clips:"))
        self.num_clips_spin = QComboBox()
        self.num_clips_spin.addItems(["3", "5", "7", "10"])
        self.num_clips_spin.setCurrentText("5")
        controls.addWidget(self.num_clips_spin)

        layout.addLayout(controls)

        # Clips list
        self.clips_list = QListWidget()
        self.clips_list.setSelectionMode(QListWidget.SingleSelection)
        self.clips_list.itemClicked.connect(self.on_clip_clicked)
        layout.addWidget(self.clips_list)

        # Clip actions
        actions = QHBoxLayout()

        preview_btn = QPushButton("▶ Preview")
        preview_btn.clicked.connect(self.preview_clip)
        actions.addWidget(preview_btn)

        edit_btn = QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self.edit_clip)
        actions.addWidget(edit_btn)

        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_selected_clip)
        actions.addWidget(export_btn)

        actions.addStretch()

        layout.addLayout(actions)

        return tab

    def create_bottom_panel(self) -> QWidget:
        """Create bottom status and progress panel"""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        return panel

    def init_components(self):
        """Initialize core components"""

        self.downloader = downloader.VideoDownloader(config.EXPORTS_DIR)
        self.transcriber = transcriber.TranscriptionEngine(config.DEFAULT_WHISPER_MODEL)
        self.clip_detector = clip_detector.ClipDetector(
            min_duration=config.CLIP_DETECTION["min_clip_duration"],
            max_duration=config.CLIP_DETECTION["max_clip_duration"],
            num_clips=config.CLIP_DETECTION["default_num_clips"],
        )
        self.renderer = renderer.VideoRenderer(config.EXPORTS_DIR)

        # Initialize media player
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setVideoOutput(self.video_widget)

            # Connect media player signals
            self.media_player.positionChanged.connect(self.position_changed)
            self.media_player.durationChanged.connect(self.duration_changed)
            self.media_player.playbackStateChanged.connect(self.playback_state_changed)
        except Exception as e:
            print(f"Error initializing media player: {e}")
            # Continue without media player - some functionality will be limited
            self.media_player = None
            self.audio_output = None

        # Try to initialize LLM
        self.init_llm()

    def init_llm(self):
        """Initialize LLM interface"""

        try:
            # Try OpenAI first
            self.llm = llm_interface.LLMInterface("openai")
            if self.llm.is_available():
                self.status_label.setText("LLM: OpenAI available")
                return
        except:
            pass

        try:
            # Try Anthropic
            self.llm = llm_interface.LLMInterface("anthropic")
            if self.llm.is_available():
                self.status_label.setText("LLM: Anthropic available")
                return
        except:
            pass

        try:
            # Try Ollama
            self.llm = llm_interface.LLMInterface("ollama")
            if self.llm.is_available():
                self.status_label.setText("LLM: Ollama available")
                return
        except:
            pass

        self.llm = None
        self.status_label.setText("LLM: Not available (using rule-based detection)")

    # ==================== Slot Implementations ====================

    @Slot()
    def open_video_file(self):
        """Open video file dialog"""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*)",
        )

        if file_path:
            self.source_url = None
            self.youtube_subs_path = None
            self.post_btn.setVisible(False)  # No posting for local files
            self.load_video(file_path)

    @Slot()
    def download_from_url(self):
        """Download video from URL"""

        from ui.dialogs import URLDialog

        dialog = URLDialog(self)
        if dialog.exec():
            url = dialog.get_url()
            self.download_video(url)

    @Slot()
    def download_video(self, url: str):
        """Download video from URL"""

        self.status_label.setText(f"Downloading: {url}")
        self.progress_bar.setRange(0, 0)  # Indeterminate

        try:
            self.source_url = url
            self.youtube_subs_path = None

            video_path, video_info = self.downloader.download(url)
            self.current_video_path = video_path

            # Show Post button only for YouTube videos (not Twitter or local)
            is_youtube = self.downloader.is_youtube_url(url)
            self.post_btn.setVisible(is_youtube)

            # Update UI
            self.video_title_label.setText(video_info.get("title", "Unknown"))
            duration = video_info.get("duration", 0)
            self.video_duration_label.setText(
                f"Duration: {self.format_duration(duration)}"
            )

            # Load video
            self.load_video(str(video_path))

            self.status_label.setText("Download complete")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

        except Exception as e:
            self.show_error(f"Download failed: {str(e)}")

    @Slot()
    def transcribe_video(self):
        """Transcribe current video — tries SRT first, falls back to Whisper"""

        if not self.current_video_path:
            self.show_error("No video loaded")
            return

        language = self._get_selected_language()
        lang_code = language if language else "hi"

        self.status_label.setText("Transcribing...")
        self.progress_bar.setRange(0, 0)

        try:
            srt_used = False

            # --- Option 1: SRT already found by scanning local files ---
            if self.youtube_subs_path and self.youtube_subs_path.exists():
                self.status_label.setText(
                    f"Using found SRT: {self.youtube_subs_path.name}"
                )
                self.current_transcript = self.downloader.parse_srt(
                    self.youtube_subs_path
                )

                if self.current_transcript:
                    srt_used = True
                    print(f"[INFO] Using local SRT: {self.youtube_subs_path}")

            # --- Option 2: Try downloading from YouTube URL ---
            if (
                not srt_used
                and self.source_url
                and self.downloader.is_youtube_url(self.source_url)
            ):
                self.status_label.setText(
                    f"Checking YouTube subtitles ({lang_code})..."
                )

                dl_path = self.downloader.download_subtitles(
                    self.source_url, lang=lang_code
                )

                if dl_path:
                    self.status_label.setText("Parsing YouTube subtitles...")
                    self.current_transcript = self.downloader.parse_srt(dl_path)

                    if self.current_transcript:
                        self.youtube_subs_path = dl_path
                        srt_used = True
                        print(f"[INFO] Using downloaded YouTube subs: {dl_path}")

            # --- Option 3: Fall back to Whisper ---
            if not srt_used:
                print(f"[DEBUG] Transcribing with Whisper, language: {language}")
                self.status_label.setText("Running Whisper transcription...")
                self.current_transcript = self.transcriber.transcribe_video(
                    str(self.current_video_path), language=language
                )

            # Initialize editor with transcript
            self.editor = editor_engine.TranscriptEditor(self.current_transcript)

            # Update UI
            self.populate_transcript_list()
            source_label = "SRT" if srt_used else "Whisper"
            self.status_label.setText(
                f"Transcription complete ({source_label}): "
                f"{len(self.current_transcript)} segments"
            )
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            self.transcript_ready.emit(self.current_transcript)

        except Exception as e:
            self.show_error(f"Transcription failed: {str(e)}")

    @Slot()
    def detect_clips(self):
        """Detect viral clips from transcript, or create single clip for Twitter videos"""

        if not self.current_transcript:
            self.show_error("No transcript available. Please transcribe first.")
            return

        self.status_label.setText("Detecting clips...")
        self.progress_bar.setRange(0, 0)

        try:
            # For Twitter/X videos, create a single clip of the entire video
            if self.source_url and self.downloader.is_twitter_url(self.source_url):
                from core.clip_detector import ClipSegment

                first_seg = self.current_transcript[0]
                last_seg = self.current_transcript[-1]
                self.detected_clips = [
                    ClipSegment(
                        start_time=first_seg["start"],
                        end_time=last_seg["end"],
                        title="Full Video",
                        hook=first_seg["text"][:100],
                        score=1.0,
                        reason="twitter_single_clip",
                        topics=[],
                    )
                ]
                self.post_btn.setVisible(False)  # No posting for Twitter clips
            else:
                # Normal viral clip detection for YouTube/local videos
                num_clips = int(self.num_clips_spin.currentText())
                self.clip_detector.num_clips = num_clips

                llm_provider = (
                    self.llm if self.llm and self.llm.is_available() else None
                )

                self.detected_clips = self.clip_detector.detect_clips(
                    self.current_transcript, use_llm=bool(llm_provider)
                )

            # Update UI
            self.populate_clips_list()
            self.status_label.setText(f"Detected {len(self.detected_clips)} clips")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            self.clips_detected.emit(self.detected_clips)

        except Exception as e:
            self.show_error(f"Clip detection failed: {str(e)}")

    @Slot()
    def export_selected_clip(self):
        """Export currently selected clip"""

        # Get selected clip
        selected_items = self.clips_list.selectedItems()
        if not selected_items:
            # Try to get first clip
            if self.detected_clips:
                clip = self.detected_clips[0]
            else:
                self.show_error("No clip selected")
                return
        else:
            index = self.clips_list.row(selected_items[0])
            if index < len(self.detected_clips):
                clip = self.detected_clips[index]
            else:
                self.show_error("Invalid clip selection")
                return

        # Export
        self.export_clip(clip)

    def export_clip(self, clip: clip_detector.ClipSegment):
        """Export a clip"""

        if not self.current_video_path:
            self.show_error("No video loaded")
            return

        # Get export format
        format_text = self.format_combo.currentText()
        preset = format_text.split()[0].lower()

        # Determine if vertical
        vertical = "9:16" in format_text

        # Generate SRT for subtitles — filter to clip range, offset timestamps to clip start
        srt_path = None
        if self.add_subtitles_check.isChecked():
            clip_segs = [
                s
                for s in self.current_transcript
                if s["end"] > clip.start_time and s["start"] < clip.end_time
            ]
            srt_path = self.transcriber.export_srt(
                clip_segs,
                config.CACHE_DIR / "temp.srt",
                offset=clip.start_time,
            )
            print(
                f"[DEBUG] SRT: {Path(srt_path).stat().st_size if Path(srt_path).exists() else 0} bytes, {len(clip_segs)} segments"
            )

        self.status_label.setText(f"Exporting clip: {clip.title}")

        try:
            output_path = self.renderer.create_clip_with_subtitles(
                str(self.current_video_path),
                srt_path,
                clip.start_time,
                clip.end_time,
                vertical=vertical,
                preset=preset,
            )

            self.status_label.setText(f"Export complete: {output_path.name}")
            self.export_complete.emit(str(output_path))

            QMessageBox.information(
                self, "Export Complete", f"Clip exported to:\n{output_path}"
            )

        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")

    @Slot()
    def toggle_playback(self):
        """Toggle video playback"""

        if not self.media_player:
            self.show_error("Media player not available")
            return

        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    @Slot(int)
    def set_volume(self, value: int):
        """Set media player volume"""

        if self.audio_output:
            self.audio_output.setVolume(value / 100.0)

    @Slot(int)
    def seek_video(self, position: int):
        """Seek video to position"""

        if self.media_player and self.media_player.duration() > 0:
            self.media_player.setPosition(
                position * self.media_player.duration() // 1000
            )

    @Slot(int)
    def position_changed(self, position: int):
        """Handle position change"""

        # Update seek slider
        if self.media_player and self.media_player.duration() > 0:
            self.seek_slider.setValue(position * 1000 // self.media_player.duration())

        # Update time label
        current = QTime(0, 0).addMSecs(position).toString("mm:ss")
        total = (
            QTime(0, 0)
            .addMSecs(self.media_player.duration() if self.media_player else 0)
            .toString("mm:ss")
        )
        self.time_label.setText(f"{current} / {total}")

    @Slot(int)
    def duration_changed(self, duration: int):
        """Handle duration change"""

        if self.media_player:
            self.seek_slider.setRange(0, 1000)

    @Slot(QMediaPlayer.PlaybackState)
    def playback_state_changed(self, state: QMediaPlayer.PlaybackState):
        """Handle playback state change"""

        if state == QMediaPlayer.PlayingState:
            self.play_button.setText("⏸ Pause")
        else:
            self.play_button.setText("▶ Play")

    @Slot(QListWidgetItem)
    def on_transcript_click(self, item: QListWidgetItem):
        """Handle transcript item click"""

        index = self.transcript_list.row(item)
        if index < len(self.current_transcript):
            segment = self.current_transcript[index]
            self.segment_info_label.setText(
                f"Time: {self.format_duration(segment['start'])} - {self.format_duration(segment['end'])}"
            )
            # Seek to position
            if self.media_player:
                self.media_player.setPosition(int(segment["start"] * 1000))

    @Slot(QListWidgetItem)
    def on_clip_clicked(self, item: QListWidgetItem):
        """Handle clip item click"""

        index = self.clips_list.row(item)
        if index < len(self.detected_clips):
            clip = self.detected_clips[index]
            self.segment_info_label.setText(
                f"Clip: {clip.title}\n{self.format_duration(clip.start_time)} - {self.format_duration(clip.end_time)}"
            )

    @Slot()
    def preview_clip(self):
        """Preview selected clip"""

        selected_items = self.clips_list.selectedItems()
        if not selected_items:
            return

        index = self.clips_list.row(selected_items[0])
        if index < len(self.detected_clips):
            clip = self.detected_clips[index]
            # Seek to clip start
            if self.media_player:
                self.media_player.setPosition(int(clip.start_time * 1000))
                self.media_player.play()
            # Will stop at clip end (could add timer)

    @Slot()
    def edit_clip(self):
        """Edit selected clip"""

        selected_items = self.clips_list.selectedItems()
        if not selected_items:
            self.show_error("No clip selected")
            return

        index = self.clips_list.row(selected_items[0])
        if index >= len(self.detected_clips):
            self.show_error("Invalid clip selection")
            return

        clip = self.detected_clips[index]
        max_duration = 0
        if self.current_transcript:
            max_duration = self.current_transcript[-1].get("end", 0)

        from ui.dialogs import EditClipDialog

        clip_data = {
            "title": clip.title,
            "start_time": clip.start_time,
            "end_time": clip.end_time,
            "hook": clip.hook,
            "reason": clip.reason,
        }

        dialog = EditClipDialog(clip_data, max_duration, self)
        if dialog.exec():
            edited = dialog.get_edited_data()

            # Validate timing
            if edited["end_time"] <= edited["start_time"]:
                self.show_error("End time must be greater than start time")
                return

            # Update the clip in detected_clips
            self.detected_clips[index] = clip_detector.ClipSegment(
                start_time=edited["start_time"],
                end_time=edited["end_time"],
                title=edited["title"],
                hook=edited["hook"],
                score=clip.score,
                reason=edited["reason"],
                topics=clip.topics,
            )

            # Refresh UI
            self.populate_clips_list()
            self.clips_list.setCurrentRow(index)
            self.status_label.setText(f"Clip updated: {edited['title'][:40]}")

    @Slot()
    def refresh_transcript(self):
        """Refresh transcript display"""

        if self.current_transcript:
            self.populate_transcript_list()

    def load_video(self, file_path: str):
        """Load video into player"""

        self.current_video_path = Path(file_path)

        # Load into media player
        if self.media_player:
            self.media_player.setSource(
                QUrl.fromLocalFile(str(self.current_video_path))
            )

        # Update UI
        self.video_title_label.setText(self.current_video_path.name)

        # Get video info
        video_info = self.renderer.get_video_info(file_path)
        duration = video_info.get("duration", 0)
        self.video_duration_label.setText(f"Duration: {self.format_duration(duration)}")

        # Scan for existing SRT files next to the video
        self._scan_for_srt_files()

        self.status_label.setText(f"Video loaded: {self.current_video_path.name}")
        self.video_loaded.emit(file_path)

    def _scan_for_srt_files(self):
        """
        Scan for SRT files next to the current video.
        Matches patterns like: videoname.hi.srt, videoname.hi.auto.srt
        Handles yt-dlp sanitization differences between video and srt filenames.
        Stores the best match for the selected transcription language.
        """
        self.youtube_subs_path = None

        if not self.current_video_path:
            return

        video_dir = self.current_video_path.parent
        video_stem = self.current_video_path.stem

        # Find all SRT files in the same directory
        all_srts = list(video_dir.glob("*.srt"))
        if not all_srts:
            return

        # Normalize: replace non-alphanumeric chars with space, collapse spaces, lowercase
        # This handles yt-dlp sanitization differences (e.g. '#' vs ' ')
        def _norm(name):
            result = []
            prev_space = True  # skip leading spaces
            for c in name.lower():
                if c.isalnum():
                    result.append(c)
                    prev_space = False
                elif not prev_space:
                    result.append(" ")
                    prev_space = True
            return "".join(result).strip()

        norm_video = _norm(video_stem)

        matching_srts = []
        for srt in all_srts:
            srt_stem = srt.stem  # e.g. "...hi" or "...hi.auto"
            norm_srt = _norm(srt_stem)

            # Try exact match first, then normalized match
            if srt_stem.startswith(video_stem):
                remainder = srt_stem[len(video_stem) :].strip(".")
            elif norm_srt.startswith(norm_video):
                # Normalized match — extract language from remainder
                remainder = norm_srt[len(norm_video) :].strip()
            else:
                continue

            # Extract language: "hi" from "hi" or "hi auto"
            parts = remainder.split() if remainder else []
            lang = parts[0] if parts else "unknown"
            matching_srts.append({"path": srt, "lang": lang})

        if not matching_srts:
            return

        self._available_srt_files = matching_srts

        selected_lang = self._get_selected_language() or "hi"

        best = None
        for entry in matching_srts:
            if entry["lang"] == selected_lang:
                best = entry
                break
        if not best:
            best = matching_srts[0]

        self.youtube_subs_path = best["path"]

        lang_list = ", ".join(e["lang"] for e in matching_srts)
        self.status_label.setText(
            f"Found SRT: {best['path'].name}  [languages: {lang_list}]"
        )
        print(f"[INFO] Found SRT files: {[e['path'].name for e in matching_srts]}")

    def populate_transcript_list(self):
        """Populate transcript list widget"""

        self.transcript_list.clear()

        for i, segment in enumerate(self.current_transcript):
            text = segment["text"]
            start = self.format_duration(segment["start"])
            item_text = f"[{start}] {text[:100]}{'...' if len(text) > 100 else ''}"

            item = QListWidgetItem(item_text)
            self.transcript_list.addItem(item)

    def populate_clips_list(self):
        """Populate clips list widget"""

        self.clips_list.clear()

        for i, clip in enumerate(self.detected_clips):
            duration = clip.end_time - clip.start_time
            score = int(clip.score * 100)

            item_text = f"#{i + 1} {clip.title[:40]}\n"
            item_text += f"   {self.format_duration(clip.start_time)} - {self.format_duration(clip.end_time)} ({duration:.0f}s) | Score: {score}%"

            item = QListWidgetItem(item_text)
            self.clips_list.addItem(item)

    def format_duration(self, seconds: float) -> str:
        """Format seconds to mm:ss"""

        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _get_selected_language(self) -> Optional[str]:
        """Map language selector to Whisper language code, or None for auto-detect"""

        lang_map = {
            "Hindi (Devanagari)": "hi",
            "English": "en",
            "Urdu": "ur",
            "Bengali": "bn",
            "Tamil": "ta",
            "Telugu": "te",
            "Marathi": "mr",
            "Gujarati": "gu",
            "Kannada": "kn",
            "Malayalam": "ml",
            "Punjabi": "pa",
            "Arabic": "ar",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
        }
        selected = self.language_combo.currentText()
        return lang_map.get(selected, None)

    def show_error(self, message: str):
        """Show error message"""

        self.status_label.setText(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)
        self.error_occurred.emit(message)

    def show_about(self):
        """Show about dialog"""

        QMessageBox.about(
            self,
            "About Video Repurposing Studio",
            "<h3>Video Repurposing Studio</h3>"
            "<p>Local-first AI video repurposing system</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>YouTube URL / Local file input</li>"
            "<li>Whisper transcription</li>"
            "<li>Viral clip detection</li>"
            "<li>Auto format conversion (Reels, Shorts, TikTok)</li>"
            "<li>Subtitle generation</li>"
            "</ul>",
        )

    @Slot()
    def select_logo(self):
        """Open logo selection dialog"""
        from ui.dialogs import LogoUploadWidget
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Logo Settings")
        layout = QVBoxLayout(dialog)

        logo_widget = LogoUploadWidget()
        layout.addWidget(logo_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            self.current_logo_settings = logo_widget.get_settings()
            if self.current_logo_settings.get("logo_path"):
                self.status_label.setText(
                    f"Logo set: {Path(self.current_logo_settings['logo_path']).name}"
                )
            else:
                self.status_label.setText("Logo removed")

    @Slot()
    def post_to_twitter(self):
        """Post selected clip to Twitter/X"""
        from ui.dialogs import PostDialog

        # Get selected clip
        selected_items = self.clips_list.selectedItems()
        clip_title = ""
        if selected_items:
            index = self.clips_list.row(selected_items[0])
            if index < len(self.detected_clips):
                clip_title = self.detected_clips[index].title

        dialog = PostDialog(clip_title, self)
        if dialog.exec():
            data = dialog.get_post_data()
            self.status_label.setText(
                f"Posting to Twitter: {data['tweet_text'][:50]}..."
            )
            # TODO: Implement actual Twitter API posting
            QMessageBox.information(
                self,
                "Twitter/X",
                "Twitter posting will be available after API integration.\n"
                f"Tweet text: {data['tweet_text']}\n"
                f"Hashtags: {data['hashtags']}",
            )


def main():
    """Main entry point"""

    app = QApplication(sys.argv)
    app.setApplicationName("Video Repurposing Studio")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
