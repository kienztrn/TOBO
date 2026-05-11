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
CURRENT_VERSION = "1.8.1"
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

SETTINGS_CONFIG_NAME = "tobo_ui_settings.json"

THEME_PRESETS = {
    "1. Kem cam đào": {
        "bg": "#FFF7ED", "surface": "#FFFBF5", "primary": "#F97316", "secondary": "#FB7185",
        "accent": "#FACC15", "text": "#292524", "muted": "#78716C", "border": "#FED7AA",
    },
    "2. Apple Light": {
        "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#111827", "secondary": "#CBD5E1",
        "accent": "#007AFF", "text": "#1E293B", "muted": "#64748B", "border": "#E5E7EB",
    },
    "3. Apple Light Soft": {
        "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#111827", "secondary": "#CBD5E1",
        "accent": "#007AFF", "text": "#1E293B", "muted": "#64748B", "border": "#E5E7EB",
    },
    "4. Peach Cream": {
        "bg": "#FFF7ED", "surface": "#FFFBF5", "primary": "#F97316", "secondary": "#FB7185",
        "accent": "#FACC15", "text": "#292524", "muted": "#78716C", "border": "#FED7AA",
    },
    "5. Pink Neon Soft": {
        "bg": "#FFF1F7", "surface": "#FFFFFF", "primary": "#DB2777", "secondary": "#9333EA",
        "accent": "#F472B6", "text": "#2E1065", "muted": "#7E6A8A", "border": "#FBCFE8",
    },
    "6. Blue Cloud": {
        "bg": "#F8FBFF", "surface": "#FFFFFF", "primary": "#3B82F6", "secondary": "#60A5FA",
        "accent": "#93C5FD", "text": "#1E3A8A", "muted": "#64748B", "border": "#DBEAFE",
    },
    "7. Golden Warm": {
        "bg": "#FFFBEB", "surface": "#FFFFFF", "primary": "#F59E0B", "secondary": "#FBBF24",
        "accent": "#FDE68A", "text": "#78350F", "muted": "#71635A", "border": "#FDE68A",
    },
    "8. Shopee Peach": {
        "bg": "#FFF7F2", "surface": "#FFFFFF", "primary": "#EE4D2D", "secondary": "#FF6B81",
        "accent": "#FFB86B", "text": "#431407", "muted": "#7C6A63", "border": "#FFD6C2",
    },
    "9. Coffee Gold": {
        "bg": "#FAF7F2", "surface": "#FFFFFF", "primary": "#A16207", "secondary": "#D97706",
        "accent": "#FCD34D", "text": "#292524", "muted": "#78716C", "border": "#E7E0D5",
    },
    "10. Dark Orange": {
        "bg": "#0F0A05", "surface": "#1A120B", "primary": "#F97316", "secondary": "#FB923C",
        "accent": "#FACC15", "text": "#FFF7ED", "muted": "#C4A484", "border": "#7C2D12",
        "success": "#22C55E", "warning": "#F59E0B",
    },
}

LANG_OPTIONS = {
    "vi": "Tiếng Việt",
    "en": "English",
    "ko": "한국어",
    "zh": "中文",
}

APP_LANG = "vi"
CURRENT_THEME_KEY = "2. Apple Light"

I18N = {
    "vi": {
        "subtitle": "Studio phụ đề AI • dịch văn bản sạch • xuất TXT/SRT • cập nhật tại chỗ",
        "control": "TOBO AI CONTROL",
        "mode": "AI LIGHT MODE",
        "settings": "Cài đặt",
        "update_center": "TOBO AI CONTROL",
        "update_desc": "Preset phim hoạt hình, cập nhật tại chỗ và ủng hộ tác giả.",
        "update": "↻ Cập nhật",
        "updates": "☕ Ủng hộ",
        "sparkle": "Sparkle FX",
        "sound": "Âm click",
        "ready": "In-place update ready",
        "keep_libs": "Không xóa .venv • không tải lại thư viện",
        "pick": "＋ Chọn video/audio",
        "source_lang": "Ngôn ngữ gốc",
        "translate": "Dịch",
        "model": "Model AI",
        "device": "Thiết bị",
        "export": "Xuất file",
        "start": "▶ Bắt đầu xử lý",
        "save_txt": "💾 Lưu TXT",
        "export_srt": "🎬 Xuất SRT",
        "output": "📁 Output",
        "clear": "🧹 Xóa",
        "status": "SYSTEM STATUS",
        "original": "Văn bản gốc",
        "original_hint": "Có timestamp để kiểm tra transcript",
        "translation": "Bản dịch",
        "translation_hint": "Bản dịch sạch hoặc kèm <#giây#> nếu bật Delay",
        "app_language": "Ngôn ngữ app",
        "theme": "Bảng màu giao diện",
        "apply": "Áp dụng",
        "close": "Đóng",
        "settings_title": "Cài đặt TOBO VietSub",
        "theme_note": "Đổi theme sẽ áp dụng ngay, không cần cài lại thư viện.",
    },
    "en": {
        "subtitle": "AI subtitle studio • clean translation • TXT/SRT export • in-place updater",
        "control": "TOBO AI CONTROL",
        "mode": "AI LIGHT MODE",
        "settings": "Settings",
        "update_center": "TOBO AI CONTROL",
        "update_desc": "Cartoon preset, in-place update, and creator support.",
        "update": "↻ Update",
        "updates": "☕ Ủng hộ",
        "sparkle": "Sparkle FX",
        "sound": "Click sound",
        "ready": "In-place update ready",
        "keep_libs": "Keep .venv • no library reinstall",
        "pick": "＋ Pick video/audio",
        "source_lang": "Source language",
        "translate": "Translate",
        "model": "AI model",
        "device": "Device",
        "export": "Export file",
        "start": "▶ Start",
        "save_txt": "💾 Save TXT",
        "export_srt": "🎬 Export SRT",
        "output": "📁 Output",
        "clear": "🧹 Clear",
        "status": "SYSTEM STATUS",
        "original": "Original text",
        "original_hint": "Timestamped transcript for checking",
        "translation": "Translation",
        "translation_hint": "Clean translation or <#seconds#> pauses when Delay is on",
        "app_language": "App language",
        "theme": "UI color theme",
        "apply": "Apply",
        "close": "Close",
        "settings_title": "TOBO VietSub Settings",
        "theme_note": "Theme changes apply instantly. Libraries stay untouched.",
    },
    "ko": {
        "subtitle": "AI 자막 스튜디오 • 깔끔한 번역 • TXT/SRT 내보내기 • 제자리 업데이트",
        "control": "TOBO AI CONTROL",
        "mode": "AI LIGHT MODE",
        "settings": "설정",
        "update_center": "TOBO AI CONTROL",
        "update_desc": "TOBO VietSub를 응원해 주셔서 감사합니다.",
        "update": "↻ 업데이트",
        "updates": "☕ Ủng hộ",
        "sparkle": "Sparkle FX",
        "sound": "클릭음",
        "ready": "제자리 업데이트 준비됨",
        "keep_libs": ".venv 유지 • 라이브러리 재설치 없음",
        "pick": "＋ 비디오/오디오 선택",
        "source_lang": "원본 언어",
        "translate": "번역",
        "model": "AI 모델",
        "device": "장치",
        "export": "파일 내보내기",
        "start": "▶ 시작",
        "save_txt": "💾 TXT 저장",
        "export_srt": "🎬 SRT 내보내기",
        "output": "📁 Output",
        "clear": "🧹 지우기",
        "status": "SYSTEM STATUS",
        "original": "원본 텍스트",
        "original_hint": "확인용 타임스탬프 포함",
        "translation": "번역문",
        "translation_hint": "Delay가 켜지면 <#초#> 지연을 포함합니다",
        "app_language": "앱 언어",
        "theme": "UI 색상 테마",
        "apply": "적용",
        "close": "닫기",
        "settings_title": "TOBO VietSub 설정",
        "theme_note": "테마는 즉시 적용됩니다. 라이브러리는 그대로 유지됩니다.",
    },
    "zh": {
        "subtitle": "AI 字幕工作室 • 干净翻译 • 导出 TXT/SRT • 原地更新",
        "control": "TOBO AI CONTROL",
        "mode": "AI LIGHT MODE",
        "settings": "设置",
        "update_center": "TOBO AI CONTROL",
        "update_desc": "Cartoon preset, in-place update, and creator support.",
        "update": "↻ 更新",
        "updates": "☕ Ủng hộ",
        "sparkle": "Sparkle FX",
        "sound": "点击音",
        "ready": "原地更新已就绪",
        "keep_libs": "保留 .venv • 不重新安装库",
        "pick": "＋ 选择视频/音频",
        "source_lang": "源语言",
        "translate": "翻译",
        "model": "AI 模型",
        "device": "设备",
        "export": "导出文件",
        "start": "▶ 开始处理",
        "save_txt": "💾 保存 TXT",
        "export_srt": "🎬 导出 SRT",
        "output": "📁 Output",
        "clear": "🧹 清空",
        "status": "SYSTEM STATUS",
        "original": "原文",
        "original_hint": "带时间戳，方便检查",
        "translation": "译文",
        "translation_hint": "开启延迟时会加入 <#秒#> 停顿",
        "app_language": "应用语言",
        "theme": "界面颜色主题",
        "apply": "应用",
        "close": "关闭",
        "settings_title": "TOBO VietSub 设置",
        "theme_note": "主题会立即应用，不会重新安装库。",
    },
}


EXTRA_I18N = {'vi': {'ready_status': 'Sẵn sàng', 'soft_sparkle_active': 'Lấp lánh nhẹ đang bật', 'soft_sparkle_paused': 'Sparkle FX đã tắt', 'soft_glow': '✦ ánh sáng mềm', 'theme_swatches': ['Nền', 'Card', 'Chính', 'Phụ', 'Nhấn', 'Chữ', 'Mờ', 'Viền'], 'busy_title': 'Đang chạy', 'busy_processing': 'App đang xử lý file hiện tại.', 'busy_settings': 'App đang xử lý video, xử lý xong rồi đổi cài đặt cho an toàn.', 'ui_error_title': 'Lỗi giao diện', 'pick_title': 'Chọn video/audio', 'missing_file_title': 'Thiếu file', 'missing_file_message': 'Bạn hãy chọn video/audio trước.', 'preparing': 'Đang chuẩn bị...', 'loading_model': 'Đang tải/khởi động AI model. Lần đầu có thể lâu vì phải tải model...', 'reading_media': 'Đang đọc trực tiếp video/audio...', 'direct_read_failed': 'Đọc trực tiếp lỗi, thử fallback FFmpeg...', 'transcribing': 'Đang nhận diện giọng nói...', 'detected_lang': 'Đang nhận diện giọng nói. Ngôn ngữ phát hiện: {lang}', 'gpu_failed': 'GPU lỗi hoặc chưa đủ CUDA, chuyển sang CPU. Chi tiết: {error}', 'auto_device_failed': 'Tự động chọn thiết bị lỗi, chuyển sang CPU. Chi tiết: {error}', 'ffmpeg_extract': 'Đang fallback: tách audio bằng FFmpeg...', 'ffmpeg_error': 'FFmpeg lỗi khi tách audio:\n{error}', 'ffmpeg_missing': 'Không đọc trực tiếp được file này và máy chưa có FFmpeg để fallback.\n\nLỗi đọc trực tiếp:\n{error}\n\nCài FFmpeg: winget install Gyan.FFmpeg', 'exported': 'Đã xuất: {files}', 'transcribed_done': 'Đã nhận diện xong.', 'translating_clean': 'Đang dịch văn bản. Ô dịch chỉ hiện text sạch, không kèm timestamp...', 'done_message': 'Hoàn tất. File nằm trong thư mục output.', 'exported_list': 'Đã xuất', 'completed': 'Hoàn tất', 'missing_translate_lib': 'Chưa có thư viện dịch. Hãy chạy install_windows.bat để cài deep-translator.', 'translating_part': 'Đang dịch phần {i}/{total}...', 'no_data_title': 'Chưa có dữ liệu', 'no_text_to_save': 'Chưa có văn bản để lưu.', 'saved_title': 'Đã lưu', 'no_srt_data': 'Chưa có dữ liệu để xuất SRT. Hãy xử lý video trước.', 'saved_srt_title': 'Đã lưu SRT', 'output_folder': 'Thư mục output', 'updates_folder': 'Thư mục updates', 'update_title': 'Cập nhật', 'checking_update': 'Đang kiểm tra cập nhật...', 'update_available_title': 'Có bản cập nhật mới', 'update_available_msg': 'Có bản mới v{version}.\n\n{notes}\n\nTải về ngay không?', 'update_downloaded_title': 'Đã tải cập nhật', 'update_downloaded_msg': 'Đã tải xong file cập nhật:\n{path}\n\nMở thư mục updates, giải nén/chạy file mới để cập nhật.', 'newest_version': 'Bạn đang dùng bản mới nhất rồi: v{version}.', 'update_ready_apply': 'App sẽ tự cập nhật trong cửa sổ mới rồi mở lại.\nĐừng xóa .venv, thư viện sẽ được giữ nguyên.', 'settings_applied': 'Đã áp dụng cài đặt.'}, 'en': {'ready_status': 'Ready', 'soft_sparkle_active': 'Soft sparkle active', 'soft_sparkle_paused': 'Sparkle FX paused', 'soft_glow': '✦ soft glow', 'theme_swatches': ['Background', 'Card', 'Primary', 'Secondary', 'Accent', 'Text', 'Muted', 'Border'], 'busy_title': 'Running', 'busy_processing': 'The app is processing the current file.', 'busy_settings': 'The app is processing a video. Change settings after it finishes.', 'ui_error_title': 'UI error', 'pick_title': 'Choose video/audio', 'missing_file_title': 'Missing file', 'missing_file_message': 'Please choose a video/audio file first.', 'preparing': 'Preparing...', 'loading_model': 'Loading/starting AI model. First run may take longer because the model must download...', 'reading_media': 'Reading video/audio directly...', 'direct_read_failed': 'Direct reading failed, trying FFmpeg fallback...', 'transcribing': 'Transcribing speech...', 'detected_lang': 'Transcribing speech. Detected language: {lang}', 'gpu_failed': 'GPU failed or CUDA is not ready, switching to CPU. Details: {error}', 'auto_device_failed': 'Auto device selection failed, switching to CPU. Details: {error}', 'ffmpeg_extract': 'Fallback: extracting audio with FFmpeg...', 'ffmpeg_error': 'FFmpeg failed while extracting audio:\n{error}', 'ffmpeg_missing': 'This file could not be read directly and FFmpeg is not installed for fallback.\n\nDirect read error:\n{error}\n\nInstall FFmpeg: winget install Gyan.FFmpeg', 'exported': 'Exported: {files}', 'transcribed_done': 'Transcription finished.', 'translating_clean': 'Translating text. The translation panel shows clean text without timestamps...', 'done_message': 'Done. Files are in the output folder.', 'exported_list': 'Exported', 'completed': 'Completed', 'missing_translate_lib': 'Translation library is missing. Run install_windows.bat to install deep-translator.', 'translating_part': 'Translating part {i}/{total}...', 'no_data_title': 'No data', 'no_text_to_save': 'No text to save yet.', 'saved_title': 'Saved', 'no_srt_data': 'No data to export SRT. Process a video first.', 'saved_srt_title': 'SRT saved', 'output_folder': 'Output folder', 'updates_folder': 'Updates folder', 'update_title': 'Update', 'checking_update': 'Checking for updates...', 'update_available_title': 'New update available', 'update_available_msg': 'A new version v{version} is available.\n\n{notes}\n\nDownload now?', 'update_downloaded_title': 'Update downloaded', 'update_downloaded_msg': 'Update file downloaded:\n{path}\n\nOpen the updates folder and run/extract the new file.', 'newest_version': 'You are already on the latest version: v{version}.', 'update_ready_apply': 'The app will update itself in a new window and restart.\nDo not delete .venv; libraries will be preserved.', 'settings_applied': 'Settings applied.'}, 'ko': {'ready_status': '준비됨', 'soft_sparkle_active': '부드러운 반짝임 켜짐', 'soft_sparkle_paused': 'Sparkle FX 꺼짐', 'soft_glow': '✦ 부드러운 빛', 'theme_swatches': ['배경', '카드', '메인', '보조', '강조', '텍스트', '희미함', '테두리'], 'busy_title': '실행 중', 'busy_processing': '현재 파일을 처리 중입니다.', 'busy_settings': '비디오 처리 중입니다. 완료 후 설정을 변경하세요.', 'ui_error_title': 'UI 오류', 'pick_title': '비디오/오디오 선택', 'missing_file_title': '파일 없음', 'missing_file_message': '먼저 비디오/오디오 파일을 선택하세요.', 'preparing': '준비 중...', 'loading_model': 'AI 모델을 불러오는 중입니다. 첫 실행은 모델 다운로드 때문에 오래 걸릴 수 있습니다...', 'reading_media': '비디오/오디오를 직접 읽는 중...', 'direct_read_failed': '직접 읽기 실패, FFmpeg 대체 방식을 시도합니다...', 'transcribing': '음성을 인식하는 중...', 'detected_lang': '음성을 인식하는 중. 감지된 언어: {lang}', 'gpu_failed': 'GPU 오류 또는 CUDA 준비 안 됨, CPU로 전환합니다. 세부 정보: {error}', 'auto_device_failed': '자동 장치 선택 실패, CPU로 전환합니다. 세부 정보: {error}', 'ffmpeg_extract': '대체 방식: FFmpeg로 오디오 추출 중...', 'ffmpeg_error': 'FFmpeg 오디오 추출 오류:\n{error}', 'ffmpeg_missing': '이 파일을 직접 읽을 수 없고 FFmpeg도 설치되어 있지 않습니다.\n\n직접 읽기 오류:\n{error}\n\nFFmpeg 설치: winget install Gyan.FFmpeg', 'exported': '내보냄: {files}', 'transcribed_done': '인식 완료.', 'translating_clean': '번역 중입니다. 번역 영역에는 타임스탬프 없이 텍스트만 표시됩니다...', 'done_message': '완료. 파일은 output 폴더에 있습니다.', 'exported_list': '내보낸 파일', 'completed': '완료', 'missing_translate_lib': '번역 라이브러리가 없습니다. install_windows.bat를 실행해 deep-translator를 설치하세요.', 'translating_part': '번역 중 {i}/{total}...', 'no_data_title': '데이터 없음', 'no_text_to_save': '저장할 텍스트가 없습니다.', 'saved_title': '저장됨', 'no_srt_data': 'SRT로 내보낼 데이터가 없습니다. 먼저 비디오를 처리하세요.', 'saved_srt_title': 'SRT 저장됨', 'output_folder': 'output 폴더', 'updates_folder': 'updates 폴더', 'update_title': '업데이트', 'checking_update': '업데이트 확인 중...', 'update_available_title': '새 업데이트 있음', 'update_available_msg': '새 버전 v{version}이 있습니다.\n\n{notes}\n\n지금 다운로드할까요?', 'update_downloaded_title': '업데이트 다운로드됨', 'update_downloaded_msg': '업데이트 파일 다운로드 완료:\n{path}\n\nupdates 폴더를 열어 새 파일을 실행/압축 해제하세요.', 'newest_version': '이미 최신 버전입니다: v{version}.', 'update_ready_apply': '새 창에서 자동 업데이트 후 앱을 다시 엽니다.\n.venv를 삭제하지 마세요. 라이브러리는 유지됩니다.', 'settings_applied': '설정이 적용되었습니다.'}, 'zh': {'ready_status': '就绪', 'soft_sparkle_active': '柔和闪光已开启', 'soft_sparkle_paused': 'Sparkle FX 已暂停', 'soft_glow': '✦ 柔光', 'theme_swatches': ['背景', '卡片', '主色', '副色', '强调', '文字', '弱化', '边框'], 'busy_title': '正在运行', 'busy_processing': '应用正在处理当前文件。', 'busy_settings': '应用正在处理视频，请完成后再修改设置。', 'ui_error_title': '界面错误', 'pick_title': '选择视频/音频', 'missing_file_title': '缺少文件', 'missing_file_message': '请先选择视频/音频文件。', 'preparing': '正在准备...', 'loading_model': '正在加载/启动 AI 模型。首次运行可能需要下载模型...', 'reading_media': '正在直接读取视频/音频...', 'direct_read_failed': '直接读取失败，尝试 FFmpeg 备用方案...', 'transcribing': '正在识别语音...', 'detected_lang': '正在识别语音。检测到语言：{lang}', 'gpu_failed': 'GPU 错误或 CUDA 未就绪，切换到 CPU。详情：{error}', 'auto_device_failed': '自动选择设备失败，切换到 CPU。详情：{error}', 'ffmpeg_extract': '备用方案：正在用 FFmpeg 提取音频...', 'ffmpeg_error': 'FFmpeg 提取音频失败：\n{error}', 'ffmpeg_missing': '无法直接读取该文件，且未安装 FFmpeg 备用方案。\n\n直接读取错误：\n{error}\n\n安装 FFmpeg：winget install Gyan.FFmpeg', 'exported': '已导出：{files}', 'transcribed_done': '识别完成。', 'translating_clean': '正在翻译文本。译文区域只显示干净文本，不带时间戳...', 'done_message': '完成。文件在 output 文件夹中。', 'exported_list': '已导出', 'completed': '完成', 'missing_translate_lib': '缺少翻译库。请运行 install_windows.bat 安装 deep-translator。', 'translating_part': '正在翻译 {i}/{total}...', 'no_data_title': '没有数据', 'no_text_to_save': '没有可保存的文本。', 'saved_title': '已保存', 'no_srt_data': '没有可导出 SRT 的数据。请先处理视频。', 'saved_srt_title': 'SRT 已保存', 'output_folder': 'output 文件夹', 'updates_folder': 'updates 文件夹', 'update_title': '更新', 'checking_update': '正在检查更新...', 'update_available_title': '有新版本', 'update_available_msg': '发现新版本 v{version}。\n\n{notes}\n\n现在下载吗？', 'update_downloaded_title': '更新已下载', 'update_downloaded_msg': '更新文件已下载：\n{path}\n\n打开 updates 文件夹并运行/解压新文件。', 'newest_version': '你已经是最新版本：v{version}。', 'update_ready_apply': '应用将在新窗口中自动更新并重启。\n不要删除 .venv，库会保留。', 'settings_applied': '设置已应用。'}}
for _lang, _items in EXTRA_I18N.items():
    I18N.setdefault(_lang, {}).update(_items)
I18N["vi"]["error_title"] = "Lỗi"
I18N["en"]["error_title"] = "Error"
I18N["ko"]["error_title"] = "오류"
I18N["zh"]["error_title"] = "错误"
I18N["vi"]["python_missing_update"] = "Đã tải bản cập nhật nhưng không tìm thấy Python để tự áp dụng. Mở thư mục updates rồi giải nén thủ công."
I18N["en"]["python_missing_update"] = "Python was not found, so the update cannot be applied automatically. Open the updates folder and extract it manually."
I18N["ko"]["python_missing_update"] = "Python을 찾을 수 없어 자동 업데이트를 적용할 수 없습니다. updates 폴더를 열고 수동으로 압축을 해제하세요."
I18N["zh"]["python_missing_update"] = "未找到 Python，无法自动应用更新。请打开 updates 文件夹并手动解压。"
I18N["vi"].update({"delay_tags": "Delay <#s#>", "export_voice": "⏱ Xuất Voice TXT", "no_voice_data": "Chưa có bản dịch có delay. Hãy dịch video trước.", "saved_voice_title": "Đã lưu Voice TXT", "timed_translation_hint": "Bản dịch có chèn <#giây#> để canh nhịp theo video", "translating_timed": "Đang tính độ trễ <#giây#> theo timestamp gốc...", "voice_file_suffix": "voice_timing"})
I18N["en"].update({"delay_tags": "Delay <#s#>", "export_voice": "⏱ Export Voice TXT", "no_voice_data": "No timed translation yet. Translate a video first.", "saved_voice_title": "Voice TXT saved", "timed_translation_hint": "Translation with <#seconds#> pauses aligned to the source video", "translating_timed": "Calculating <#seconds#> pauses from source timestamps...", "voice_file_suffix": "voice_timing"})
I18N["ko"].update({"delay_tags": "지연 <#초#>", "export_voice": "⏱ Voice TXT 내보내기", "no_voice_data": "지연이 포함된 번역이 없습니다. 먼저 비디오를 번역하세요.", "saved_voice_title": "Voice TXT 저장됨", "timed_translation_hint": "원본 영상 타임라인에 맞춘 <#초#> 지연 번역", "translating_timed": "원본 타임스탬프로 <#초#> 지연을 계산 중...", "voice_file_suffix": "voice_timing"})
I18N["zh"].update({"delay_tags": "延迟 <#秒#>", "export_voice": "⏱ 导出 Voice TXT", "no_voice_data": "还没有带延迟的译文。请先翻译视频。", "saved_voice_title": "Voice TXT 已保存", "timed_translation_hint": "根据原视频时间轴插入 <#秒#> 停顿的译文", "translating_timed": "正在根据原始时间戳计算 <#秒#> 停顿...", "voice_file_suffix": "voice_timing"})

I18N["vi"].update({
    "translation_style": "Phong cách dịch",
    "output_folder_name": "Tên folder xuất",
    "output_folder_placeholder": "VD: phim_meo_tap_01",
    "style_natural": "Tự nhiên",
    "style_humorous": "Hài hước",
    "style_serious": "Nghiêm túc",
    "style_horror": "Kinh dị",
    "style_romantic": "Lãng mạn",
    "style_scifi": "Khoa học viễn tưởng",
    "style_cartoon": "Hoạt hình vui nhộn",
    "style_action": "Hành động",
    "style_note": "Style dịch dùng hậu xử lý để câu thoại mềm và hợp phim hơn.",
    "export_folder_note": "Nếu nhập tên folder, toàn bộ file xuất sẽ nằm trong output/folder đó.",
    "help_button": "📘 Cách dùng / Bản cập nhật",
    "help_title": "Mô tả app, cách dùng và bản cập nhật",
    "help_body": "TOBO VietSub là app nhận diện lời thoại từ video/audio, dịch văn bản, xuất TXT/SRT và tạo Voice TXT có delay <#giây#>.\n\nCách dùng nhanh:\n1. Chọn video/audio.\n2. Chọn ngôn ngữ gốc hoặc để tự động.\n3. Chọn ngôn ngữ dịch.\n4. Chọn phong cách dịch phù hợp phim: hài hước, nghiêm túc, kinh dị, lãng mạn, khoa học...\n5. Nhập tên folder xuất nếu muốn gom file cho gọn.\n6. Bấm Bắt đầu xử lý.\n\nBản v1.6.6:\n- Thêm phong cách dịch cho phim hoạt hình/phim ngoại quốc.\n- Thêm ô tên folder xuất riêng.\n- Thêm mục mô tả app/cách dùng/bản cập nhật trong Cài đặt.\n- Giữ auto-update in-place, không xóa .venv và không cài lại thư viện.",
    "open_export_folder": "Mở folder xuất",
    "style_applied_status": "Đang áp dụng phong cách dịch: {style}",
})
I18N["en"].update({
    "translation_style": "Translation style",
    "output_folder_name": "Output folder name",
    "output_folder_placeholder": "E.g. cartoon_episode_01",
    "style_natural": "Natural",
    "style_humorous": "Humorous",
    "style_serious": "Serious",
    "style_horror": "Horror",
    "style_romantic": "Romantic",
    "style_scifi": "Sci-fi",
    "style_cartoon": "Playful cartoon",
    "style_action": "Action",
    "style_note": "Translation style uses post-processing to make dialogue softer and more movie-like.",
    "export_folder_note": "If you enter a folder name, all exported files go into output/that folder.",
    "help_button": "📘 Help / Changelog",
    "help_title": "App description, usage and changelog",
    "help_body": "TOBO VietSub transcribes dialogue from video/audio, translates text, exports TXT/SRT, and creates Voice TXT with <#seconds#> delay tags.\n\nQuick use:\n1. Pick a video/audio file.\n2. Choose source language or auto detect.\n3. Choose target translation language.\n4. Pick a translation style: humorous, serious, horror, romantic, sci-fi...\n5. Enter an output folder name if you want files grouped cleanly.\n6. Click Start.\n\nv1.6.6:\n- Added translation style for cartoons/foreign films.\n- Added custom output folder name.\n- Added help/changelog inside Settings.\n- Keeps in-place auto-update without deleting .venv or reinstalling libraries.",
    "open_export_folder": "Open export folder",
    "style_applied_status": "Applying translation style: {style}",
})
I18N["ko"].update({
    "translation_style": "번역 스타일",
    "output_folder_name": "출력 폴더 이름",
    "output_folder_placeholder": "예: cartoon_episode_01",
    "style_natural": "자연스럽게",
    "style_humorous": "유머러스",
    "style_serious": "진지하게",
    "style_horror": "공포",
    "style_romantic": "로맨틱",
    "style_scifi": "SF",
    "style_cartoon": "카툰/장난스럽게",
    "style_action": "액션",
    "style_note": "번역 스타일은 후처리로 대사를 더 부드럽고 영화답게 만듭니다.",
    "export_folder_note": "폴더 이름을 입력하면 모든 출력 파일이 output/해당 폴더에 저장됩니다.",
    "help_button": "📘 사용법 / 업데이트 내역",
    "help_title": "앱 설명, 사용법 및 업데이트 내역",
    "help_body": "TOBO VietSub는 비디오/오디오 대사를 인식하고 번역하며 TXT/SRT 및 <#초#> 지연 태그가 있는 Voice TXT를 생성합니다.\n\n빠른 사용법:\n1. 비디오/오디오를 선택합니다.\n2. 원본 언어를 선택하거나 자동 감지를 둡니다.\n3. 번역 언어를 선택합니다.\n4. 유머, 진지함, 공포, 로맨스, SF 등 번역 스타일을 고릅니다.\n5. 파일을 정리할 출력 폴더 이름을 입력합니다.\n6. 시작을 누릅니다.\n\nv1.6.6:\n- 만화/해외 영화용 번역 스타일 추가.\n- 사용자 지정 출력 폴더 추가.\n- 설정 안에 도움말/업데이트 내역 추가.\n- .venv 및 라이브러리를 유지하는 제자리 업데이트 유지.",
    "open_export_folder": "출력 폴더 열기",
    "style_applied_status": "번역 스타일 적용 중: {style}",
})
I18N["zh"].update({
    "translation_style": "翻译风格",
    "output_folder_name": "输出文件夹名称",
    "output_folder_placeholder": "例如：cartoon_episode_01",
    "style_natural": "自然",
    "style_humorous": "幽默",
    "style_serious": "严肃",
    "style_horror": "恐怖",
    "style_romantic": "浪漫",
    "style_scifi": "科幻",
    "style_cartoon": "卡通活泼",
    "style_action": "动作",
    "style_note": "翻译风格会通过后处理让对白更柔和、更像影视台词。",
    "export_folder_note": "输入文件夹名称后，所有导出文件会进入 output/该文件夹。",
    "help_button": "📘 使用说明 / 更新日志",
    "help_title": "应用说明、使用方法和更新日志",
    "help_body": "TOBO VietSub 可从视频/音频识别对白，翻译文本，导出 TXT/SRT，并生成带 <#秒#> 延迟标签的 Voice TXT。\n\n快速使用：\n1. 选择视频/音频。\n2. 选择源语言或自动识别。\n3. 选择目标翻译语言。\n4. 选择翻译风格：幽默、严肃、恐怖、浪漫、科幻等。\n5. 输入输出文件夹名称，方便整理。\n6. 点击开始。\n\nv1.6.6：\n- 添加适合动画/外国影片的翻译风格。\n- 添加自定义输出文件夹。\n- 在设置中添加帮助/更新日志。\n- 保留原地自动更新，不删除 .venv，不重新安装库。",
    "open_export_folder": "打开输出文件夹",
    "style_applied_status": "正在应用翻译风格：{style}",
})
I18N["vi"].update({"config_file": "File cần sửa", "url_404": "{purpose} lỗi 404: link update không tồn tại hoặc chưa upload file.", "url_http": "{purpose} lỗi HTTP {code}: {reason}", "url_dns": "{purpose} lỗi DNS: domain update không tồn tại/sai link/mất mạng.", "url_network": "{purpose} lỗi mạng: {reason}", "manifest_not_json": "{purpose} lỗi: manifest không phải JSON hợp lệ.", "generic_error": "{purpose} lỗi: {error}"})
I18N["en"].update({"config_file": "Config file", "url_404": "{purpose} 404 error: update link does not exist or file has not been uploaded.", "url_http": "{purpose} HTTP {code}: {reason}", "url_dns": "{purpose} DNS error: update domain does not exist, link is wrong, or network is down.", "url_network": "{purpose} network error: {reason}", "manifest_not_json": "{purpose} error: manifest is not valid JSON.", "generic_error": "{purpose} error: {error}"})
I18N["ko"].update({"config_file": "수정할 파일", "url_404": "{purpose} 404 오류: 업데이트 링크가 없거나 파일이 업로드되지 않았습니다.", "url_http": "{purpose} HTTP {code}: {reason}", "url_dns": "{purpose} DNS 오류: 업데이트 도메인이 없거나 링크가 잘못되었거나 네트워크가 끊겼습니다.", "url_network": "{purpose} 네트워크 오류: {reason}", "manifest_not_json": "{purpose} 오류: manifest가 올바른 JSON이 아닙니다.", "generic_error": "{purpose} 오류: {error}"})
I18N["zh"].update({"config_file": "需要修改的文件", "url_404": "{purpose} 404 错误：更新链接不存在或文件尚未上传。", "url_http": "{purpose} HTTP {code}: {reason}", "url_dns": "{purpose} DNS 错误：更新域名不存在、链接错误或网络不可用。", "url_network": "{purpose} 网络错误：{reason}", "manifest_not_json": "{purpose} 错误：manifest 不是有效 JSON。", "generic_error": "{purpose} 错误：{error}"})

I18N["vi"].update({
    "system_check": "🩺 Kiểm tra hệ thống",
    "system_check_title": "Kiểm tra hệ thống",
    "system_check_running": "Đang kiểm tra hệ thống...",
    "system_check_done": "Đã kiểm tra hệ thống.",
    "read_speed": "Tốc độ đọc",
    "speed_slow": "Chậm",
    "speed_normal": "Vừa",
    "speed_fast": "Nhanh",
    "delay_min": "Delay tối thiểu",
    "delay_max": "Delay tối đa",
    "delay_round": "Làm tròn delay",
    "delay_skip": "Bỏ delay < 0.2s",
    "voice_timing_settings": "Thiết lập Voice Delay",
})
I18N["en"].update({
    "system_check": "🩺 System check",
    "system_check_title": "System check",
    "system_check_running": "Checking system...",
    "system_check_done": "System check completed.",
    "read_speed": "Read speed",
    "speed_slow": "Slow",
    "speed_normal": "Normal",
    "speed_fast": "Fast",
    "delay_min": "Min delay",
    "delay_max": "Max delay",
    "delay_round": "Round delay",
    "delay_skip": "Skip delay < 0.2s",
    "voice_timing_settings": "Voice Delay Settings",
})
I18N["ko"].update({
    "system_check": "🩺 시스템 확인",
    "system_check_title": "시스템 확인",
    "system_check_running": "시스템 확인 중...",
    "system_check_done": "시스템 확인 완료.",
    "read_speed": "읽기 속도",
    "speed_slow": "느림",
    "speed_normal": "보통",
    "speed_fast": "빠름",
    "delay_min": "최소 Delay",
    "delay_max": "최대 Delay",
    "delay_round": "Delay 반올림",
    "delay_skip": "0.2초 미만 Delay 생략",
    "voice_timing_settings": "Voice Delay 설정",
})
I18N["zh"].update({
    "system_check": "🩺 系统检查",
    "system_check_title": "系统检查",
    "system_check_running": "正在检查系统...",
    "system_check_done": "系统检查完成。",
    "read_speed": "朗读速度",
    "speed_slow": "慢",
    "speed_normal": "中",
    "speed_fast": "快",
    "delay_min": "最小延迟",
    "delay_max": "最大延迟",
    "delay_round": "延迟取整",
    "delay_skip": "跳过 <0.2秒 延迟",
    "voice_timing_settings": "Voice Delay 设置",
})


def get_settings_path() -> Path:
    return APP_DIR / SETTINGS_CONFIG_NAME


def load_ui_settings() -> dict:
    defaults = {"app_language": "vi", "theme": CURRENT_THEME_KEY}
    path = get_settings_path()
    if not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return defaults
        defaults.update({k: v for k, v in data.items() if k in defaults})
        return defaults
    except Exception:
        return defaults


def save_ui_settings(data: dict):
    path = get_settings_path()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_theme(theme_key: str):
    global BG_COLOR, BG_2, SURFACE, SURFACE_2, CARD, ACCENT, ACCENT_2, ACCENT_3
    global TEXT, TEXT_MUTED, TEXT_DIM, BORDER, ENTRY_BG, TEXTBOX_BG, SUCCESS, WARNING, CURRENT_THEME_KEY
    theme = THEME_PRESETS.get(theme_key) or THEME_PRESETS.get(CURRENT_THEME_KEY) or next(iter(THEME_PRESETS.values()))
    CURRENT_THEME_KEY = theme_key if theme_key in THEME_PRESETS else CURRENT_THEME_KEY
    BG_COLOR = theme["bg"]
    BG_2 = theme["bg"]
    SURFACE = theme["surface"]
    SURFACE_2 = theme["surface"]
    CARD = theme["surface"]
    ACCENT = theme["primary"]
    ACCENT_2 = theme["accent"]
    ACCENT_3 = theme["secondary"]
    TEXT = theme["text"]
    TEXT_MUTED = theme["muted"]
    TEXT_DIM = theme["muted"]
    BORDER = theme["border"]
    ENTRY_BG = theme["surface"]
    TEXTBOX_BG = theme["surface"]
    SUCCESS = theme.get("success", "#16A34A")
    WARNING = theme.get("warning", "#D97706")


OPTION_TABLES = {
    "vi": {
        "source": [(None, "Tự động nhận diện"), ("vi", "Tiếng Việt"), ("en", "Tiếng Anh"), ("zh", "Tiếng Trung"), ("ja", "Tiếng Nhật"), ("ko", "Tiếng Hàn"), ("fr", "Tiếng Pháp"), ("de", "Tiếng Đức"), ("es", "Tiếng Tây Ban Nha"), ("th", "Tiếng Thái"), ("id", "Tiếng Indonesia")],
        "translate": [(None, "Không dịch"), ("vi", "Dịch sang Tiếng Việt"), ("en", "Dịch sang Tiếng Anh"), ("zh-CN", "Dịch sang Tiếng Trung"), ("ja", "Dịch sang Tiếng Nhật"), ("ko", "Dịch sang Tiếng Hàn"), ("fr", "Dịch sang Tiếng Pháp"), ("de", "Dịch sang Tiếng Đức"), ("es", "Dịch sang Tiếng Tây Ban Nha"), ("th", "Dịch sang Tiếng Thái"), ("id", "Dịch sang Tiếng Indonesia")],
        "model": [("large-v3-turbo", "Turbo - large-v3-turbo"), ("tiny", "Nhanh nhất - tiny"), ("base", "Nhanh - base"), ("small", "Cân bằng - small"), ("medium", "Chính xác hơn - medium"), ("large-v3", "Rất chính xác - large-v3")],
        "device": [("auto", "Tự động"), ("cpu", "CPU"), ("gpu", "GPU NVIDIA")],
    },
    "en": {
        "source": [(None, "Auto detect"), ("vi", "Vietnamese"), ("en", "English"), ("zh", "Chinese"), ("ja", "Japanese"), ("ko", "Korean"), ("fr", "French"), ("de", "German"), ("es", "Spanish"), ("th", "Thai"), ("id", "Indonesian")],
        "translate": [(None, "No translation"), ("vi", "Translate to Vietnamese"), ("en", "Translate to English"), ("zh-CN", "Translate to Chinese"), ("ja", "Translate to Japanese"), ("ko", "Translate to Korean"), ("fr", "Translate to French"), ("de", "Translate to German"), ("es", "Translate to Spanish"), ("th", "Translate to Thai"), ("id", "Translate to Indonesian")],
        "model": [("large-v3-turbo", "Turbo - large-v3-turbo"), ("tiny", "Fastest - tiny"), ("base", "Fast - base"), ("small", "Balanced - small"), ("medium", "More accurate - medium"), ("large-v3", "Very accurate - large-v3")],
        "device": [("auto", "Auto"), ("cpu", "CPU"), ("gpu", "NVIDIA GPU")],
    },
    "ko": {
        "source": [(None, "자동 감지"), ("vi", "베트남어"), ("en", "영어"), ("zh", "중국어"), ("ja", "일본어"), ("ko", "한국어"), ("fr", "프랑스어"), ("de", "독일어"), ("es", "스페인어"), ("th", "태국어"), ("id", "인도네시아어")],
        "translate": [(None, "번역 안 함"), ("vi", "베트남어로 번역"), ("en", "영어로 번역"), ("zh-CN", "중국어로 번역"), ("ja", "일본어로 번역"), ("ko", "한국어로 번역"), ("fr", "프랑스어로 번역"), ("de", "독일어로 번역"), ("es", "스페인어로 번역"), ("th", "태국어로 번역"), ("id", "인도네시아어로 번역")],
        "model": [("large-v3-turbo", "터보 - large-v3-turbo"), ("tiny", "가장 빠름 - tiny"), ("base", "빠름 - base"), ("small", "균형 - small"), ("medium", "더 정확함 - medium"), ("large-v3", "매우 정확함 - large-v3")],
        "device": [("auto", "자동"), ("cpu", "CPU"), ("gpu", "NVIDIA GPU")],
    },
    "zh": {
        "source": [(None, "自动识别"), ("vi", "越南语"), ("en", "英语"), ("zh", "中文"), ("ja", "日语"), ("ko", "韩语"), ("fr", "法语"), ("de", "德语"), ("es", "西班牙语"), ("th", "泰语"), ("id", "印尼语")],
        "translate": [(None, "不翻译"), ("vi", "翻译成越南语"), ("en", "翻译成英语"), ("zh-CN", "翻译成中文"), ("ja", "翻译成日语"), ("ko", "翻译成韩语"), ("fr", "翻译成法语"), ("de", "翻译成德语"), ("es", "翻译成西班牙语"), ("th", "翻译成泰语"), ("id", "翻译成印尼语")],
        "model": [("large-v3-turbo", "Turbo - large-v3-turbo"), ("tiny", "最快 - tiny"), ("base", "快速 - base"), ("small", "平衡 - small"), ("medium", "更准确 - medium"), ("large-v3", "非常准确 - large-v3")],
        "device": [("auto", "自动"), ("cpu", "CPU"), ("gpu", "NVIDIA GPU")],
    },
}


STYLE_OPTION_TABLES = {
    "vi": [
        ("faithful", "Giữ nghĩa sát"),
        ("natural", "Dịch tự nhiên"),
        ("viral_tiktok", "Dịch viral/TikTok"),
        ("cartoon_movie", "Dịch phim hoạt hình"),
        ("dubbing", "Dịch lồng tiếng"),
        ("silly_fun", "Dịch hài bựa nhẹ"),
        ("polite", "Dịch lịch sự"),
        ("native", "Dịch như người bản xứ"),
    ],
    "en": [
        ("faithful", "Faithful meaning"),
        ("natural", "Natural translation"),
        ("viral_tiktok", "Viral/TikTok style"),
        ("cartoon_movie", "Cartoon movie style"),
        ("dubbing", "Voice dubbing style"),
        ("silly_fun", "Light silly comedy"),
        ("polite", "Polite style"),
        ("native", "Native speaker style"),
    ],
    "ko": [
        ("faithful", "의미 충실"),
        ("natural", "자연스러운 번역"),
        ("viral_tiktok", "바이럴/TikTok 스타일"),
        ("cartoon_movie", "애니메이션 영화 스타일"),
        ("dubbing", "더빙 대사 스타일"),
        ("silly_fun", "가벼운 코미디 스타일"),
        ("polite", "정중한 스타일"),
        ("native", "원어민 스타일"),
    ],
    "zh": [
        ("faithful", "忠实原意"),
        ("natural", "自然翻译"),
        ("viral_tiktok", "爆款/TikTok 风格"),
        ("cartoon_movie", "动画电影风格"),
        ("dubbing", "配音台词风格"),
        ("silly_fun", "轻松搞笑风格"),
        ("polite", "礼貌风格"),
        ("native", "母语者风格"),
    ],
}

SPEED_OPTION_TABLES = {
    "vi": [("slow", "Chậm"), ("normal", "Vừa"), ("fast", "Nhanh")],
    "en": [("slow", "Slow"), ("normal", "Normal"), ("fast", "Fast")],
    "ko": [("slow", "느림"), ("normal", "보통"), ("fast", "빠름")],
    "zh": [("slow", "慢"), ("normal", "中"), ("fast", "快")],
}

def speed_options() -> list[str]:
    return [label for _, label in SPEED_OPTION_TABLES.get(APP_LANG, SPEED_OPTION_TABLES["vi"])]

def speed_label(value: str) -> str:
    for code, label in SPEED_OPTION_TABLES.get(APP_LANG, SPEED_OPTION_TABLES["vi"]):
        if code == value:
            return label
    return SPEED_OPTION_TABLES.get(APP_LANG, SPEED_OPTION_TABLES["vi"])[1][1]

def speed_value(label: str) -> str:
    for table in SPEED_OPTION_TABLES.values():
        for code, any_label in table:
            if any_label == label:
                return code
    return "normal"

def style_options() -> list[str]:
    return [label for _, label in STYLE_OPTION_TABLES.get(APP_LANG, STYLE_OPTION_TABLES["vi"])]

def style_label(value: str) -> str:
    for code, label in STYLE_OPTION_TABLES.get(APP_LANG, STYLE_OPTION_TABLES["vi"]):
        if code == value:
            return label
    return STYLE_OPTION_TABLES.get(APP_LANG, STYLE_OPTION_TABLES["vi"])[0][1]

def style_value(label: str) -> str:
    for table in STYLE_OPTION_TABLES.values():
        for code, any_label in table:
            if any_label == label:
                return code
    return "natural"

def option_map(kind: str) -> dict:
    table = OPTION_TABLES.get(APP_LANG, OPTION_TABLES["vi"]).get(kind, [])
    return {label: value for value, label in table}

def option_label(kind: str, value):
    table = OPTION_TABLES.get(APP_LANG, OPTION_TABLES["vi"]).get(kind, [])
    for code, label in table:
        if code == value:
            return label
    return table[0][1] if table else ""

def option_value(kind: str, label: str):
    mapping = option_map(kind)
    if label in mapping:
        return mapping[label]
    # fallback: scan every language so old labels still map correctly after language switch
    for lang_table in OPTION_TABLES.values():
        for code, any_label in lang_table.get(kind, []):
            if any_label == label:
                return code
    return None


def tr(key: str) -> str:
    table = I18N.get(APP_LANG) or I18N["vi"]
    return table.get(key, I18N["vi"].get(key, key))


_loaded_ui = load_ui_settings()
APP_LANG = _loaded_ui.get("app_language", "vi") if _loaded_ui.get("app_language") in LANG_OPTIONS else "vi"
apply_theme(_loaded_ui.get("theme", CURRENT_THEME_KEY))

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
    "Turbo - large-v3-turbo": "large-v3-turbo",
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
    log(tr("ffmpeg_extract"))
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0:
        raise RuntimeError(tr("ffmpeg_error").format(error=proc.stderr[-2500:]))


class NeonButton(tk.Button):
    def __init__(self, master, text, command=None, variant="primary", sound_callback=None, **kwargs):
        self.variant = variant
        self.sound_callback = sound_callback
        self.user_command = command
        palette = {
            "primary": (ACCENT, ACCENT_3, "#FFFFFF"),
            "cyan": (ACCENT_2, ACCENT, "#FFFFFF"),
            "pink": (ACCENT_3, ACCENT, "#FFFFFF"),
            "ghost": (SURFACE_2, BORDER, TEXT),
            "dark": (SURFACE, SURFACE_2, TEXT),
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
        self.root.geometry("1180x820")
        self.root.minsize(1080, 740)
        self.root.configure(bg=BG_COLOR)
        self.q = queue.Queue()
        self.worker = None
        self.selected_file = tk.StringVar()
        self.language = tk.StringVar(value=option_label("source", None))
        self.translate_to = tk.StringVar(value=option_label("translate", None))
        self.model_size = tk.StringVar(value=option_label("model", "large-v3-turbo"))
        self.device_mode = tk.StringVar(value=option_label("device", "auto"))
        self.export_format = tk.StringVar(value="TXT + SRT")
        self.translation_style = tk.StringVar(value=style_label("natural"))
        self.output_folder_name = tk.StringVar(value="")
        self.delay_tags_enabled = tk.BooleanVar(value=True)
        self.read_speed = tk.StringVar(value=speed_label("normal"))
        self.delay_min = tk.StringVar(value="0.10")
        self.delay_max = tk.StringVar(value="2.50")
        self.delay_round = tk.StringVar(value="0.05")
        self.srt_max_lines = tk.StringVar(value="0")
        self.delay_skip_small = tk.BooleanVar(value=True)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value=tr("ready_status"))
        self.progress = tk.DoubleVar(value=0)
        self.last_text = ""
        self.last_translation = ""
        self.last_clean_translation = ""
        self.last_timed_translation = ""
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
        self.settings_panel = None
        self.shell = None
        self.main_container = None
        self.controls_collapsed = False
        self.controls_toggle_btn = None
        self.controls_rows = []
        self.loader_canvas = None
        self.loader_tick = 0
        self.loader_popup = None
        self.loader_popup_canvas = None
        self.loader_popup_label = None
        self.ui_locked = False
        self.video_bg_enabled = tk.BooleanVar(value=True)
        self.video_bg_label = None
        self.video_bg_status = None
        self.video_bg_images = []
        self.video_bg_index = 0
        self.video_bg_delay_ms = 90
        self.video_bg_size = (304, 112)
        self.setup_branding()
        self.build_ui()
        self.root.after(100, self.poll_queue)
        self.root.after(220, self.animate_pulse)
        self.root.after(260, self.animate_loader)
        self.root.after(600, self.start_video_background)

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
        self.shell = shell

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
            text=tr("subtitle"),
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

        top_strip = tk.Frame(control_card, bg=SURFACE, height=32)
        top_strip.pack(fill="x", side="top")
        top_strip.pack_propagate(False)
        tk.Label(
            top_strip,
            text=tr("control"),
            bg=SURFACE,
            fg=ACCENT,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=14)
        self.settings_button = tk.Button(
            top_strip,
            text="☰",
            command=self.open_settings,
            bg=SURFACE_2,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.settings_button.pack(side="right", padx=(0, 12), pady=3)
        tk.Label(
            top_strip,
            text=f"v{CURRENT_VERSION}",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(0, 10))

        card_body = tk.Frame(control_card, bg=SURFACE)
        card_body.pack(fill="both", expand=True, padx=14, pady=12)

        video_panel = tk.Frame(card_body, bg=SURFACE_2, width=304, height=112, highlightthickness=1, highlightbackground=BORDER)
        video_panel.pack(side="left", fill="y")
        video_panel.pack_propagate(False)

        self.video_bg_label = tk.Label(
            video_panel,
            text="Loading video...",
            bg=SURFACE_2,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9, "bold"),
            justify="center",
        )
        self.video_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.video_bg_status = None

        control_panel = tk.Frame(card_body, bg=SURFACE, width=250)
        control_panel.pack(side="left", fill="both", expand=True, padx=(16, 0))

        tk.Label(
            control_panel,
            text=tr("update_center"),
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI Variable Display", 11, "bold"),
            justify="left",
            wraplength=238,
        ).pack(anchor="w")
        tk.Label(
            control_panel,
            text=tr("update_desc"),
            bg=SURFACE,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=238,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(3, 6))

        action_row = tk.Frame(control_panel, bg=SURFACE)
        action_row.pack(fill="x")
        NeonButton(action_row, tr("update"), self.check_update, variant="primary", sound_callback=self.play_click).pack(side="left")
        NeonButton(action_row, tr("updates"), self.show_support_qr, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(8, 0))

        toggle_row = tk.Frame(control_panel, bg=SURFACE)
        toggle_row.pack(fill="x", pady=(12, 0))
        tk.Checkbutton(
            toggle_row,
            text=tr("sparkle"),
            variable=self.sparkle_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="left")
        tk.Checkbutton(
            toggle_row,
            text=tr("sound"),
            variable=self.sound_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="left", padx=(14, 0))

        info_row = tk.Frame(control_panel, bg=SURFACE)
        info_row.pack(fill="x", pady=(12, 0))
        tk.Label(
            info_row,
            text=tr("ready"),
            bg=SURFACE,
            fg=SUCCESS,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info_row,
            text=tr("keep_libs"),
            bg=SURFACE,
            fg=TEXT_DIM,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(3, 0))

        main = tk.Frame(shell, bg=BG_COLOR)
        self.main_container = main
        main.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        top = tk.Frame(main, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        top.pack(fill="x", pady=(0, 12))

        file_row = tk.Frame(top, bg=SURFACE)
        file_row.pack(fill="x", padx=16, pady=(16, 12))
        NeonButton(file_row, tr("pick"), self.pick_file, variant="cyan", sound_callback=self.play_click).pack(side="left")
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
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(12, 10), ipady=10)
        # Nút thu/phóng thiết lập đã được chuyển xuống hàng thao tác.

        options = tk.Frame(top, bg=SURFACE)
        options.pack(fill="x", padx=16, pady=(0, 14))
        for col in range(5):
            options.columnconfigure(col, weight=1)

        self.add_combo(options, tr("source_lang"), self.language, list(option_map("source").keys()), 0)
        self.add_combo(options, tr("translate"), self.translate_to, list(option_map("translate").keys()), 1)
        self.add_combo(options, tr("model"), self.model_size, list(option_map("model").keys()), 2)
        self.add_combo(options, tr("device"), self.device_mode, list(option_map("device").keys()), 3)
        self.add_combo(options, tr("export"), self.export_format, list(EXPORT_FORMATS.keys()), 4)

        advanced_options = tk.Frame(top, bg=SURFACE)
        advanced_options.pack(fill="x", padx=16, pady=(0, 14))
        advanced_options.columnconfigure(0, weight=1)
        advanced_options.columnconfigure(1, weight=2)
        self.add_combo(advanced_options, tr("translation_style"), self.translation_style, style_options(), 0)
        folder_frame = tk.Frame(advanced_options, bg=SURFACE)
        folder_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        tk.Label(folder_frame, text=tr("output_folder_name"), bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.output_folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.output_folder_name,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT_2,
        )
        voice_options = tk.Frame(top, bg=SURFACE)
        voice_options.pack(fill="x", padx=16, pady=(0, 14))
        for col in range(6):
            voice_options.columnconfigure(col, weight=1)
        self.add_combo(voice_options, tr("read_speed"), self.read_speed, speed_options(), 0)

        def small_entry(parent, label, var, col):
            fr = tk.Frame(parent, bg=SURFACE)
            fr.grid(row=0, column=col, sticky="ew", padx=(10 if col else 0, 0))
            tk.Label(fr, text=label, bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ent = tk.Entry(fr, textvariable=var, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10), highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT_2)
            ent.pack(fill="x", pady=(6, 0), ipady=5)
            return ent

        small_entry(voice_options, tr("delay_min"), self.delay_min, 1)
        small_entry(voice_options, tr("delay_max"), self.delay_max, 2)
        small_entry(voice_options, tr("delay_round"), self.delay_round, 3)
        small_entry(voice_options, tr("srt_max_lines"), self.srt_max_lines, 4)
        skip_box = tk.Frame(voice_options, bg=SURFACE)
        skip_box.grid(row=0, column=5, sticky="ew", padx=(10, 0))
        tk.Label(skip_box, text=tr("voice_timing_settings"), bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Checkbutton(
            skip_box,
            text=tr("delay_skip"),
            variable=self.delay_skip_small,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(anchor="w", pady=(6, 0))

        btns = tk.Frame(top, bg=SURFACE)
        btns.pack(fill="x", padx=16, pady=(0, 16))
        self.controls_toggle_btn = NeonButton(
            btns,
            "✓ Thiết lập xong",
            self.toggle_controls_panel,
            variant="primary",
            sound_callback=self.play_click,
        )
        self.controls_toggle_btn.pack(side="left")
        NeonButton(btns, tr("cartoon_mode"), self.apply_cartoon_mode, variant="pink", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("save_txt"), self.save_text, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("export_srt"), self.save_srt_manual, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("export_voice"), self.save_voice_timing_manual, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("system_check"), self.check_system, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("output"), self.open_output, variant="ghost", sound_callback=self.play_click).pack(side="left", padx=(10, 0))
        NeonButton(btns, tr("clear"), self.clear_text, variant="dark", sound_callback=self.play_click).pack(side="left", padx=(10, 0))

        tk.Checkbutton(
            btns,
            text=tr("delay_tags"),
            variable=self.delay_tags_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="right", padx=(0, 14))

        tk.Checkbutton(
            btns,
            text=tr("sparkle"),
            variable=self.sparkle_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="right", padx=(0, 14))

        tk.Checkbutton(
            btns,
            text=tr("sound"),
            variable=self.sound_enabled,
            bg=SURFACE,
            fg=TEXT_MUTED,
            activebackground=SURFACE,
            activeforeground=TEXT,
            selectcolor=ENTRY_BG,
            font=("Segoe UI", 10),
            relief="flat",
        ).pack(side="right")

        self.controls_collapsed = False
        self.controls_rows = [
            (options, {"fill": "x", "padx": 16, "pady": (0, 14)}),
            (advanced_options, {"fill": "x", "padx": 16, "pady": (0, 14)}),
            (voice_options, {"fill": "x", "padx": 16, "pady": (0, 14)}),
        ]

        process_strip = tk.Frame(main, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        process_strip.pack(fill="x", pady=(0, 8))
        start_wrap = tk.Frame(process_strip, bg=SURFACE)
        start_wrap.pack(anchor="center", pady=10)
        self.quick_start_btn = NeonButton(
            start_wrap,
            tr("start"),
            self.start,
            variant="primary",
            sound_callback=self.play_click,
        )
        self.quick_start_btn.pack()
        self.start_btn = self.quick_start_btn
        self.status_label = None

        panes = ttk.PanedWindow(main, orient="horizontal")
        panes.pack(fill="both", expand=True)

        left = self.make_text_card(panes, tr("original"), tr("original_hint"))
        right = self.make_text_card(panes, tr("translation"), tr("translation_hint"))
        panes.add(left, weight=1)
        panes.add(right, weight=1)

        self.text_original = self.make_textbox(left)
        self.text_original.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.text_translated = self.make_textbox(right)
        self.text_translated.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def toggle_controls_panel(self):
        """Thu/phóng khung cấu hình chính để giao diện gọn hơn."""
        try:
            self.play_click()
            self.controls_collapsed = not self.controls_collapsed
            if self.controls_collapsed:
                for widget, _pack_opts in self.controls_rows:
                    try:
                        widget.pack_forget()
                    except Exception:
                        pass
                if self.controls_toggle_btn:
                    self.controls_toggle_btn.configure(text="▾ Mở thiết lập")
            else:
                for widget, pack_opts in self.controls_rows:
                    try:
                        widget.pack(**pack_opts)
                    except Exception:
                        pass
                if self.controls_toggle_btn:
                    self.controls_toggle_btn.configure(text="✓ Thiết lập xong")
        except Exception as e:
            messagebox.showerror(tr("ui_error_title"), str(e))

    def draw_loader(self):
        """Truck overlay loader dựng bằng Tkinter Canvas theo ý tưởng Uiverse CSS."""
        c = getattr(self, "loader_popup_canvas", None)
        if not c:
            return
        try:
            c.delete("all")
            w, h = 340, 165
            pct = max(0, min(100, float(self.progress.get() or 0)))
            active = bool((self.worker and self.worker.is_alive()) or self.ui_locked)
            phase = self.loader_tick

            # Background card.
            c.create_rectangle(0, 0, w, h, fill="#FFFFFF", outline="")
            c.create_rectangle(12, 12, w - 12, h - 12, fill="#FFFBF5", outline=BORDER, width=1)
            # Truck wrapper.
            base_x = 104
            base_y = 104
            bounce = math.sin(phase / 3.0) * 3 if active else 0
            road_y = 132

            # Moving road marks.
            c.create_line(60, road_y, 280, road_y, fill="#282828", width=2)
            if active:
                off = (phase * 9) % 80
                for mx in range(-30, 300, 70):
                    x1 = 280 - ((mx + off) % 320)
                    c.create_line(x1, road_y - 1, x1 + 24, road_y - 1, fill="#282828", width=3)

                # Lamp post sliding.
                lamp_x = 320 - ((phase * 7) % 410)
                c.create_line(lamp_x, road_y, lamp_x, road_y - 62, fill="#282828", width=3)
                c.create_line(lamp_x, road_y - 62, lamp_x + 18, road_y - 70, fill="#282828", width=3)
                c.create_oval(lamp_x + 14, road_y - 76, lamp_x + 26, road_y - 64, fill=ACCENT, outline="#282828")

            # Truck body.
            bx = base_x
            by = base_y + bounce
            primary = ACCENT if ACCENT else "#F97316"
            dark = TEXT if TEXT else "#282828"
            # cargo box
            c.create_rectangle(bx, by - 46, bx + 82, by - 12, fill=primary, outline=dark, width=2)
            c.create_rectangle(bx + 10, by - 38, bx + 40, by - 20, fill="#FFF7ED", outline=dark, width=1)
            # cabin
            c.create_polygon(bx + 82, by - 46, bx + 112, by - 34, bx + 122, by - 12, bx + 82, by - 12, fill="#FB923C", outline=dark, width=2)
            c.create_polygon(bx + 88, by - 38, bx + 108, by - 30, bx + 113, by - 20, bx + 88, by - 20, fill="#DBEAFE", outline=dark, width=1)
            # bumper/underbody
            c.create_rectangle(bx - 6, by - 14, bx + 130, by - 4, fill=dark, outline=dark)
            c.create_rectangle(bx + 122, by - 18, bx + 136, by - 8, fill=ACCENT_3, outline=dark, width=1)

            # Wheels.
            wheel_angle = phase * 20 if active else 0
            for wx in (bx + 28, bx + 100):
                c.create_oval(wx - 14, by - 15, wx + 14, by + 13, fill=dark, outline=dark)
                c.create_oval(wx - 7, by - 8, wx + 7, by + 6, fill="#FFFFFF", outline="#FFFFFF")
                # spokes
                r = 11
                for a in (0, math.pi / 2):
                    ang = math.radians(wheel_angle) + a
                    c.create_line(wx - math.cos(ang) * r, by - 1 - math.sin(ang) * r, wx + math.cos(ang) * r, by - 1 + math.sin(ang) * r, fill="#FFFFFF", width=1)

            # Progress text + bar.
            c.create_rectangle(66, 146, 274, 154, fill=BORDER, outline="")
            if pct > 0:
                c.create_rectangle(66, 146, 66 + int(208 * pct / 100), 154, fill=primary, outline="")
            c.create_text(w / 2, 160, text=f"{int(pct)}%", fill=TEXT_MUTED, font=("Segoe UI", 9, "bold"))

            if self.loader_popup_label:
                self.loader_popup_label.configure(text=self.status.get() or "Loading...")
        except Exception:
            pass

    def animate_loader(self):
        try:
            self.loader_tick += 1
            if self.loader_popup and self.loader_popup.winfo_exists():
                self.draw_loader()
        except Exception:
            pass
        self.root.after(90, self.animate_loader)

    def show_loader_overlay(self):
        """Hiện truck loader ở giữa app bằng Frame nội bộ, không dùng Toplevel nữa.
        Bản Toplevel trước có thể bị Windows/theme đẩy ra sau nên người dùng không thấy.
        """
        try:
            if self.loader_popup and self.loader_popup.winfo_exists():
                self.position_loader_overlay()
                self.draw_loader()
                self.loader_popup.lift()
                return

            popup = tk.Frame(
                self.root,
                bg="#FFFFFF",
                highlightthickness=2,
                highlightbackground=ACCENT if ACCENT else BORDER,
                bd=0,
            )
            popup.configure(width=360, height=245)
            popup.pack_propagate(False)

            # Card shadow giả lập bằng nền viền dày, nhìn rõ hơn trên cả theme sáng/tối.
            title = tk.Label(
                popup,
                text="TOBO IS WORKING",
                bg="#FFFFFF",
                fg=TEXT if TEXT else "#111827",
                font=("Segoe UI", 11, "bold"),
            )
            title.pack(pady=(10, 0))

            self.loader_popup_canvas = tk.Canvas(popup, width=340, height=165, bg="#FFFFFF", highlightthickness=0, bd=0)
            self.loader_popup_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 0))
            self.loader_popup_label = tk.Label(
                popup,
                text=self.status.get() or "Loading...",
                bg="#FFFFFF",
                fg=TEXT_MUTED if TEXT_MUTED else "#64748B",
                font=("Segoe UI", 10, "bold"),
                wraplength=320,
            )
            self.loader_popup_label.pack(pady=(0, 10))

            self.loader_popup = popup
            self.position_loader_overlay()
            self.draw_loader()
            self.loader_popup.lift()
            self.root.update_idletasks()
        except Exception as e:
            try:
                self.status.set(f"Loader error: {e}")
            except Exception:
                pass

    def position_loader_overlay(self):
        try:
            if not (self.loader_popup and self.loader_popup.winfo_exists()):
                return
            self.loader_popup.place(relx=0.5, rely=0.52, anchor="center", width=360, height=245)
            self.loader_popup.lift()
        except Exception:
            pass

    def hide_loader_overlay(self):
        try:
            if self.loader_popup and self.loader_popup.winfo_exists():
                self.loader_popup.destroy()
        except Exception:
            pass
        self.loader_popup = None
        self.loader_popup_canvas = None
        self.loader_popup_label = None

    def rebuild_ui(self):
        try:
            self.root.configure(bg=BG_COLOR)
            for child in self.root.winfo_children():
                child.destroy()
            self.pulse_colors = [ACCENT, ACCENT_2, ACCENT_3, TEXT]
            self.sparkle_canvas = None
            self.sparkle_items = []
            self.header_status_label = None
            self.settings_panel = None
            self.loader_canvas = None
            self.hide_loader_overlay()
            self.controls_rows = []
            self.controls_collapsed = False
            self.build_ui()
            self.setup_sparkle_scene()
            self.status.set(tr("ready_status"))
        except Exception as e:
            messagebox.showerror(tr("ui_error_title"), str(e))

    def close_settings_panel(self):
        panel = getattr(self, "settings_panel", None)
        if panel is not None:
            try:
                panel.destroy()
            except Exception:
                pass
        self.settings_panel = None
        try:
            self.settings_button.configure(text="☰")
        except Exception:
            pass

    def open_settings(self):
        self.play_click()
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(tr("busy_title"), tr("busy_settings"))
            return

        if getattr(self, "settings_panel", None) is not None and self.settings_panel.winfo_exists():
            self.close_settings_panel()
            return

        current = load_ui_settings()
        panel = tk.Frame(self.shell, bg=BG_COLOR, highlightthickness=1, highlightbackground=BORDER)
        self.settings_panel = panel
        try:
            self.settings_button.configure(text="×")
        except Exception:
            pass

        pack_kwargs = {"fill": "x", "padx": 18, "pady": (0, 10)}
        if getattr(self, "main_container", None) is not None:
            pack_kwargs["before"] = self.main_container
        panel.pack(**pack_kwargs)

        wrap = tk.Frame(panel, bg=BG_COLOR)
        wrap.pack(fill="x", padx=16, pady=14)

        head = tk.Frame(wrap, bg=BG_COLOR)
        head.pack(fill="x", pady=(0, 12))
        tk.Label(head, text="☰", bg=BG_COLOR, fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(head, text=tr("settings_title"), bg=BG_COLOR, fg=TEXT, font=("Segoe UI Variable Display", 16, "bold")).pack(side="left", padx=(10, 0))
        tk.Button(
            head,
            text="×",
            command=self.close_settings_panel,
            bg=BG_COLOR,
            fg=TEXT_MUTED,
            activebackground=SURFACE_2,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=10,
            pady=2,
            cursor="hand2",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="right")

        card = tk.Frame(wrap, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x")

        grid = tk.Frame(card, bg=SURFACE)
        grid.pack(fill="x", padx=14, pady=14)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        lang_box = tk.Frame(grid, bg=SURFACE)
        lang_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(lang_box, text=tr("app_language"), bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        lang_reverse = {name: key for key, name in LANG_OPTIONS.items()}
        lang_var = tk.StringVar(value=LANG_OPTIONS.get(current.get("app_language", "vi"), "Tiếng Việt"))
        lang_combo = ttk.Combobox(lang_box, textvariable=lang_var, values=list(LANG_OPTIONS.values()), state="readonly")
        lang_combo.pack(fill="x", ipady=5)

        theme_box = tk.Frame(grid, bg=SURFACE)
        theme_box.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        tk.Label(theme_box, text=tr("theme"), bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        theme_var = tk.StringVar(value=current.get("theme", CURRENT_THEME_KEY) if current.get("theme", CURRENT_THEME_KEY) in THEME_PRESETS else CURRENT_THEME_KEY)
        theme_combo = ttk.Combobox(theme_box, textvariable=theme_var, values=list(THEME_PRESETS.keys()), state="readonly")
        theme_combo.pack(fill="x", ipady=5)

        preview = tk.Frame(card, bg=SURFACE)
        preview.pack(fill="x", padx=14, pady=(0, 12))
        labels = list(zip(["bg", "surface", "primary", "secondary", "accent", "text", "muted", "border"], tr("theme_swatches")))

        def draw_preview(*_):
            for child in preview.winfo_children():
                child.destroy()
            theme = THEME_PRESETS.get(theme_var.get()) or THEME_PRESETS[CURRENT_THEME_KEY]
            for i, (key, label) in enumerate(labels):
                box = tk.Frame(preview, bg=SURFACE)
                box.grid(row=0, column=i, sticky="ew", padx=3, pady=5)
                color = theme[key]
                tk.Label(box, text="  ", bg=color, width=3, relief="flat", highlightthickness=1, highlightbackground=BORDER).pack(side="top", anchor="w")
                tk.Label(box, text=f"{label}\n{color}", bg=SURFACE, fg=TEXT_MUTED, justify="left", font=("Segoe UI", 7)).pack(side="top", anchor="w")
            for c in range(8):
                preview.columnconfigure(c, weight=1)

        theme_combo.bind("<<ComboboxSelected>>", draw_preview)
        draw_preview()

        bottom = tk.Frame(wrap, bg=BG_COLOR)
        bottom.pack(fill="x", pady=(12, 0))
        tk.Label(bottom, text=tr("theme_note"), bg=BG_COLOR, fg=TEXT_MUTED, wraplength=620, justify="left", font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)

        def apply_settings():
            global APP_LANG
            old_source = option_value("source", self.language.get())
            old_translate = option_value("translate", self.translate_to.get())
            old_model = option_value("model", self.model_size.get()) or "large-v3-turbo"
            old_device = option_value("device", self.device_mode.get()) or "auto"
            old_style = style_value(self.translation_style.get()) if hasattr(self, "translation_style") else "natural"
            old_speed = speed_value(self.read_speed.get()) if hasattr(self, "read_speed") else "normal"
            lang_key = lang_reverse.get(lang_var.get(), "vi")
            theme_key = theme_var.get()
            save_ui_settings({"app_language": lang_key, "theme": theme_key})
            APP_LANG = lang_key
            apply_theme(theme_key)
            self.language.set(option_label("source", old_source))
            self.translate_to.set(option_label("translate", old_translate))
            self.model_size.set(option_label("model", old_model))
            self.device_mode.set(option_label("device", old_device))
            if hasattr(self, "translation_style"):
                self.translation_style.set(style_label(old_style))
            if hasattr(self, "read_speed"):
                self.read_speed.set(speed_label(old_speed))
            self.close_settings_panel()
            self.rebuild_ui()

        tk.Button(
            bottom,
            text=tr("apply"),
            command=apply_settings,
            bg=ACCENT,
            fg="#FFFFFF",
            activebackground=ACCENT_3,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="right", padx=(10, 0))
        tk.Button(
            bottom,
            text=tr("help_button"),
            command=self.open_help_window,
            bg=SURFACE,
            fg=TEXT,
            activebackground=SURFACE_2,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            highlightthickness=1,
            highlightbackground=BORDER,
        ).pack(side="right", padx=(10, 0))

    def open_help_window(self):
        self.play_click()
        win = tk.Toplevel(self.root)
        win.title(tr("help_title"))
        win.geometry("620x560")
        win.configure(bg=BG_COLOR)
        try:
            win.transient(self.root)
        except Exception:
            pass
        wrap = tk.Frame(win, bg=BG_COLOR)
        wrap.pack(fill="both", expand=True, padx=18, pady=18)
        tk.Label(wrap, text=tr("help_title"), bg=BG_COLOR, fg=TEXT, font=("Segoe UI Variable Display", 18, "bold")).pack(anchor="w", pady=(0, 10))
        body = tk.Text(
            wrap,
            wrap="word",
            bg=TEXTBOX_BG,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=12,
            pady=12,
        )
        body.pack(fill="both", expand=True)
        body.insert("1.0", tr("help_body"))
        body.configure(state="disabled")
        btns = tk.Frame(wrap, bg=BG_COLOR)
        btns.pack(fill="x", pady=(12, 0))
        tk.Button(
            btns,
            text=tr("close"),
            command=win.destroy,
            bg=ACCENT,
            fg="#FFFFFF",
            activebackground=ACCENT_3,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

    def make_card(self, parent, **pack_opts):
        outer = tk.Frame(parent, bg=BG_COLOR)
        if pack_opts:
            outer.pack(**pack_opts)
        card = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="both", expand=True, padx=1, pady=1)
        # Tkinter gốc không bo góc thật như web/CSS. Bản này làm mềm bằng padding, viền nhẹ,
        # ít góc nhọn hơn và layout đều hơn. Muốn bo góc thật nên chuyển sang PySide6/CustomTkinter.
        return card

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG, foreground=TEXT, arrowcolor=ACCENT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], foreground=[("readonly", TEXT)])
        style.configure("Horizontal.TProgressbar", thickness=12, troughcolor=BORDER, background=ACCENT, bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT)
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
            if getattr(self, "status_label", None):
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
        c.create_rectangle(0, 0, w, h, fill=SURFACE_2, outline="")
        c.create_oval(-50, -38, 132, 118, fill=BORDER, outline="")
        c.create_oval(148, -22, 330, 94, fill=BG_COLOR, outline="")
        c.create_oval(172, 44, 342, 156, fill=SURFACE, outline="")
        c.create_arc(36, 30, 270, 158, start=20, extent=142, style="arc", outline=BORDER, width=2)
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
        self.sparkle_orbit = c.create_text(238, 88, text=tr("soft_glow"), fill=ACCENT, font=("Segoe UI", 9, "bold"))

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
                    color = palette[(idx + int(self.sparkle_tick / 5)) % len(palette)] if twinkle > 0.76 else BORDER
                    self.sparkle_canvas.itemconfig(sp["item"], fill=color, outline=color)
                if self.header_status_label:
                    label = tr("soft_sparkle_active") if self.sparkle_tick % 10 < 5 else tr("mode")
                    self.header_status_label.configure(text=label)
                if hasattr(self, "sparkle_orbit"):
                    ox = 238 + math.sin(self.sparkle_tick / 8.0) * 5
                    oy = 88 + math.cos(self.sparkle_tick / 9.0) * 2
                    self.sparkle_canvas.coords(self.sparkle_orbit, ox, oy)
                    self.sparkle_canvas.itemconfig(self.sparkle_orbit, fill=palette[int(self.sparkle_tick / 6) % len(palette)])
            elif self.sparkle_canvas and self.header_status_label:
                self.header_status_label.configure(text=tr("soft_sparkle_paused"))
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
                return tr("url_404").format(purpose=purpose) + f"\n\n{tr("config_file")}: {config_path}"
            return tr("url_http").format(purpose=purpose, code=err.code, reason=err.reason) + f"\n\n{tr("config_file")}: {config_path}"
        if isinstance(err, urllib.error.URLError):
            reason = getattr(err, "reason", err)
            reason_text = str(reason)
            if isinstance(reason, socket.gaierror) or "getaddrinfo failed" in reason_text.lower():
                return tr("url_dns").format(purpose=purpose) + f"\n\n{tr("config_file")}: {config_path}"
            return tr("url_network").format(purpose=purpose, reason=reason_text) + f"\n\n{tr("config_file")}: {config_path}"
        if isinstance(err, json.JSONDecodeError):
            return tr("manifest_not_json").format(purpose=purpose)
        return tr("generic_error").format(purpose=purpose, error=err)

    def check_update(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(tr("busy_title"), tr("busy_processing"))
            return
        self.status.set(tr("checking_update"))
        threading.Thread(target=self.check_update_worker, daemon=True).start()

    def check_update_worker(self):
        try:
            cfg = self.load_update_config()
            manifest_url = (cfg.get("manifest_url") or "").strip()
            config_path = self.get_update_config_path()
            if not manifest_url:
                self.q.put(("update_info", f"manifest_url is empty.\n\nConfig file: {config_path}"))
                return
            if self.is_placeholder_url(manifest_url):
                self.q.put(("update_info", f"manifest_url is still a placeholder. Replace it with a real JSON link.\n\nCurrent link: {manifest_url}"))
                return
            if not (manifest_url.startswith("http://") or manifest_url.startswith("https://") or manifest_url.startswith("file://")):
                self.q.put(("update_info", f"Invalid manifest_url: {manifest_url}"))
                return
            try:
                req = urllib.request.Request(manifest_url, headers={"User-Agent": f"{APP_NAME}/{CURRENT_VERSION}"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    manifest = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                self.q.put(("update_info", self.explain_url_error(e, tr("update_title"))))
                return
            latest_version = str(manifest.get("version", "")).strip()
            download_url = str(manifest.get("url") or manifest.get("zip_url") or manifest.get("exe_url") or "").strip()
            notes = str(manifest.get("notes", "")).strip()
            if not latest_version or not download_url:
                raise RuntimeError("Update manifest is missing version or url/zip_url/exe_url.")
            if self.version_tuple(latest_version) <= self.version_tuple(CURRENT_VERSION):
                self.q.put(("update_info", tr("newest_version").format(version=CURRENT_VERSION)))
                return
            self.q.put(("update_available", {"version": latest_version, "url": download_url, "notes": notes}))
        except Exception as e:
            self.q.put(("update_info", f"{tr("update_title")}: {e}"))

    def download_update(self, info: dict):
        threading.Thread(target=self.download_update_worker, args=(info,), daemon=True).start()

    def download_update_worker(self, info: dict):
        try:
            version = safe_filename(info.get("version", "new"))
            url = (info.get("url") or "").strip()
            if not url:
                raise RuntimeError("Missing update download URL.")
            suffix = ".exe" if url.lower().split("?")[0].endswith(".exe") else ".zip"
            target = UPDATES_DIR / f"TOBO_VietSub_update_{version}{suffix}"
            self.q.put(("status", f"{tr("update_title")} v{version}..."))
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
                self.q.put(("update_info", self.explain_url_error(e, tr("update_title"))))
                return
            self.q.put(("progress", 100))
            if suffix == ".zip":
                self.q.put(("update_ready_to_apply", str(target)))
            else:
                self.q.put(("update_downloaded", str(target)))
        except Exception as e:
            self.q.put(("update_info", f"{tr("update_title")}: {e}"))

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
            messagebox.showerror(tr("update_title"), "Missing tobo_update_helper.py")
            return

        py_cmd = self.find_update_python()
        if not py_cmd:
            messagebox.showinfo(
                tr("update_title"),
                tr("python_missing_update")
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
                tr("update_title"),
                tr("update_ready_apply")
            )
            self.root.after(500, self.root.destroy)
        except Exception as e:
            messagebox.showerror(tr("update_title"), f"{e}")

    def default_background_config_text(self) -> str:
        return json.dumps(
            {
                "enabled": True,
                "video_url": "",
                "cache_file": "assets/support_coffee.mp4",
                "max_frames": 120,
                "width": 304,
                "height": 112,
                "fps": 12,
                "note": "Header video clip for the TOBO support/coffee panel."
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
        if not self.video_bg_label:
            return
        threading.Thread(target=self.video_background_worker, daemon=True).start()

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
                img = ImageEnhance.Brightness(img).enhance(0.88)
                img = ImageEnhance.Contrast(img).enhance(1.08)
                overlay = Image.new("RGB", img.size, (255, 247, 237))
                img = Image.blend(img, overlay, 0.06)
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
            title=tr("pick_title"),
            filetypes=[("Media files", AUDIO_VIDEO_EXTENSIONS), ("All files", "*.*")],
        )
        if path:
            self.selected_file.set(path)

    def log(self, msg):
        self.q.put(("status", msg))

    def iter_interactive_widgets(self, parent=None):
        parent = parent or self.root
        for child in parent.winfo_children():
            if isinstance(child, (tk.Button, tk.Checkbutton, tk.Entry, ttk.Combobox)):
                yield child
            yield from self.iter_interactive_widgets(child)

    def set_interaction_locked(self, locked: bool):
        self.ui_locked = bool(locked)
        for widget in self.iter_interactive_widgets():
            try:
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="disabled" if locked else "readonly")
                else:
                    widget.configure(state="disabled" if locked else "normal")
            except Exception:
                pass

    def begin_busy(self, message: str, progress: float = 5):
        self.status.set(message)
        self.progress.set(progress)
        self.set_interaction_locked(True)
        self.show_loader_overlay()
        self.root.update_idletasks()

    def end_busy(self, message: str | None = None, progress: float | None = None):
        if progress is not None:
            self.progress.set(progress)
        if message:
            self.status.set(message)
        self.set_interaction_locked(False)
        self.hide_loader_overlay()
        self.root.update_idletasks()

    def check_system(self):
        if self.ui_locked or (self.worker and self.worker.is_alive()):
            return
        self.play_click()
        self.begin_busy(tr("system_check_running"), 8)
        threading.Thread(target=self.check_system_worker, daemon=True).start()

    def check_system_worker(self):
        lines = []
        def ok(name, detail=""):
            lines.append(f"✅ {name} OK" + (f" — {detail}" if detail else ""))
        def bad(name, detail=""):
            lines.append(f"❌ {name}" + (f" — {detail}" if detail else ""))

        ok("Python", sys.version.split()[0])
        try:
            import faster_whisper
            ok("faster-whisper", getattr(faster_whisper, "__version__", "installed"))
        except Exception as e:
            bad("faster-whisper", str(e))

        if check_ffmpeg():
            ok("FFmpeg")
        else:
            bad("FFmpeg", "chưa thấy trong PATH/local folder")

        try:
            import huggingface_hub
            cache_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
            model_hint = "cache folder exists" if cache_home.exists() else "cache folder not found yet"
            ok("Model cache", model_hint)
        except Exception as e:
            bad("Model cache", str(e))

        try:
            urllib.request.urlopen(urllib.request.Request("https://github.com", headers={"User-Agent": APP_NAME}), timeout=8).close()
            ok("Internet")
        except Exception as e:
            bad("Internet", str(e))

        try:
            import ctranslate2
            cuda_count = 0
            if hasattr(ctranslate2, "get_cuda_device_count"):
                cuda_count = ctranslate2.get_cuda_device_count()
            if cuda_count:
                ok("GPU/CUDA", f"{cuda_count} CUDA device(s)")
            else:
                bad("GPU/CUDA", "không phát hiện CUDA, CPU vẫn chạy được")
        except Exception as e:
            bad("GPU/CUDA", str(e))

        try:
            OUTPUT_DIR.mkdir(exist_ok=True)
            test = OUTPUT_DIR / ".write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
            ok("Thư mục output", str(OUTPUT_DIR))
        except Exception as e:
            bad("Thư mục output", str(e))

        self.q.put(("system_check_result", "\n".join(lines)))

    def safe_float(self, value, default: float) -> float:
        try:
            return float(str(value).strip().replace(",", "."))
        except Exception:
            return default

    def apply_cartoon_mode(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(tr("busy_title"), tr("busy_processing"))
            return
        try:
            self.translation_style.set(style_label("cartoon_movie"))
            self.read_speed.set(speed_label("normal"))
            self.delay_min.set("0.15")
            self.delay_max.set("2.00")
            self.delay_round.set("0.05")
            if hasattr(self, "srt_max_lines"):
                self.srt_max_lines.set("2")
            self.delay_skip_small.set(True)
            self.delay_tags_enabled.set(True)
            self.status.set(tr("cartoon_applied"))
            if self.controls_collapsed:
                self.toggle_controls_panel()
        except Exception as e:
            messagebox.showerror(tr("ui_error_title"), str(e))

    def wrap_srt_text(self, text: str, max_lines: int = 0, max_chars: int = 42) -> str:
        text = " ".join((text or "").split()).strip()
        if not text or max_lines <= 0:
            return text
        max_lines = max(1, int(max_lines))
        max_chars = max(12, int(max_chars))
        # CJK text has no spaces; split by character chunks.
        cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u30ff" or "\uac00" <= ch <= "\ud7af")
        if cjk >= max(2, len(text.replace(" ", "")) * 0.45):
            chunk = 18
            parts = [text[i:i+chunk] for i in range(0, len(text), chunk)]
        else:
            words = text.split()
            parts = []
            current = ""
            for word in words:
                candidate = (current + " " + word).strip()
                if current and len(candidate) > max_chars:
                    parts.append(current)
                    current = word
                else:
                    current = candidate
            if current:
                parts.append(current)
        if len(parts) <= max_lines:
            return "\n".join(parts)
        # Keep max line count by merging overflow into the last line.
        kept = parts[:max_lines-1]
        kept.append(" ".join(parts[max_lines-1:]))
        return "\n".join(kept)

    def start(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(tr("busy_title"), tr("busy_processing"))
            return
        file_path = self.selected_file.get().strip()
        if not file_path or not Path(file_path).exists():
            messagebox.showerror(tr("missing_file_title"), tr("missing_file_message"))
            return
        settings = {
            "model_name": option_value("model", self.model_size.get()) or "large-v3-turbo",
            "device_choice": option_value("device", self.device_mode.get()) or "auto",
            "source_lang": option_value("source", self.language.get()),
            "target_lang": option_value("translate", self.translate_to.get()),
            "export_format": EXPORT_FORMATS[self.export_format.get()],
            "delay_tags_enabled": bool(self.delay_tags_enabled.get()),
            "translation_style": style_value(self.translation_style.get()),
            "translation_style_label": self.translation_style.get(),
            "output_folder_name": self.output_folder_name.get().strip(),
            "read_speed": speed_value(self.read_speed.get()),
            "delay_min": self.safe_float(self.delay_min.get(), 0.10),
            "delay_max": self.safe_float(self.delay_max.get(), 2.50),
            "delay_round": self.safe_float(self.delay_round.get(), 0.05),
            "srt_max_lines": int(self.safe_float(self.srt_max_lines.get(), 0)) if hasattr(self, "srt_max_lines") else 0,
            "delay_skip_small": bool(self.delay_skip_small.get()),
        }
        self.begin_busy(tr("preparing"), 3)
        self.text_original.delete("1.0", "end")
        self.text_translated.delete("1.0", "end")
        self.last_text = ""
        self.last_translation = ""
        self.last_clean_translation = ""
        self.last_timed_translation = ""
        self.last_rows = []
        self.last_translated_rows = []
        self.worker = threading.Thread(target=self.process_file, args=(Path(file_path), settings), daemon=True)
        self.worker.start()

    def turbo_model_candidates(self, model_name: str) -> list[str]:
        if model_name == "large-v3-turbo":
            # Try the short alias first. If the installed faster-whisper build does not know it,
            # fall back to public CTranslate2 conversions on Hugging Face.
            return [
                "large-v3-turbo",
                "h2oai/faster-whisper-large-v3-turbo",
                "deepdml/faster-whisper-large-v3-turbo-ct2",
            ]
        return [model_name]

    def load_whisper_candidate(self, WhisperModel, candidates: list[str], device: str, compute_type: str):
        last_error = None
        for candidate in candidates:
            try:
                if candidate != candidates[0]:
                    self.log(f"Turbo alias lỗi, thử model thay thế: {candidate}")
                return WhisperModel(candidate, device=device, compute_type=compute_type)
            except Exception as e:
                last_error = e
        raise last_error

    def create_model(self, model_name: str, device_choice: str):
        from faster_whisper import WhisperModel
        candidates = self.turbo_model_candidates(model_name)
        if device_choice == "gpu":
            try:
                return self.load_whisper_candidate(WhisperModel, candidates, device="cuda", compute_type="float16")
            except Exception as e:
                self.log(tr("gpu_failed").format(error=e))
                return self.load_whisper_candidate(WhisperModel, candidates, device="cpu", compute_type="int8")
        if device_choice == "cpu":
            return self.load_whisper_candidate(WhisperModel, candidates, device="cpu", compute_type="int8")
        try:
            return self.load_whisper_candidate(WhisperModel, candidates, device="auto", compute_type="auto")
        except Exception as e:
            self.log(tr("auto_device_failed").format(error=e))
            return self.load_whisper_candidate(WhisperModel, candidates, device="cpu", compute_type="int8")

    def transcribe_source(self, model, media_path: Path, lang: str | None):
        segments, info = model.transcribe(str(media_path), language=lang, beam_size=5, vad_filter=True, word_timestamps=False)
        duration = float(getattr(info, "duration", 0) or 0)
        detected_language = getattr(info, "language", None)
        self.log(tr("detected_lang").format(lang=detected_language) if detected_language else tr("transcribing"))
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
            self.log(tr("loading_model"))
            model = self.create_model(settings["model_name"], settings["device_choice"])
            rows = None
            direct_error = None
            try:
                self.q.put(("progress", 18))
                self.log(tr("reading_media"))
                rows = self.transcribe_source(model, input_file, settings["source_lang"])
            except Exception as e:
                direct_error = e
                self.q.put(("clear_original", None))
                self.log(tr("direct_read_failed"))
            if rows is None:
                if not check_ffmpeg():
                    raise RuntimeError(tr("ffmpeg_missing").format(error=direct_error))
                audio_path = TEMP_DIR / f"{safe_filename(input_file.stem)}_{int(time.time())}.wav"
                extract_audio(input_file, audio_path, self.log)
                self.q.put(("progress", 22))
                rows = self.transcribe_source(model, audio_path, settings["source_lang"])

            self.last_rows = rows
            original_text = "\n".join(self.format_segment_line(row, row["text"]) for row in rows)
            self.last_text = original_text
            safe_stem = safe_filename(input_file.stem)
            export_format = settings["export_format"]
            export_dir = self.resolve_export_dir(settings.get("output_folder_name", ""))
            written_files = []

            if export_format in ("txt", "both"):
                out_txt = export_dir / f"{safe_stem}_transcript.txt"
                out_txt.write_text(original_text, encoding="utf-8")
                written_files.append(str(out_txt.relative_to(OUTPUT_DIR)) if out_txt.is_relative_to(OUTPUT_DIR) else out_txt.name)

            if export_format in ("srt", "both"):
                out_srt = export_dir / f"{safe_stem}_transcript.srt"
                out_srt.write_text(self.rows_to_srt(rows, max_lines=settings.get("srt_max_lines", 0)), encoding="utf-8-sig")
                written_files.append(str(out_srt.relative_to(OUTPUT_DIR)) if out_srt.is_relative_to(OUTPUT_DIR) else out_srt.name)

            self.q.put(("progress", 88))
            self.log(tr("exported").format(files=", ".join(written_files)) if written_files else tr("transcribed_done"))

            target_lang = settings["target_lang"]
            if target_lang:
                self.log(tr("translating_clean"))
                translated_rows = self.translate_rows(rows, target_lang, settings.get("translation_style", "natural"))
                self.last_translated_rows = translated_rows
                clean_translation = "\n".join(row["text"] for row in translated_rows if row.get("text"))
                self.last_clean_translation = clean_translation
                display_translation = clean_translation

                if settings.get("delay_tags_enabled", True):
                    self.log(tr("translating_timed"))
                    timed_translation = self.rows_to_voice_timing_text(
                        translated_rows,
                        target_lang,
                        speed=settings.get("read_speed", "normal"),
                        min_delay=settings.get("delay_min", 0.10),
                        max_delay=settings.get("delay_max", 2.50),
                        round_step=settings.get("delay_round", 0.05),
                        skip_under=0.2 if settings.get("delay_skip_small", True) else 0.10,
                    )
                    self.last_timed_translation = timed_translation
                    display_translation = timed_translation
                else:
                    self.last_timed_translation = ""

                self.last_translation = display_translation
                self.q.put(("set_translation", display_translation))

                if export_format in ("txt", "both"):
                    trans_txt = export_dir / f"{safe_stem}_translated_{target_lang.replace('-', '_')}.txt"
                    trans_txt.write_text(clean_translation, encoding="utf-8")
                    written_files.append(str(trans_txt.relative_to(OUTPUT_DIR)) if trans_txt.is_relative_to(OUTPUT_DIR) else trans_txt.name)
                    if self.last_timed_translation:
                        voice_txt = export_dir / f"{safe_stem}_translated_{target_lang.replace('-', '_')}_{tr('voice_file_suffix')}.txt"
                        voice_txt.write_text(self.last_timed_translation, encoding="utf-8")
                        written_files.append(str(voice_txt.relative_to(OUTPUT_DIR)) if voice_txt.is_relative_to(OUTPUT_DIR) else voice_txt.name)
                if export_format in ("srt", "both"):
                    trans_srt = export_dir / f"{safe_stem}_translated_{target_lang.replace('-', '_')}.srt"
                    trans_srt.write_text(self.rows_to_srt(translated_rows, max_lines=settings.get("srt_max_lines", 0)), encoding="utf-8-sig")
                    written_files.append(str(trans_srt.relative_to(OUTPUT_DIR)) if trans_srt.is_relative_to(OUTPUT_DIR) else trans_srt.name)

            self.q.put(("progress", 100))
            done_msg = tr("done_message")
            if written_files:
                done_msg += "\n\n" + tr("exported_list") + ":\n- " + "\n- ".join(written_files)
            self.q.put(("done", done_msg))
        except Exception as e:
            self.q.put(("error", str(e)))
        finally:
            if audio_path:
                try:
                    audio_path.unlink(missing_ok=True)
                except Exception:
                    pass

    def resolve_export_dir(self, folder_name: str) -> Path:
        name = safe_filename((folder_name or "").strip())
        if not name:
            target = OUTPUT_DIR
        else:
            target = OUTPUT_DIR / name
        target.mkdir(parents=True, exist_ok=True)
        return target

    def stylize_translation_text(self, text: str, style_code: str, target_lang: str) -> str:
        raw = (text or "").strip()
        if not raw:
            return raw
        if style_code in ("", None, "faithful"):
            # Giữ nghĩa sát: không thêm thắt, chỉ dọn khoảng trắng.
            return " ".join(raw.split())

        lang = "vi" if target_lang == "vi" else ("zh" if target_lang in {"zh", "zh-CN"} else target_lang)
        end_punct = raw.endswith((".", "!", "?", "…", "。", "！", "？", "~"))

        def finish(s: str, punct: str = ".") -> str:
            s = " ".join((s or "").split()).strip()
            if not s:
                return s
            return s if s.endswith((".", "!", "?", "…", "。", "！", "？", "~")) else s + punct

        def apply_replacements(s: str, pairs: list[tuple[str, str]]) -> str:
            out = s
            for a, b in pairs:
                out = out.replace(a, b).replace(a.capitalize(), b.capitalize())
            return out

        if lang == "vi":
            replacement_map = {
                "natural": [
                    ("tôi là", "mình là"), ("tại sao", "sao"), ("được rồi", "được rồi"),
                    ("không thể", "không thể"), ("xin chào", "chào"),
                ],
                "viral_tiktok": [
                    ("tại sao", "ủa sao"), ("không thể", "không thể nào"), ("được rồi", "ok luôn"),
                    ("thật sao", "thật luôn á"), ("xin chào", "hello nha"),
                ],
                "cartoon_movie": [
                    ("tại sao", "sao vậy ta"), ("không", "không nha"), ("được rồi", "được rồi nè"),
                    ("chạy", "chạy lẹ lên"), ("xin chào", "hí lô"),
                ],
                "dubbing": [
                    ("tôi", "ta"), ("bạn", "ngươi"), ("được rồi", "rõ rồi"),
                    ("không thể", "không được"),
                ],
                "silly_fun": [
                    ("không", "không nha trời"), ("tại sao", "sao kỳ vậy trời"),
                    ("được rồi", "ok luôn, khỏi căng"), ("xin chào", "hí lô bà con"),
                ],
                "polite": [
                    ("tôi", "tôi"), ("mày", "bạn"), ("tao", "tôi"), ("ừ", "vâng"),
                    ("ok", "được"), ("không", "không ạ"),
                ],
                "native": [
                    ("tại sao", "sao"), ("không phải", "đâu phải"), ("được rồi", "rồi, được"),
                    ("bạn có thể", "bạn thử"), ("xin chào", "chào"),
                ],
            }
            out = apply_replacements(raw, replacement_map.get(style_code, []))
            if style_code == "natural":
                return finish(out, ".") if not end_punct else out
            if style_code == "viral_tiktok":
                return finish(out, "!")
            if style_code == "cartoon_movie":
                return out if out.endswith(("nè!", "nha!", "!", "?", "~")) else out + " nha!"
            if style_code == "dubbing":
                return finish(out, "!") if len(out) <= 38 else finish(out, ".")
            if style_code == "silly_fun":
                return finish(out, "!")
            if style_code == "polite":
                if not out.endswith(("ạ.", "ạ!", "ạ?", ".", "!", "?")) and len(out) < 70:
                    out += " ạ"
                return finish(out, ".")
            if style_code == "native":
                return finish(out, ".") if len(out) > 18 else finish(out, "!")
            return out

        # Với ngôn ngữ khác: giữ an toàn, chỉ chỉnh nhịp/punctuation nhẹ để không làm méo nghĩa.
        if style_code == "natural":
            return finish(raw, ".")
        if style_code == "viral_tiktok":
            return finish(raw, "!")
        if style_code in ("cartoon_movie", "silly_fun"):
            return finish(raw, "!")
        if style_code == "dubbing":
            return finish(raw, "!") if len(raw) < 42 else finish(raw, ".")
        if style_code == "polite":
            return finish(raw, ".")
        if style_code == "native":
            return finish(raw, ".")
        return raw

    def format_segment_line(self, row: dict, text: str) -> str:
        return f"[{format_timestamp(row['start'])} → {format_timestamp(row['end'])}] {text.strip()}"

    def rows_to_srt(self, rows: list[dict], max_lines: int = 0) -> str:
        blocks = []
        for idx, row in enumerate(rows, start=1):
            text = (row.get("text") or "").strip()
            if not text:
                continue
            text = self.wrap_srt_text(text, max_lines=max_lines)
            blocks.append(f"{idx}\n{format_srt_timestamp(row.get('start', 0))} --> {format_srt_timestamp(row.get('end', 0))}\n{text}")
        return "\n\n".join(blocks) + ("\n" if blocks else "")

    def estimate_tts_seconds(self, text: str, target_lang: str | None = None, speed: str = "normal") -> float:
        clean = (text or "").strip()
        if not clean:
            return 0.0
        cjk_chars = sum(1 for ch in clean if "\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u30ff" or "\uac00" <= ch <= "\ud7af")
        compact_len = len(clean.replace(" ", ""))
        if cjk_chars >= max(2, compact_len * 0.45) or target_lang in {"zh", "zh-CN", "ja", "ko"}:
            base = max(0.45, max(1, cjk_chars) / 4.2)
        else:
            words = [w for w in clean.replace("\n", " ").split(" ") if w.strip()]
            base = max(0.55, len(words) / 2.65)
        punctuation_pause = sum(clean.count(ch) for ch in ",.;:!?，。！？、") * 0.10
        result = min(20.0, base + punctuation_pause)
        factor = {"slow": 1.25, "normal": 1.0, "fast": 0.82}.get(speed, 1.0)
        return result * factor

    def rows_to_voice_timing_text(self, rows: list[dict], target_lang: str | None = None, speed: str = "normal", min_delay: float = 0.10, max_delay: float = 2.50, round_step: float = 0.05, skip_under: float = 0.20) -> str:
        lines = []
        if not rows:
            return ""
        first_start = max(0.0, float(rows[0].get("start", 0) or 0))
        round_step = max(0.01, float(round_step or 0.05))
        min_delay = max(0.0, float(min_delay or 0.0))
        max_delay = max(min_delay, float(max_delay or 2.5))
        skip_under = max(0.0, float(skip_under or 0.0))

        def clean_delay(value: float) -> float:
            value = max(min_delay, min(max_delay, value))
            return round(value / round_step) * round_step

        if first_start >= skip_under:
            lines.append(f"<#{clean_delay(first_start):.2f}#>")
        for idx, row in enumerate(rows):
            text = (row.get("text") or "").strip()
            if not text:
                continue
            start = float(row.get("start", 0) or 0)
            end = max(start, float(row.get("end", start) or start))
            segment_duration = max(0.0, end - start)
            next_start = None
            for nxt in rows[idx + 1:]:
                if (nxt.get("text") or "").strip():
                    next_start = float(nxt.get("start", end) or end)
                    break
            gap_to_next = max(0.0, (next_start - end) if next_start is not None else 0.0)
            estimated_speech = self.estimate_tts_seconds(text, target_lang, speed=speed)
            delay = max(0.0, segment_duration - estimated_speech) + gap_to_next
            if delay >= skip_under:
                lines.append(f"{text}<#{clean_delay(delay):.2f}#>")
            else:
                lines.append(text)
        return "\n".join(lines)

    def translate_rows(self, rows: list[dict], target_lang: str, style_code: str = "natural") -> list[dict]:
        try:
            from deep_translator import GoogleTranslator
        except Exception:
            raise RuntimeError(tr("missing_translate_lib"))
        if not rows:
            return []
        translator = GoogleTranslator(source="auto", target=target_lang)
        if style_code and style_code != "natural":
            self.log(tr("style_applied_status").format(style=style_label(style_code)))
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
            self.log(tr("translating_part").format(i=i, total=len(chunks)))
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
            styled_text = self.stylize_translation_text(translated_texts[idx] or row["text"], style_code, target_lang)
            translated_rows.append({"start": row["start"], "end": row["end"], "text": styled_text})
        return translated_rows

    def poll_queue(self):
        try:
            while True:
                typ, value = self.q.get_nowait()
                if typ == "status":
                    self.status.set(value)
                elif typ == "progress":
                    self.progress.set(value)
                    if self.ui_locked or (self.worker and self.worker.is_alive()):
                        self.show_loader_overlay()
                    else:
                        self.hide_loader_overlay()
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
                        self.animate_video_background()
                    except Exception as e:
                        if self.video_bg_status:
                            self.video_bg_status.configure(text=f"Lỗi render nền: {e}")
                elif typ == "update_info":
                    self.end_busy(tr("ready_status"))
                    messagebox.showinfo(tr("update_title"), value)
                elif typ == "update_available":
                    self.status.set(tr("update_available_title"))
                    msg = tr("update_available_msg").format(version=value.get("version"), notes=value.get("notes") or "")
                    if messagebox.askyesno(tr("update_available_title"), msg):
                        self.download_update(value)
                elif typ == "update_ready_to_apply":
                    self.status.set(tr("update_downloaded_title"))
                    if messagebox.askyesno(
                        tr("update_title"),
                        tr("update_ready_apply")
                    ):
                        self.apply_update_zip(value)
                    else:
                        try:
                            os.startfile(str(UPDATES_DIR))
                        except Exception:
                            pass
                elif typ == "update_downloaded":
                    self.status.set(tr("update_downloaded_title"))
                    messagebox.showinfo(tr("update_downloaded_title"), tr("update_downloaded_msg").format(path=value))
                    try:
                        os.startfile(str(UPDATES_DIR))
                    except Exception:
                        pass
                elif typ == "system_check_result":
                    self.end_busy(tr("system_check_done"), 100)
                    messagebox.showinfo(tr("system_check_title"), value)
                elif typ == "done":
                    self.end_busy(tr("completed"), 100)
                    messagebox.showinfo(tr("completed"), value)
                elif typ == "error":
                    self.end_busy(tr("error_title") if tr("error_title") != "error_title" else "Error")
                    messagebox.showerror(tr("error_title") if tr("error_title") != "error_title" else "Error", value)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)

    def save_text(self):
        original = self.text_original.get("1.0", "end").strip()
        translated = self.text_translated.get("1.0", "end").strip()
        if not original and not translated:
            messagebox.showinfo(tr("no_data_title"), tr("no_text_to_save"))
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if not path:
            return
        self.begin_busy("Đang lưu TXT...", 20)
        try:
            content = original
            if translated:
                content += "\n\n===== BẢN DỊCH =====\n\n" + translated
            Path(path).write_text(content, encoding="utf-8")
            self.end_busy(tr("ready_status"), 100)
            messagebox.showinfo(tr("saved_title"), path)
        except Exception as e:
            self.end_busy(tr("ready_status"))
            messagebox.showerror(tr("error_title") if tr("error_title") != "error_title" else "Error", str(e))

    def save_srt_manual(self):
        if self.ui_locked:
            return
        rows = self.last_translated_rows if self.last_translated_rows else self.last_rows
        if not rows:
            messagebox.showinfo(tr("no_data_title"), tr("no_srt_data"))
            return
        path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT", "*.srt")])
        if not path:
            return
        self.begin_busy("Đang xuất SRT...", 20)
        try:
            Path(path).write_text(self.rows_to_srt(rows, max_lines=int(self.safe_float(self.srt_max_lines.get(), 0)) if hasattr(self, "srt_max_lines") else 0), encoding="utf-8-sig")
            self.end_busy(tr("ready_status"), 100)
            messagebox.showinfo(tr("saved_srt_title"), path)
        except Exception as e:
            self.end_busy(tr("ready_status"))
            messagebox.showerror(tr("error_title") if tr("error_title") != "error_title" else "Error", str(e))

    def save_voice_timing_manual(self):
        if self.ui_locked:
            return
        content = self.last_timed_translation.strip() if self.last_timed_translation else ""
        if not content:
            rows = self.last_translated_rows if self.last_translated_rows else []
            if rows:
                content = self.rows_to_voice_timing_text(
                    rows,
                    None,
                    speed=speed_value(self.read_speed.get()) if hasattr(self, "read_speed") else "normal",
                    min_delay=self.safe_float(self.delay_min.get(), 0.10) if hasattr(self, "delay_min") else 0.10,
                    max_delay=self.safe_float(self.delay_max.get(), 2.50) if hasattr(self, "delay_max") else 2.50,
                    round_step=self.safe_float(self.delay_round.get(), 0.05) if hasattr(self, "delay_round") else 0.05,
                    skip_under=0.2 if (hasattr(self, "delay_skip_small") and self.delay_skip_small.get()) else 0.10,
                )
        if not content:
            messagebox.showinfo(tr("no_data_title"), tr("no_voice_data"))
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if not path:
            return
        self.begin_busy("Đang xuất Voice TXT...", 20)
        try:
            Path(path).write_text(content, encoding="utf-8")
            self.end_busy(tr("ready_status"), 100)
            messagebox.showinfo(tr("saved_voice_title"), path)
        except Exception as e:
            self.end_busy(tr("ready_status"))
            messagebox.showerror(tr("error_title") if tr("error_title") != "error_title" else "Error", str(e))

    def open_output(self):
        target = self.resolve_export_dir(self.output_folder_name.get().strip()) if hasattr(self, "output_folder_name") and self.output_folder_name.get().strip() else OUTPUT_DIR
        target.mkdir(exist_ok=True)
        try:
            os.startfile(str(target))
        except Exception:
            messagebox.showinfo(tr("output_folder"), str(target))

    def show_support_qr(self):
        win = tk.Toplevel(self.root)
        win.title("Ủng hộ TOBO VietSub")
        win.geometry("420x520")
        win.minsize(380, 460)
        win.configure(bg=SURFACE)
        try:
            win.iconphoto(True, self._icon_photo)
        except Exception:
            pass

        tk.Label(
            win,
            text="☕ Please support me",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI Variable Display", 18, "bold"),
        ).pack(anchor="w", padx=22, pady=(22, 4))
        tk.Label(
            win,
            text="Bạn có thể đặt mã QR vào file assets/support_qr.png. Bản sau chỉ cần thay ảnh QR là nút này tự hiện.",
            bg=SURFACE,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=360,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=22, pady=(0, 16))

        qr_box = tk.Frame(win, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        qr_box.pack(fill="both", expand=True, padx=22, pady=(0, 16))

        qr_path = APP_DIR / "assets" / "support_qr.png"
        bundled_qr = BUNDLE_DIR / "assets" / "support_qr.png"
        if not qr_path.exists() and bundled_qr.exists():
            qr_path = bundled_qr

        self.support_qr_image = None
        if qr_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(qr_path).convert("RGBA")
                img.thumbnail((300, 300))
                self.support_qr_image = ImageTk.PhotoImage(img)
                tk.Label(qr_box, image=self.support_qr_image, bg=CARD, bd=0).pack(expand=True)
            except Exception as e:
                tk.Label(qr_box, text=f"Không đọc được QR:\n{e}", bg=CARD, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(expand=True)
        else:
            canvas = tk.Canvas(qr_box, width=260, height=260, bg=CARD, highlightthickness=0)
            canvas.pack(expand=True)
            canvas.create_rectangle(28, 28, 232, 232, outline=BORDER, width=2)
            canvas.create_text(130, 112, text="QR", fill=TEXT, font=("Segoe UI", 36, "bold"))
            canvas.create_text(130, 154, text="assets/support_qr.png", fill=TEXT_MUTED, font=("Segoe UI", 10))

        bottom = tk.Frame(win, bg=SURFACE)
        bottom.pack(fill="x", padx=22, pady=(0, 20))
        NeonButton(bottom, "Đóng", win.destroy, variant="ghost", sound_callback=self.play_click).pack(side="right")

    def open_updates_folder(self):
        UPDATES_DIR.mkdir(exist_ok=True)
        try:
            os.startfile(str(UPDATES_DIR))
        except Exception:
            messagebox.showinfo(tr("updates_folder"), str(UPDATES_DIR))

    def clear_text(self):
        self.text_original.delete("1.0", "end")
        self.text_translated.delete("1.0", "end")
        self.last_text = ""
        self.last_translation = ""
        self.last_clean_translation = ""
        self.last_timed_translation = ""
        self.last_rows = []
        self.last_translated_rows = []
        self.progress.set(0)
        self.status.set(tr("ready_status"))


def main():
    root = tk.Tk()
    TOBOVietSubApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
