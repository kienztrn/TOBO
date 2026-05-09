import os
import sys
import subprocess
import threading
import queue
import time
import json
import urllib.request
import urllib.error
import urllib.parse
import socket
import random
import math
from pathlib import Path
from datetime import timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import winsound
except Exception:
    winsound = None

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
else:
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR

TEMP_DIR = APP_DIR / "temp"
OUTPUT_DIR = APP_DIR / "output"
UPDATES_DIR = APP_DIR / "updates"
CURRENT_VERSION = "1.6.2"
APP_NAME = "TOBO VietSub"
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
UPDATES_DIR.mkdir(exist_ok=True)

ASSETS_DIR = BUNDLE_DIR / "assets"
APP_ICON_PNG = ASSETS_DIR / "app_logo.png"
APP_LOGO_PNG = ASSETS_DIR / "app_logo_128.png"
BACKGROUND_CONFIG_NAME = "background_config.json"
DEFAULT_BACKGROUND_VIDEO_URL = ""

# Apple/AI light palette inspired by the cat logo
BG_COLOR = "#F8F6FF"
BG_2 = "#FFFFFF"
SURFACE = "#FFFFFF"
SURFACE_2 = "#F1ECFF"
CARD = "#FFFFFF"
ACCENT = "#9B72FF"
ACCENT_2 = "#00B8D9"
ACCENT_3 = "#FF8BD8"
TEXT = "#1E1935"
TEXT_MUTED = "#6F6790"
TEXT_DIM = "#9A91B8"
BORDER = "#E3D9FF"
ENTRY_BG = "#FFFFFF"
TEXTBOX_BG = "#FFFFFF"
SUCCESS = "#11A36A"
WARNING = "#D97706"

LANGUAGES = {
    "Tự động nhận diện": None,
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Trung": "zh",
    "Tiếng Nhật": "ja",
    "Tiếng Hàn": "ko",
    "Tiếng Pháp": "fr",
    "Tiếng Đức": "de",
    "Tiếng Tây Ban Nha": "es",
    "Tiếng Thái": "th",
    "Tiếng Indonesia": "id",
}

TRANSLATE_LANGUAGES = {
    "Không dịch": None,
    "Dịch sang Tiếng Việt": "vi",
    "Dịch sang Tiếng Anh": "en",
    "Dịch sang Tiếng Trung": "zh-CN",
    "Dịch sang Tiếng Nhật": "ja",
    "Dịch sang Tiếng Hàn": "ko",
    "Dịch sang Tiếng Pháp": "fr",
    "Dịch sang Tiếng Đức": "de",
    "Dịch sang Tiếng Tây Ban Nha": "es",
    "Dịch sang Tiếng Thái": "th",
    "Dịch sang Tiếng Indonesia": "id",
}

MODEL_SIZES = {
    "Nhanh nhất - tiny": "tiny",
    "Nhanh - base": "base",
    "Cân bằng - small": "small",
    "Chính xác hơn - medium": "medium",
    "Rất chính xác - large-v3": "large-v3",
}

EXPORT_FORMATS = {
    "TXT": "txt",
    "SRT": "srt",
    "TXT + SRT": "both",
}

AUDIO_VIDEO_EXTENSIONS = "*.mp4 *.mkv *.mov *.avi *.webm *.mp3 *.wav *.m4a *.aac *.flac *.ogg"


def format_timestamp(seconds: float) -> str:
    seconds = max(0, float(seconds or 0))
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        seconds += 1
        ms = 0
    td = timedelta(seconds=int(seconds))
    return f"{td}.{ms:03d}"


def format_srt_timestamp(seconds: float) -> str:
    seconds = max(0, float(seconds or 0))
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    if ms >= 1000:
        total += 1
        ms = 0
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def safe_filename(name: str) -> str:
    bad_chars = '<>:"/\\|?*'
    cleaned = "".join("_" if ch in bad_chars else ch for ch in name).strip()
    return cleaned or f"media_{int(time.time())}"


def ffmpeg_path() -> str:
    candidates = [
        APP_DIR / "ffmpeg" / "bin" / "ffmpeg.exe",
        BUNDLE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]
    for local in candidates:
        if local.exists():
            return str(local)
    return "ffmpeg"


def check_ffmpeg() -> bool:
    try:
        subprocess.run(
            [ffmpeg_path(), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def extract_audio(input_file: Path, output_wav: Path, log):
    cmd = [
        ffmpeg_path(),
        "-y",
        "-i", str(input_file),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        str(output_wav),
    ]
    log("Đang fallback: tách audio bằng FFmpeg...")
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg lỗi khi tách audio:\n" + proc.stderr[-2500:])


class NeonButton(tk.Button):
    def __init__(self, master, text, command=None, variant="primary", sound_callback=None, **kwargs):
        self.variant = variant
        self.sound_callback = sound_callback
        self.user_command = command
        palette = {
            "primary": (ACCENT, "#8157F2", "#FFFFFF"),
            "cyan": (ACCENT_2, "#05A5C4", "#FFFFFF"),
            "pink": (ACCENT_3, "#F06CCB", "#FFFFFF"),
            "ghost": ("#F4F0FF", "#EAE2FF", TEXT),
            "dark": ("#FFFFFF", "#F7F4FF", TEXT),
        }
        self.normal_bg, self.hover_bg, self.fg_color = palette.get(variant, palette["primary"])
        super().__init__(
            master,
            text=text,
            command=self._clicked,
            bg=self.normal_bg,
            fg=self.fg_color,
            activebackground=self.hover_bg,
            activeforeground=self.fg_color,
            relief="flat",
            bd=0,
            padx=16,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=self.hover_bg,
            **kwargs,
        )
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)

    def _enter(self, _event=None):
        self.configure(bg=self.hover_bg)

    def _leave(self, _event=None):
        self.configure(bg=self.normal_bg)

    def _press(self, _event=None):
        self.configure(relief="sunken", padx=15, pady=8)

    def _release(self, _event=None):
        self.configure(relief="flat", padx=16, pady=9)

    def _clicked(self):
        if self.sound_callback:
            self.sound_callback()
        if self.user_command:
            self.user_command()


class TOBOVietSubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TOBO VietSub - AI Video Translator")
        self.root.geometry("1120x780")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG_COLOR)
        self.q = queue.Queue()
        self.worker = None
        self.selected_file = tk.StringVar()
        self.language = tk.StringVar(value="Tự động nhận diện")
        self.translate_to = tk.StringVar(value="Không dịch")
        self.model_size = tk.StringVar(value="Cân bằng - small")
        self.device_mode = tk.StringVar(value="Tự động")
        self.export_format = tk.StringVar(value="TXT + SRT")
        self.sound_enabled = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Sẵn sàng")
        self.progress = tk.DoubleVar(value=0)
        self.last_text = ""
        self.last_translation = ""
        self.last_rows = []
        self.last_translated_rows = []
        self._icon_photo = None
        self.logo_image = None
        self.pulse_index = 0
        self.pulse_colors = [ACCENT, "#E5C8FF", ACCENT_2, "#D8F7FF", ACCENT_3]
        self.sparkle_enabled = tk.BooleanVar(value=True)
        self.sparkle_canvas = None
        self.sparkle_items = []
        self.sparkle_tick = 0
        self.header_status_label = None
        self.video_bg_enabled = tk.BooleanVar(value=False)
        self.video_bg_label = None
        self.video_bg_status = None
        self.video_bg_images = []
        self.setup_branding()
        self.build_ui()
        self.root.after(100, self.poll_queue)
        self.root.after(220, self.animate_pulse)
        self.root.after(350, self.setup_sparkle_scene)
        self.root.after(420, self.animate_sparkles)

    def play_click(self):
        if not self.sound_enabled.get():
            return
        try:
            if winsound:
                winsound.MessageBeep(winsound.MB_OK)
            else:
                self.root.bell()
        except Exception:
            pass

    def setup_branding(self):
        try:
            if APP_ICON_PNG.exists():
                self._icon_photo = tk.PhotoImage(file=str(APP_ICON_PNG))
                self.root.iconphoto(True, self._icon_photo)
        except Exception:
            pass

        try:
            from PIL import Image, ImageTk
            if APP_LOGO_PNG.exists():
                logo = Image.open(APP_LOGO_PNG).convert("RGBA")
            elif APP_ICON_PNG.exists():
                logo = Image.open(APP_ICON_PNG).convert("RGBA")
            else:
                logo = None
            if logo:
                logo.thumbnail((82, 82))
                self.logo_image = ImageTk.PhotoImage(logo)
        except Exception:
            try:
                if APP_ICON_PNG.exists():
                    self.logo_image = tk.PhotoImage(file=str(APP_ICON_PNG))
            except Exception:
                self.logo_image = None

    def build_ui(self):
        self.setup_styles()

        shell = tk.Frame(self.root, bg=BG_COLOR)
        shell.pack(fill="both", expand=True)

        self.header = tk.Frame(shell, bg=BG_COLOR)
        self.header.pack(fill="x", padx=18, pady=(16, 10))

        brand = tk.Frame(self.header, bg=BG_COLOR)
        brand.pack(side="left", fill="x", expand=True)

        logo_box = tk.Frame(brand, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        logo_box.pack(side="left", padx=(0, 14))
        if self.logo_image:
            tk.Label(logo_box, image=self.logo_image, bg=SURFACE, bd=0).pack(padx=8, pady=8)
        else:
            tk.Label(logo_box, text="TO", bg=SURFACE, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(padx=18, pady=18)

        title_wrap = tk.Frame(brand, bg=BG_COLOR)
        title_wrap.pack(side="left", fill="x", expand=True)

        title_row = tk.Frame(title_wrap, bg=BG_COLOR)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="TOBO VietSub", bg=BG_COLOR, fg=TEXT, font=("Segoe UI Variable Display", 28, "bold")).pack(side="left")
        self.pulse_dot = tk.Label(title_row, text="  ●", bg=BG_COLOR, fg=ACCENT_2, font=("Segoe UI", 20, "bold"))
        self.pulse_dot.pack(side="left")

        tk.Label(
            title_wrap,
            text="AI subtitle studio • clean translation • TXT/SRT export • in-place updater",
            bg=BG_COLOR,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        header_actions = tk.Frame(self.header, bg=BG_COLOR)
        header_actions.pack(side="right", anchor="ne")

        control_card = tk.Frame(
            header_actions,
            bg=SURFACE,
            width=560,
            height=168,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        control_card.pack(anchor="e")
        control_card.pack_propagate(False)

        top_strip = tk.Frame(control_card, bg="#FFFFFF", height=32)
        top_strip.pack(fill="x", side="top")
        top_strip.pack_propagate(False)
        tk.Label(
            top_strip,
            text="TOBO AI CONTROL",
            bg="#FFFFFF",
            fg=ACCENT,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=14)
        tk.Label(
            top_strip,
            text=f"v{CURRENT_VERSION}",
            bg="#FFFFFF",
            fg=TEXT_DIM,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=14)

        card_body = tk.Frame(control_card, bg=SURFACE)
        card_body.pack(fill="both", expand=True, padx=14, pady=12)

        aura_panel = tk.Frame(card_body, bg="#FBFAFF", width=304, height=112, highlightthickness=1, highlightbackground="#ECE4FF")
        aura_panel.pack(side="left", fill="y")
        aura_panel.pack_propagate(False)

        self.sparkle_canvas = tk.Canvas(
            aura_panel,
            width=304,
            height=112,
            bg="#FBFAFF",
            highlightthickness=0,
            bd=0,
        )
        self.sparkle_canvas.pack(fill="both", expand=True)

        badge = tk.Label(
            aura_panel,
            text="APPLE / AI LIGHT MODE",
            bg="#FFFFFF",
            fg=ACCENT,
            font=("Segoe UI", 8, "bold"),
            padx=9,
            pady=3,
        )
        badge.place(x=12, y=10)

        self.header_status_label = tk.Label(
            aura_panel,
            text="Soft sparkle active",
            bg="#FFFFFF",
            fg=TEXT,
            font=("Segoe UI", 8, "bold"),
            padx=9,
            pady=3,
        )
        self.header_status_label.place(x=12, rely=1, y=-12, anchor="sw")

        control_panel = tk.Frame(card_body, bg=SURFACE, width=220)
        control_panel.pack(side="left", fill="both", expand=True, padx=(16, 0))

        tk.Label(
            control_panel,
            text="Update Center",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI Variable Display", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            control_panel,
            text="Cập nhật tại chỗ, giữ nguyên thư viện và dữ liệu đã cài.",
            bg=SURFACE,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=218,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 10))

        action_row = tk.Frame(control_panel, bg=SURFACE)
        action_row.pack(fill="x")
        NeonButton(action_row, "↻ Cập nhật", self.check_update, variant="primary", sound_callback=self.play_click).pack(side="left")
        NeonButton(action_row, "📁 Updates", self.open_updates_folder, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(8, 0))

        toggle_row = tk.Frame(control_panel, bg=SURFACE)
        toggle_row.pack(fill="x", pady=(12, 0))
        tk.Checkbutton(
            toggle_row,
            text="Sparkle FX",
            variable=self.sparkle_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor="#F2ECFF",
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="left")
        tk.Checkbutton(
            toggle_row,
            text="Âm click",
            variable=self.sound_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor="#F2ECFF",
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="left", padx=(14, 0))

        info_row = tk.Frame(control_panel, bg=SURFACE)
        info_row.pack(fill="x", pady=(12, 0))
        tk.Label(
            info_row,
            text="In-place update ready",
            bg=SURFACE,
            fg=SUCCESS,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info_row,
            text="Không xóa .venv • không tải lại thư viện",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(3, 0))

        main = tk.Frame(shell, bg=BG_COLOR)
        main.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        top = tk.Frame(main, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        top.pack(fill="x", pady=(0, 12))

        file_row = tk.Frame(top, bg=SURFACE)
        file_row.pack(fill="x", padx=16, pady=(16, 12))
        NeonButton(file_row, "＋ Chọn video/audio", self.pick_file, variant="cyan", sound_callback=self.play_click).pack(side="left")
        self.file_entry = tk.Entry(
            file_row,
            textvariable=self.selected_file,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Consolas", 10),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT_2,
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(12, 0), ipady=10)

        options = tk.Frame(top, bg=SURFACE)
        options.pack(fill="x", padx=16, pady=(0, 14))
        for col in range(5):
            options.columnconfigure(col, weight=1)

        self.add_combo(options, "Ngôn ngữ gốc", self.language, list(LANGUAGES.keys()), 0)
        self.add_combo(options, "Dịch", self.translate_to, list(TRANSLATE_LANGUAGES.keys()), 1)
        self.add_combo(options, "Model AI", self.model_size, list(MODEL_SIZES.keys()), 2)
        self.add_combo(options, "Thiết bị", self.device_mode, ["Tự động", "CPU", "GPU NVIDIA"], 3)
        self.add_combo(options, "Xuất file", self.export_format, list(EXPORT_FORMATS.keys()), 4)

        btns = tk.Frame(top, bg=SURFACE)
        btns.pack(fill="x", padx=16, pady=(0, 16))
        self.start_btn = NeonButton(btns, "▶ Bắt đầu xử lý", self.start, variant="primary", sound_callback=self.play_click)
        self.start_btn.pack(side="left")
        NeonButton(btns, "💾 Lưu TXT", self.save_text, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, "🎬 Xuất SRT", self.save_srt_manual, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, "📁 Output", self.open_output, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, "🧹 Xóa", self.clear_text, variant="dark", sound_callback=self.play_click).pack(side="left", padx=(10, 0))

        tk.Checkbutton(
            btns,
            text="Sparkle FX",
            variable=self.sparkle_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor="#F2ECFF",
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="right", padx=(0, 14))

        tk.Checkbutton(
            btns,
            text="Âm click",
            variable=self.sound_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor="#F2ECFF",
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="right")

        status_card = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        status_card.pack(fill="x", pady=(0, 12))
        tk.Label(status_card, text="SYSTEM STATUS", bg=CARD, fg=TEXT_DIM, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(status_card, variable=self.progress, maximum=100, mode="determinate")
        self.progress_bar.pack(fill="x", padx=14, pady=(8, 4))
        self.status_label = tk.Label(status_card, textvariable=self.status, bg=CARD, fg=TEXT_MUTED, font=("Segoe UI", 10))
        self.status_label.pack(anchor="w", padx=14, pady=(2, 10))

        panes = ttk.PanedWindow(main, orient="horizontal")
        panes.pack(fill="both", expand=True)

        left = self.make_text_card(panes, "Văn bản gốc", "Có timestamp để kiểm tra transcript")
        right = self.make_text_card(panes, "Bản dịch", "Chỉ hiện văn bản dịch sạch, không kèm giây")
        panes.add(left, weight=1)
        panes.add(right, weight=1)

        self.text_original = self.make_textbox(left)
        self.text_original.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.text_translated = self.make_textbox(right)
        self.text_translated.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG, foreground=TEXT, arrowcolor=ACCENT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], foreground=[("readonly", TEXT)])
        style.configure("Horizontal.TProgressbar", thickness=12, troughcolor="#EFE8FF", background=ACCENT, bordercolor="#EFE8FF", lightcolor=ACCENT, darkcolor=ACCENT)
        style.configure("TPanedwindow", background=BG_COLOR)

    def make_text_card(self, panes, title, subtitle):
        frame = tk.Frame(panes, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        head = tk.Frame(frame, bg=SURFACE)
        head.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(head, text=title, bg=SURFACE, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(head, text=subtitle, bg=SURFACE, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        return frame

    def make_textbox(self, parent):
        return tk.Text(
            parent,
            wrap="word",
            bg=TEXTBOX_BG,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Consolas", 10),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT_2,
            padx=12,
            pady=12,
        )

    def add_combo(self, parent, label, variable, values, col):
        frame = tk.Frame(parent, bg=SURFACE)
        frame.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 10, 0))
        tk.Label(frame, text=label, bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        combo = ttk.Combobox(frame, textvariable=variable, values=values, state="readonly")
        combo.pack(fill="x", pady=(6, 0), ipady=4)

    def animate_pulse(self):
        try:
            color = self.pulse_colors[self.pulse_index % len(self.pulse_colors)]
            self.pulse_dot.configure(fg=color)
            self.status_label.configure(fg=color if self.worker and self.worker.is_alive() else TEXT_MUTED)
            self.pulse_index += 1
        except Exception:
            pass
        self.root.after(420, self.animate_pulse)

    def setup_sparkle_scene(self):
        if not self.sparkle_canvas:
            return
        c = self.sparkle_canvas
        c.delete("all")
        w, h = 304, 112
        c.create_rectangle(0, 0, w, h, fill="#FBFAFF", outline="")
        c.create_oval(-50, -38, 132, 118, fill="#F0E8FF", outline="")
        c.create_oval(148, -22, 330, 94, fill="#E9FAFF", outline="")
        c.create_oval(172, 44, 342, 156, fill="#FFEAF8", outline="")
        c.create_arc(36, 30, 270, 158, start=20, extent=142, style="arc", outline="#E5D8FF", width=2)
        c.create_text(152, 43, text="TOBO", fill=TEXT, font=("Segoe UI Variable Display", 21, "bold"))
        c.create_text(152, 66, text="clean subtitle AI workspace", fill=TEXT_MUTED, font=("Segoe UI", 8))
        self.sparkle_items = []
        palette = [ACCENT, ACCENT_2, ACCENT_3, "#FFFFFF"]
        for _ in range(24):
            x = random.randint(18, w - 18)
            y = random.randint(18, h - 18)
            base = random.choice([1.2, 1.7, 2.2, 2.8])
            color = random.choice(palette)
            item = c.create_oval(x - base, y - base, x + base, y + base, fill=color, outline=color)
            self.sparkle_items.append({"item": item, "x": x, "y": y, "base": base, "phase": random.random() * math.tau})
        self.sparkle_orbit = c.create_text(238, 88, text="✦ soft glow", fill=ACCENT, font=("Segoe UI", 9, "bold"))

    def animate_sparkles(self):
        try:
            if self.sparkle_canvas and self.sparkle_items and self.sparkle_enabled.get():
                self.sparkle_tick += 1
                palette = [ACCENT, ACCENT_2, ACCENT_3, "#FFFFFF"]
                for idx, sp in enumerate(self.sparkle_items):
                    t = self.sparkle_tick / 7.0 + sp["phase"]
                    twinkle = 0.55 + 0.45 * math.sin(t)
                    size = sp["base"] * (0.8 + 0.7 * twinkle)
                    dx = math.sin(t * 0.4) * 0.8
                    dy = math.cos(t * 0.5) * 0.8
                    x = sp["x"] + dx
                    y = sp["y"] + dy
                    self.sparkle_canvas.coords(sp["item"], x - size, y - size, x + size, y + size)
                    color = palette[(idx + int(self.sparkle_tick / 5)) % len(palette)] if twinkle > 0.76 else "#D8CFFF"
                    self.sparkle_canvas.itemconfig(sp["item"], fill=color, outline=color)
                if self.header_status_label:
                    label = "Soft sparkle active" if self.sparkle_tick % 10 < 5 else "Logo aura synced"
                    self.header_status_label.configure(text=label)
                if hasattr(self, "sparkle_orbit"):
                    ox = 238 + math.sin(self.sparkle_tick / 8.0) * 5
                    oy = 88 + math.cos(self.sparkle_tick / 9.0) * 2
                    self.sparkle_canvas.coords(self.sparkle_orbit, ox, oy)
                    self.sparkle_canvas.itemconfig(self.sparkle_orbit, fill=palette[int(self.sparkle_tick / 6) % len(palette)])
            elif self.sparkle_canvas and self.header_status_label:
                self.header_status_label.configure(text="Sparkle FX paused")
        except Exception:
            pass
        self.root.after(140, self.animate_sparkles)

    def version_tuple(self, value: str):
        parts = []
        for chunk in str(value or "0").replace("-", ".").split("."):
            num = "".join(ch for ch in chunk if ch.isdigit())
            parts.append(int(num or 0))
        return tuple(parts or [0])

    def default_update_config_text(self) -> str:
        return json.dumps(
            {
                "manifest_url": "https://raw.githubusercontent.com/kienztrn/TOBO/main/update_manifest.json",
                "note": "Link manifest JSON cho nut cap nhat TOBO VietSub.",
                "example_manifest": {
                    "version": CURRENT_VERSION,
                    "url": "https://github.com/kienztrn/TOBO/releases/latest/download/TOBO_VietSub_Portable.zip",
                    "notes": "Sua loi va toi uu app."
                }
            },
            ensure_ascii=False,
            indent=2,
        )

    def get_update_config_path(self) -> Path:
        local = APP_DIR / "update_config.json"
        bundled = BUNDLE_DIR / "update_config.json"
        if local.exists():
            return local
        try:
            if bundled.exists():
                local.write_text(bundled.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                local.write_text(self.default_update_config_text(), encoding="utf-8")
            return local
        except Exception:
            return bundled if bundled.exists() else local

    def load_update_config(self) -> dict:
        path = self.get_update_config_path()
        if not path.exists():
            return {"manifest_url": ""}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            raise RuntimeError(f"File update_config.json bị lỗi JSON: {e}")

    def is_placeholder_url(self, url: str) -> bool:
        lower = (url or "").strip().lower()
        placeholders = ["your-domain.com", "example.com", "your-site", "paste-link", "link-that-cua-ban", "your-link"]
        return any(item in lower for item in placeholders)

    def explain_url_error(self, err: Exception, purpose: str) -> str:
        config_path = self.get_update_config_path()
        if isinstance(err, urllib.error.HTTPError):
            if err.code == 404:
                return f"{purpose} lỗi 404: link update không tồn tại hoặc chưa upload file.\n\nFile cần sửa: {config_path}"
            return f"{purpose} lỗi HTTP {err.code}: {err.reason}\n\nFile cần sửa: {config_path}"
        if isinstance(err, urllib.error.URLError):
            reason = getattr(err, "reason", err)
            reason_text = str(reason)
            if isinstance(reason, socket.gaierror) or "getaddrinfo failed" in reason_text.lower():
                return f"{purpose} lỗi DNS: domain update không tồn tại/sai link/mất mạng.\n\nFile cần sửa: {config_path}"
            return f"{purpose} lỗi mạng: {reason_text}\n\nFile cần sửa: {config_path}"
        if isinstance(err, json.JSONDecodeError):
            return f"{purpose} lỗi: manifest không phải JSON hợp lệ."
        return f"{purpose} lỗi: {err}"

    def check_update(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Đang chạy", "App đang xử lý file rồi, để nó xong đã.")
            return
        self.status.set("Đang kiểm tra cập nhật...")
        threading.Thread(target=self.check_update_worker, daemon=True).start()

    def check_update_worker(self):
        try:
            cfg = self.load_update_config()
            manifest_url = (cfg.get("manifest_url") or "").strip()
            config_path = self.get_update_config_path()
            if not manifest_url:
                self.q.put(("update_info", f"Chưa cấu hình link cập nhật.\n\nFile cần sửa: {config_path}"))
                return
            if self.is_placeholder_url(manifest_url):
                self.q.put(("update_info", f"manifest_url đang là link mẫu. Thay bằng link JSON thật.\n\nLink hiện tại: {manifest_url}"))
                return
            if not (manifest_url.startswith("http://") or manifest_url.startswith("https://") or manifest_url.startswith("file://")):
                self.q.put(("update_info", f"manifest_url không hợp lệ: {manifest_url}"))
                return
            try:
                req = urllib.request.Request(manifest_url, headers={"User-Agent": f"{APP_NAME}/{CURRENT_VERSION}"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    manifest = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                self.q.put(("update_info", self.explain_url_error(e, "Kiểm tra cập nhật")))
                return
            latest_version = str(manifest.get("version", "")).strip()
            download_url = str(manifest.get("url") or manifest.get("zip_url") or manifest.get("exe_url") or "").strip()
            notes = str(manifest.get("notes", "")).strip()
            if not latest_version or not download_url:
                raise RuntimeError("Manifest update thiếu version hoặc url/zip_url/exe_url.")
            if self.version_tuple(latest_version) <= self.version_tuple(CURRENT_VERSION):
                self.q.put(("update_info", f"Bạn đang dùng bản mới nhất rồi: v{CURRENT_VERSION}."))
                return
            self.q.put(("update_available", {"version": latest_version, "url": download_url, "notes": notes}))
        except Exception as e:
            self.q.put(("update_info", f"Kiểm tra cập nhật lỗi: {e}"))

    def download_update(self, info: dict):
        threading.Thread(target=self.download_update_worker, args=(info,), daemon=True).start()

    def download_update_worker(self, info: dict):
        try:
            version = safe_filename(info.get("version", "new"))
            url = (info.get("url") or "").strip()
            if not url:
                raise RuntimeError("Thiếu link tải bản cập nhật.")
            suffix = ".exe" if url.lower().split("?")[0].endswith(".exe") else ".zip"
            target = UPDATES_DIR / f"TOBO_VietSub_update_{version}{suffix}"
            self.q.put(("status", f"Đang tải bản cập nhật v{version}..."))
            self.q.put(("progress", 5))
            try:
                req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{CURRENT_VERSION}"})
                with urllib.request.urlopen(req, timeout=60) as resp, open(target, "wb") as f:
                    total = int(resp.headers.get("Content-Length", "0") or 0)
                    downloaded = 0
                    while True:
                        chunk = resp.read(1024 * 256)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            self.q.put(("progress", min(95, int(downloaded / total * 100))))
            except Exception as e:
                if target.exists():
                    try:
                        target.unlink()
                    except Exception:
                        pass
                self.q.put(("update_info", self.explain_url_error(e, "Tải cập nhật")))
                return
            self.q.put(("progress", 100))
            if suffix == ".zip":
                self.q.put(("update_ready_to_apply", str(target)))
            else:
                self.q.put(("update_downloaded", str(target)))
        except Exception as e:
            self.q.put(("update_info", f"Tải cập nhật lỗi: {e}"))

    def find_update_python(self) -> str | None:
        candidates = []
        if not getattr(sys, "frozen", False):
            candidates.append(Path(sys.executable))
        candidates.extend([
            APP_DIR / ".venv" / "Scripts" / "python.exe",
            APP_DIR / "venv" / "Scripts" / "python.exe",
        ])
        for candidate in candidates:
            try:
                if candidate and Path(candidate).exists():
                    return str(candidate)
            except Exception:
                pass
        return "py"

    def apply_update_zip(self, zip_path: str):
        helper = APP_DIR / "tobo_update_helper.py"
        bundled_helper = BUNDLE_DIR / "tobo_update_helper.py"
        if not helper.exists() and bundled_helper.exists():
            try:
                helper.write_text(bundled_helper.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass
        if not helper.exists():
            messagebox.showerror("Cập nhật", "Thiếu file tobo_update_helper.py nên chưa thể tự cài cập nhật.")
            return

        py_cmd = self.find_update_python()
        if not py_cmd:
            messagebox.showinfo(
                "Cập nhật",
                "Đã tải bản cập nhật nhưng không tìm thấy Python để tự áp dụng.\n"
                "Mở thư mục updates rồi giải nén thủ công."
            )
            try:
                os.startfile(str(UPDATES_DIR))
            except Exception:
                pass
            return

        try:
            args = [py_cmd, str(helper), str(zip_path), str(APP_DIR)]
            if os.name == "nt":
                subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(args)
            messagebox.showinfo(
                "Cập nhật",
                "App sẽ tự cập nhật trong cửa sổ mới rồi mở lại.\n"
                "Đừng xóa .venv, thư viện sẽ được giữ nguyên."
            )
            self.root.after(500, self.root.destroy)
        except Exception as e:
            messagebox.showerror("Cập nhật", f"Không chạy được trình cập nhật tự động:\n{e}")

    def default_background_config_text(self) -> str:
        return json.dumps(
            {
                "enabled": True,
                "video_url": DEFAULT_BACKGROUND_VIDEO_URL,
                "cache_file": "assets/background_cloudfront.mp4",
                "max_frames": 90,
                "width": 360,
                "height": 128,
                "fps": 12,
                "note": "TOBO VietSub se tu tai MP4 nay ve cache tren may cua ban de lam nen dong nhe."
            },
            ensure_ascii=False,
            indent=2,
        )

    def get_background_config_path(self) -> Path:
        local = APP_DIR / BACKGROUND_CONFIG_NAME
        bundled = BUNDLE_DIR / BACKGROUND_CONFIG_NAME
        if local.exists():
            return local
        try:
            if bundled.exists():
                local.write_text(bundled.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                local.write_text(self.default_background_config_text(), encoding="utf-8")
            return local
        except Exception:
            return bundled if bundled.exists() else local

    def load_background_config(self) -> dict:
        path = self.get_background_config_path()
        if not path.exists():
            return json.loads(self.default_background_config_text())
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return json.loads(self.default_background_config_text())
            return data
        except Exception:
            return json.loads(self.default_background_config_text())

    def start_video_background(self):
        return

    def resolve_background_video_file(self, cfg: dict) -> Path | None:
        cache_name = str(cfg.get("cache_file") or "assets/background_cloudfront.mp4").replace("\\", "/").strip("/")
        local_cache = APP_DIR / cache_name
        bundled_cache = BUNDLE_DIR / cache_name
        if local_cache.exists() and local_cache.stat().st_size > 0:
            return local_cache
        if bundled_cache.exists() and bundled_cache.stat().st_size > 0:
            return bundled_cache

        url = str(cfg.get("video_url") or DEFAULT_BACKGROUND_VIDEO_URL).strip()
        if not url:
            return None
        local_cache.parent.mkdir(parents=True, exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{CURRENT_VERSION}"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(local_cache, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 512)
                    if not chunk:
                        break
                    f.write(chunk)
            if local_cache.exists() and local_cache.stat().st_size > 0:
                return local_cache
        except Exception as e:
            self.q.put(("bg_status", f"Không tải được nền video: {e}"))
            return None
        return None

    def video_background_worker(self):
        try:
            cfg = self.load_background_config()
            if not cfg.get("enabled", True):
                self.q.put(("bg_status", "Nền video đang tắt trong background_config.json"))
                return
            width = int(cfg.get("width") or self.video_bg_size[0])
            height = int(cfg.get("height") or self.video_bg_size[1])
            self.video_bg_size = (max(180, width), max(80, height))
            fps = int(cfg.get("fps") or 12)
            self.video_bg_delay_ms = max(33, int(1000 / max(1, fps)))
            max_frames = max(12, min(180, int(cfg.get("max_frames") or 90)))

            video_file = self.resolve_background_video_file(cfg)
            if not video_file:
                self.q.put(("bg_status", "Không có file nền video. Kiểm tra background_config.json"))
                return

            try:
                import av
                from PIL import Image, ImageEnhance
            except Exception as e:
                self.q.put(("bg_status", f"Thiếu thư viện nền video: {e}"))
                return

            frames = []
            container = av.open(str(video_file))
            stream = container.streams.video[0]
            step = max(1, int((float(stream.average_rate or 24) / max(1, fps))))
            for i, frame in enumerate(container.decode(stream)):
                if i % step != 0:
                    continue
                img = frame.to_image().convert("RGB")
                img = img.resize(self.video_bg_size, Image.LANCZOS)
                img = ImageEnhance.Brightness(img).enhance(0.52)
                img = ImageEnhance.Contrast(img).enhance(1.25)
                # phủ nhẹ màu neon để hợp UI dark/future
                overlay = Image.new("RGB", img.size, (8, 11, 24))
                img = Image.blend(img, overlay, 0.22)
                frames.append(img)
                if len(frames) >= max_frames:
                    break
            try:
                container.close()
            except Exception:
                pass

            if frames:
                self.q.put(("bg_frames", frames))
            else:
                self.q.put(("bg_status", "Không đọc được frame nào từ MP4 nền."))
        except Exception as e:
            self.q.put(("bg_status", f"Nền video lỗi: {e}"))

    def animate_video_background(self):
        try:
            if self.video_bg_enabled.get() and self.video_bg_images and self.video_bg_label:
                img = self.video_bg_images[self.video_bg_index % len(self.video_bg_images)]
                self.video_bg_label.configure(image=img, text="")
                self.video_bg_index += 1
        except Exception:
            pass
        self.root.after(self.video_bg_delay_ms, self.animate_video_background)

    def pick_file(self):
        path = filedialog.askopenfilename(
            title="Chọn video/audio",
            filetypes=[("Media files", AUDIO_VIDEO_EXTENSIONS), ("All files", "*.*")],
        )
        if path:
            self.selected_file.set(path)

    def log(self, msg):
        self.q.put(("status", msg))

    def start(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Đang chạy", "App đang xử lý file hiện tại.")
            return
        file_path = self.selected_file.get().strip()
        if not file_path or not Path(file_path).exists():
            messagebox.showerror("Thiếu file", "Bạn hãy chọn video/audio trước.")
            return
        settings = {
            "model_name": MODEL_SIZES[self.model_size.get()],
            "device_choice": self.device_mode.get(),
            "source_lang": LANGUAGES[self.language.get()],
            "target_lang": TRANSLATE_LANGUAGES[self.translate_to.get()],
            "export_format": EXPORT_FORMATS[self.export_format.get()],
        }
        self.start_btn.config(state="disabled")
        self.progress.set(3)
        self.status.set("Đang chuẩn bị...")
        self.text_original.delete("1.0", "end")
        self.text_translated.delete("1.0", "end")
        self.last_text = ""
        self.last_translation = ""
        self.last_rows = []
        self.last_translated_rows = []
        self.worker = threading.Thread(target=self.process_file, args=(Path(file_path), settings), daemon=True)
        self.worker.start()

    def create_model(self, model_name: str, device_choice: str):
        from faster_whisper import WhisperModel
        if device_choice == "GPU NVIDIA":
            try:
                return WhisperModel(model_name, device="cuda", compute_type="float16")
            except Exception as e:
                self.log(f"GPU lỗi hoặc chưa đủ CUDA, chuyển sang CPU. Chi tiết: {e}")
                return WhisperModel(model_name, device="cpu", compute_type="int8")
        if device_choice == "CPU":
            return WhisperModel(model_name, device="cpu", compute_type="int8")
        try:
            return WhisperModel(model_name, device="auto", compute_type="auto")
        except Exception as e:
            self.log(f"Tự động chọn thiết bị lỗi, chuyển sang CPU. Chi tiết: {e}")
            return WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe_source(self, model, media_path: Path, lang: str | None):
        segments, info = model.transcribe(str(media_path), language=lang, beam_size=5, vad_filter=True, word_timestamps=False)
        duration = float(getattr(info, "duration", 0) or 0)
        detected_language = getattr(info, "language", None)
        self.log(f"Đang nhận diện giọng nói. Ngôn ngữ phát hiện: {detected_language}" if detected_language else "Đang nhận diện giọng nói...")
        rows = []
        pending_lines = []
        for count, seg in enumerate(segments, start=1):
            text = (seg.text or "").strip()
            if not text:
                continue
            row = {"start": float(seg.start or 0), "end": float(seg.end or 0), "text": text}
            rows.append(row)
            pending_lines.append(self.format_segment_line(row, text))
            if len(pending_lines) >= 5:
                self.q.put(("append_original", "\n".join(pending_lines) + "\n"))
                pending_lines = []
            pct = 25 + min(60, int((row["end"] / duration) * 60)) if duration > 0 else min(85, 25 + count)
            if count % 3 == 0:
                self.q.put(("progress", pct))
        if pending_lines:
            self.q.put(("append_original", "\n".join(pending_lines) + "\n"))
        return rows

    def process_file(self, input_file: Path, settings: dict):
        audio_path = None
        try:
            self.q.put(("progress", 8))
            self.log("Đang tải/khởi động AI model. Lần đầu có thể lâu vì phải tải model...")
            model = self.create_model(settings["model_name"], settings["device_choice"])
            rows = None
            direct_error = None
            try:
                self.q.put(("progress", 18))
                self.log("Đang đọc trực tiếp video/audio...")
                rows = self.transcribe_source(model, input_file, settings["source_lang"])
            except Exception as e:
                direct_error = e
                self.q.put(("clear_original", None))
                self.log("Đọc trực tiếp lỗi, thử fallback FFmpeg...")
            if rows is None:
                if not check_ffmpeg():
                    raise RuntimeError("Không đọc trực tiếp được file này và máy chưa có FFmpeg để fallback.\n\n" f"Lỗi đọc trực tiếp:\n{direct_error}\n\nCài FFmpeg: winget install Gyan.FFmpeg")
                audio_path = TEMP_DIR / f"{safe_filename(input_file.stem)}_{int(time.time())}.wav"
                extract_audio(input_file, audio_path, self.log)
                self.q.put(("progress", 22))
                rows = self.transcribe_source(model, audio_path, settings["source_lang"])

            self.last_rows = rows
            original_text = "\n".join(self.format_segment_line(row, row["text"]) for row in rows)
            self.last_text = original_text
            safe_stem = safe_filename(input_file.stem)
            export_format = settings["export_format"]
            written_files = []

            if export_format in ("txt", "both"):
                out_txt = OUTPUT_DIR / f"{safe_stem}_transcript.txt"
                out_txt.write_text(original_text, encoding="utf-8")
                written_files.append(out_txt.name)

            if export_format in ("srt", "both"):
                out_srt = OUTPUT_DIR / f"{safe_stem}_transcript.srt"
                out_srt.write_text(self.rows_to_srt(rows), encoding="utf-8-sig")
                written_files.append(out_srt.name)

            self.q.put(("progress", 88))
            self.log("Đã xuất: " + ", ".join(written_files) if written_files else "Đã nhận diện xong.")

            target_lang = settings["target_lang"]
            if target_lang:
                self.log("Đang dịch văn bản. Ô dịch chỉ hiện text sạch, không kèm timestamp...")
                translated_rows = self.translate_rows(rows, target_lang)
                self.last_translated_rows = translated_rows
                display_translation = "\n".join(row["text"] for row in translated_rows if row.get("text"))
                self.last_translation = display_translation
                self.q.put(("set_translation", display_translation))

                if export_format in ("txt", "both"):
                    trans_txt = OUTPUT_DIR / f"{safe_stem}_translated_{target_lang.replace('-', '_')}.txt"
                    trans_txt.write_text(display_translation, encoding="utf-8")
                    written_files.append(trans_txt.name)
                if export_format in ("srt", "both"):
                    trans_srt = OUTPUT_DIR / f"{safe_stem}_translated_{target_lang.replace('-', '_')}.srt"
                    trans_srt.write_text(self.rows_to_srt(translated_rows), encoding="utf-8-sig")
                    written_files.append(trans_srt.name)

            self.q.put(("progress", 100))
            done_msg = "Hoàn tất. File nằm trong thư mục output."
            if written_files:
                done_msg += "\n\nĐã xuất:\n- " + "\n- ".join(written_files)
            self.q.put(("done", done_msg))
        except Exception as e:
            self.q.put(("error", str(e)))
        finally:
            if audio_path:
                try:
                    audio_path.unlink(missing_ok=True)
                except Exception:
                    pass

    def format_segment_line(self, row: dict, text: str) -> str:
        return f"[{format_timestamp(row['start'])} → {format_timestamp(row['end'])}] {text.strip()}"

    def rows_to_srt(self, rows: list[dict]) -> str:
        blocks = []
        for idx, row in enumerate(rows, start=1):
            text = (row.get("text") or "").strip()
            if not text:
                continue
            blocks.append(f"{idx}\n{format_srt_timestamp(row.get('start', 0))} --> {format_srt_timestamp(row.get('end', 0))}\n{text}")
        return "\n\n".join(blocks) + ("\n" if blocks else "")

    def translate_rows(self, rows: list[dict], target_lang: str) -> list[dict]:
        try:
            from deep_translator import GoogleTranslator
        except Exception:
            raise RuntimeError("Chưa có thư viện dịch. Hãy chạy install_windows.bat để cài deep-translator.")
        if not rows:
            return []
        translator = GoogleTranslator(source="auto", target=target_lang)
        translated_texts = [""] * len(rows)
        chunks = []
        current = []
        current_len = 0
        max_chars = 3000
        for idx, row in enumerate(rows):
            text = row["text"].strip()
            projected = current_len + len(text) + 1
            if current and projected > max_chars:
                chunks.append(current)
                current = []
                current_len = 0
            current.append((idx, text))
            current_len += len(text) + 1
        if current:
            chunks.append(current)
        for i, chunk in enumerate(chunks, start=1):
            self.log(f"Đang dịch phần {i}/{len(chunks)}...")
            source_lines = [text for _, text in chunk]
            source_blob = "\n".join(source_lines)
            try:
                translated_blob = translator.translate(source_blob)
                translated_lines = [line.strip() for line in translated_blob.splitlines() if line.strip()]
            except Exception:
                translated_lines = []
            if len(translated_lines) != len(chunk):
                translated_lines = []
                for _, text in chunk:
                    try:
                        translated_lines.append(translator.translate(text).strip())
                    except Exception:
                        translated_lines.append(text)
            for (idx, _), translated_line in zip(chunk, translated_lines):
                translated_texts[idx] = translated_line
            self.q.put(("progress", min(98, 88 + int(i / max(1, len(chunks)) * 10))))
        translated_rows = []
        for idx, row in enumerate(rows):
            translated_rows.append({"start": row["start"], "end": row["end"], "text": translated_texts[idx] or row["text"]})
        return translated_rows

    def poll_queue(self):
        try:
            while True:
                typ, value = self.q.get_nowait()
                if typ == "status":
                    self.status.set(value)
                elif typ == "progress":
                    self.progress.set(value)
                elif typ == "append_original":
                    self.text_original.insert("end", value)
                    self.text_original.see("end")
                elif typ == "clear_original":
                    self.text_original.delete("1.0", "end")
                elif typ == "set_translation":
                    self.text_translated.delete("1.0", "end")
                    self.text_translated.insert("1.0", value)
                elif typ == "bg_status":
                    if self.video_bg_status:
                        self.video_bg_status.configure(text=str(value)[:80])
                elif typ == "bg_frames":
                    try:
                        from PIL import ImageTk
                        self.video_bg_images = [ImageTk.PhotoImage(img) for img in value]
                        if self.video_bg_status:
                            self.video_bg_status.configure(text=f"Video nền: {len(self.video_bg_images)} frames")
                        self.animate_video_background()
                    except Exception as e:
                        if self.video_bg_status:
                            self.video_bg_status.configure(text=f"Lỗi render nền: {e}")
                elif typ == "update_info":
                    self.status.set("Sẵn sàng")
                    self.start_btn.config(state="normal")
                    messagebox.showinfo("Cập nhật", value)
                elif typ == "update_available":
                    self.status.set("Có bản cập nhật mới")
                    msg = f"Có bản mới v{value.get('version')}.\n\n{value.get('notes') or 'Không có ghi chú.'}\n\nTải về ngay không?"
                    if messagebox.askyesno("Có bản cập nhật mới", msg):
                        self.download_update(value)
                elif typ == "update_ready_to_apply":
                    self.status.set("Đã tải bản cập nhật")
                    if messagebox.askyesno(
                        "Cài cập nhật",
                        "Đã tải xong bản cập nhật.\n\n"
                        "Cài luôn bây giờ không?\n"
                        "App sẽ giữ nguyên .venv, thư viện, output, temp và chỉ ghi đè file app mới."
                    ):
                        self.apply_update_zip(value)
                    else:
                        try:
                            os.startfile(str(UPDATES_DIR))
                        except Exception:
                            pass
                elif typ == "update_downloaded":
                    self.status.set("Đã tải bản cập nhật")
                    messagebox.showinfo("Đã tải cập nhật", f"Đã tải xong file cập nhật:\n{value}\n\nMở thư mục updates, giải nén/chạy file mới để cập nhật.")
                    try:
                        os.startfile(str(UPDATES_DIR))
                    except Exception:
                        pass
                elif typ == "done":
                    self.status.set("Hoàn tất")
                    self.start_btn.config(state="normal")
                    messagebox.showinfo("Hoàn tất", value)
                elif typ == "error":
                    self.status.set("Có lỗi")
                    self.start_btn.config(state="normal")
                    messagebox.showerror("Lỗi", value)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)

    def save_text(self):
        original = self.text_original.get("1.0", "end").strip()
        translated = self.text_translated.get("1.0", "end").strip()
        if not original and not translated:
            messagebox.showinfo("Chưa có dữ liệu", "Chưa có văn bản để lưu.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if not path:
            return
        content = original
        if translated:
            content += "\n\n===== BẢN DỊCH =====\n\n" + translated
        Path(path).write_text(content, encoding="utf-8")
        messagebox.showinfo("Đã lưu", path)

    def save_srt_manual(self):
        rows = self.last_translated_rows if self.last_translated_rows else self.last_rows
        if not rows:
            messagebox.showinfo("Chưa có dữ liệu", "Chưa có dữ liệu để xuất SRT. Hãy xử lý video trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT", "*.srt")])
        if not path:
            return
        Path(path).write_text(self.rows_to_srt(rows), encoding="utf-8-sig")
        messagebox.showinfo("Đã lưu SRT", path)

    def open_output(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        try:
            os.startfile(str(OUTPUT_DIR))
        except Exception:
            messagebox.showinfo("Thư mục output", str(OUTPUT_DIR))

    def open_updates_folder(self):
        UPDATES_DIR.mkdir(exist_ok=True)
        try:
            os.startfile(str(UPDATES_DIR))
        except Exception:
            messagebox.showinfo("Thư mục updates", str(UPDATES_DIR))

    def clear_text(self):
        self.text_original.delete("1.0", "end")
        self.text_translated.delete("1.0", "end")
        self.last_text = ""
        self.last_translation = ""
        self.last_rows = []
        self.last_translated_rows = []
        self.progress.set(0)
        self.status.set("Sẵn sàng")


def main():
    root = tk.Tk()
    TOBOVietSubApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
