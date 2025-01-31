import customtkinter as ctk
import os
import json
from tkinter import filedialog, messagebox
from wand.image import Image
from wand.color import Color

class Localization:
    TRANSLATIONS = {
        "en": {
            # Settings tab
            "settings": "Settings",
            "appearance": "Appearance",
            "language": "Language",
            "theme_light": "Light",
            "theme_dark": "Dark",
            "save_settings": "Save Settings",
            "settings_saved": "Settings saved successfully!",
            # Convert tab
            "convert": "Convert",
            "select_files": "Select files or folder",
            "browse": "Browse",
            "conversion_format": "Conversion format",
            "convert_btn": "Convert",
            "success": "Success",
            "error": "Error",
            "select_folder": "Select folder? (No - select files)",
            "select_images": "Select images",
            "select_save_folder": "Select folder to save",
            "no_images": "No images to convert!",
            "conversion_complete": "Conversion complete!",
            "conversion_error": "Conversion error for {}: {}",
            # Merge tab
            "merge": "Merge",
            "merge_direction": "Merge direction",
            "horizontal": "Horizontal",
            "vertical": "Vertical",
            "add_range": "Add Range",
            "image": "Image",
            "to": "to",
            "delete": "Delete",
            "merge_btn": "Merge",
            "no_merge_images": "No images to merge!",
            "invalid_range": "Invalid range for image {}!",
            "no_range_images": "No images in range {}!",
            "loading_error": "Error loading images: {}",
            "saving_error": "Error saving image {}: {}",
            "merge_complete": "Merge complete!",
            # About section
            "about": "About",
            "version": "Version",
            "github": "GitHub Repository",
            "github_link": "Open in browser",
            "visible_formats": "Visible Formats",
            "merge_output_format": "Merge Output Format",
        },
        "ru": {
            # Settings tab
            "settings": "Настройки",
            "appearance": "Внешний вид",
            "language": "Язык",
            "theme_light": "Светлая",
            "theme_dark": "Тёмная",
            "save_settings": "Сохранить настройки",
            "settings_saved": "Настройки успешно сохранены!",
            # Convert tab
            "convert": "Конвертация",
            "select_files": "Выберите папку или файлы",
            "browse": "Обзор",
            "conversion_format": "Формат конвертации",
            "convert_btn": "Конвертировать",
            "success": "Успех",
            "error": "Ошибка",
            "select_folder": "Выбрать папку? (Нет - выбрать файлы)",
            "select_images": "Выберите изображения",
            "select_save_folder": "Выберите папку для сохранения",
            "no_images": "Нет изображений для конвертации!",
            "conversion_complete": "Конвертация завершена!",
            "conversion_error": "Ошибка конвертации {}: {}",
            # Merge tab
            "merge": "Склеивание",
            "merge_direction": "Направление склеивания",
            "horizontal": "Горизонтально",
            "vertical": "Вертикально",
            "add_range": "Добавить диапазон",
            "image": "Изображение",
            "to": "до",
            "delete": "Удалить",
            "merge_btn": "Склеить",
            "no_merge_images": "Нет изображений для склеивания!",
            "invalid_range": "Некорректный диапазон для изображения {}!",
            "no_range_images": "Нет изображений в диапазоне {}!",
            "loading_error": "Ошибка загрузки изображений: {}",
            "saving_error": "Ошибка сохранения изображения {}: {}",
            "merge_complete": "Склеивание завершено!",
            # About section
            "about": "О программе",
            "version": "Версия",
            "github": "Репозиторий GitHub",
            "github_link": "Открыть в браузере",
            "visible_formats": "Видимые форматы",
            "merge_output_format": "Формат склеивания",
        },
        "zh": {
            # Settings tab
            "settings": "设置",
            "appearance": "外观",
            "language": "语言",
            "theme_light": "浅色",
            "theme_dark": "深色",
            "save_settings": "保存设置",
            "settings_saved": "设置保存成功！",
            # Convert tab
            "convert": "转换",
            "select_files": "选择文件或文件夹",
            "browse": "浏览",
            "conversion_format": "转换格式",
            "convert_btn": "转换",
            "success": "成功",
            "error": "错误",
            "select_folder": "选择文件夹？（否 - 选择文件）",
            "select_images": "选择图片",
            "select_save_folder": "选择保存文件夹",
            "no_images": "没有图片可转换！",
            "conversion_complete": "转换完成！",
            "conversion_error": "{} 转换错误：{}",
            # Merge tab
            "merge": "合并",
            "merge_direction": "合并方向",
            "horizontal": "水平",
            "vertical": "垂直",
            "add_range": "添加范围",
            "image": "图片",
            "to": "到",
            "delete": "删除",
            "merge_btn": "合并",
            "no_merge_images": "没有图片可合并！",
            "invalid_range": "图片 {} 的范围无效！",
            "no_range_images": "范围 {} 中没有图片！",
            "loading_error": "加载图片错误：{}",
            "saving_error": "保存图片 {} 错误：{}",
            "merge_complete": "合并完成！",
            # About section
            "about": "关于",
            "version": "版本",
            "github": "GitHub 仓库",
            "github_link": "在浏览器中打开",
            "visible_formats": "可见格式",
            "merge_output_format": "合并输出格式"
        },
        "ja": {
            # Settings tab
            "settings": "設定",
            "appearance": "外観",
            "language": "言語",
            "theme_light": "ライト",
            "theme_dark": "ダーク",
            "save_settings": "設定を保存",
            "settings_saved": "設定が保存されました！",
            # Convert tab
            "convert": "変換",
            "select_files": "ファイルまたはフォルダを選択",
            "browse": "参照",
            "conversion_format": "変換形式",
            "convert_btn": "変換",
            "success": "成功",
            "error": "エラー",
            "select_folder": "フォルダを選択？（いいえ - ファイルを選択）",
            "select_images": "画像を選択",
            "select_save_folder": "保存フォルダを選択",
            "no_images": "変換する画像がありません！",
            "conversion_complete": "変換が完了しました！",
            "conversion_error": "{} の変換エラー：{}",
            # Merge tab
            "merge": "結合",
            "merge_direction": "結合方向",
            "horizontal": "水平",
            "vertical": "垂直",
            "add_range": "範囲を追加",
            "image": "画像",
            "to": "から",
            "delete": "削除",
            "merge_btn": "結合",
            "no_merge_images": "結合する画像がありません！",
            "invalid_range": "画像 {} の範囲が無効です！",
            "no_range_images": "範囲 {} に画像がありません！",
            "loading_error": "画像の読み込みエラー：{}",
            "saving_error": "画像 {} の保存エラー：{}",
            "merge_complete": "結合が完了しました！",
            # About section
            "about": "について",
            "version": "バージョン",
            "github": "GitHub リポジトリ",
            "github_link": "ブラウザで開く",
            "visible_formats": "表示形式",
            "merge_output_format": "結合出力形式"
        },
        "ko": {
            # Settings tab
            "settings": "설정",
            "appearance": "외관",
            "language": "언어",
            "theme_light": "라이트",
            "theme_dark": "다크",
            "save_settings": "설정 저장",
            "settings_saved": "설정이 저장되었습니다!",
            # Convert tab
            "convert": "변환",
            "select_files": "파일 또는 폴더 선택",
            "browse": "찾아보기",
            "conversion_format": "변환 형식",
            "convert_btn": "변환",
            "success": "성공",
            "error": "오류",
            "select_folder": "폴더를 선택하시겠습니까? (아니오 - 파일 선택)",
            "select_images": "이미지 선택",
            "select_save_folder": "저장 폴더 선택",
            "no_images": "변환할 이미지가 없습니다!",
            "conversion_complete": "변환이 완료되었습니다!",
            "conversion_error": "{} 변환 오류: {}",
            # Merge tab
            "merge": "병합",
            "merge_direction": "병합 방향",
            "horizontal": "가로",
            "vertical": "세로",
            "add_range": "범위 추가",
            "image": "이미지",
            "to": "에서",
            "delete": "삭제",
            "merge_btn": "병합",
            "no_merge_images": "병합할 이미지가 없습니다!",
            "invalid_range": "이미지 {}의 범위가 잘못되었습니다!",
            "no_range_images": "범위 {}에 이미지가 없습니다!",
            "loading_error": "이미지 로딩 오류: {}",
            "saving_error": "이미지 {} 저장 오류: {}",
            "merge_complete": "병합이 완료되었습니다!",
            # About section
            "about": "정보",
            "version": "버전",
            "github": "GitHub 저장소",
            "github_link": "브라우저에서 열기",
            "visible_formats": "표시 형식",
            "merge_output_format": "병합 출력 형식"
        },
        "es": {
            # Settings tab
            "settings": "Configuración",
            "appearance": "Apariencia",
            "language": "Idioma",
            "theme_light": "Claro",
            "theme_dark": "Oscuro",
            "save_settings": "Guardar Configuración",
            "settings_saved": "¡Configuración guardada exitosamente!",
            # Convert tab
            "convert": "Convertir",
            "select_files": "Seleccionar archivos o carpeta",
            "browse": "Explorar",
            "conversion_format": "Formato de conversión",
            "convert_btn": "Convertir",
            "success": "Éxito",
            "error": "Error",
            "select_folder": "¿Seleccionar carpeta? (No - seleccionar archivos)",
            "select_images": "Seleccionar imágenes",
            "select_save_folder": "Seleccionar carpeta para guardar",
            "no_images": "¡No hay imágenes para convertir!",
            "conversion_complete": "¡Conversión completada!",
            "conversion_error": "Error de conversión para {}: {}",
            # Merge tab
            "merge": "Fusionar",
            "merge_direction": "Dirección de fusión",
            "horizontal": "Horizontal",
            "vertical": "Vertical",
            "add_range": "Añadir Rango",
            "image": "Imagen",
            "to": "hasta",
            "delete": "Eliminar",
            "merge_btn": "Fusionar",
            "no_merge_images": "¡No hay imágenes para fusionar!",
            "invalid_range": "¡Rango inválido para la imagen {}!",
            "no_range_images": "¡No hay imágenes en el rango {}!",
            "loading_error": "Error al cargar imágenes: {}",
            "saving_error": "Error al guardar la imagen {}: {}",
            "merge_complete": "¡Fusión completada!",
            # About section
            "about": "Acerca de",
            "version": "Versión",
            "github": "Repositorio GitHub",
            "github_link": "Abrir en navegador",
            "visible_formats": "Formatos Visibles",
            "merge_output_format": "Formato de Salida de Fusión",
        },
        "fr": {
            # Settings tab
            "settings": "Paramètres",
            "appearance": "Apparence",
            "language": "Langue",
            "theme_light": "Clair",
            "theme_dark": "Sombre",
            "save_settings": "Enregistrer les Paramètres",
            "settings_saved": "Paramètres enregistrés avec succès !",
            # Convert tab
            "convert": "Convertir",
            "select_files": "Sélectionner fichiers ou dossier",
            "browse": "Parcourir",
            "conversion_format": "Format de conversion",
            "convert_btn": "Convertir",
            "success": "Succès",
            "error": "Erreur",
            "select_folder": "Sélectionner un dossier ? (Non - sélectionner des fichiers)",
            "select_images": "Sélectionner des images",
            "select_save_folder": "Sélectionner le dossier de sauvegarde",
            "no_images": "Aucune image à convertir !",
            "conversion_complete": "Conversion terminée !",
            "conversion_error": "Erreur de conversion pour {}: {}",
            # Merge tab
            "merge": "Fusionner",
            "merge_direction": "Direction de fusion",
            "horizontal": "Horizontale",
            "vertical": "Verticale",
            "add_range": "Ajouter une Plage",
            "image": "Image",
            "to": "à",
            "delete": "Supprimer",
            "merge_btn": "Fusionner",
            "no_merge_images": "Aucune image à fusionner !",
            "invalid_range": "Plage invalide pour l'image {} !",
            "no_range_images": "Aucune image dans la plage {} !",
            "loading_error": "Erreur de chargement des images : {}",
            "saving_error": "Erreur lors de la sauvegarde de l'image {} : {}",
            "merge_complete": "Fusion terminée !",
            # About section
            "about": "À propos",
            "version": "Version",
            "github": "Dépôt GitHub",
            "github_link": "Ouvrir dans le navigateur",
            "visible_formats": "Formats Visibles",
            "merge_output_format": "Format de Sortie de Fusion",
        },
        "de": {
            # Settings tab
            "settings": "Einstellungen",
            "appearance": "Erscheinungsbild",
            "language": "Sprache",
            "theme_light": "Hell",
            "theme_dark": "Dunkel",
            "save_settings": "Einstellungen Speichern",
            "settings_saved": "Einstellungen erfolgreich gespeichert!",
            # Convert tab
            "convert": "Konvertieren",
            "select_files": "Dateien oder Ordner auswählen",
            "browse": "Durchsuchen",
            "conversion_format": "Konvertierungsformat",
            "convert_btn": "Konvertieren",
            "success": "Erfolg",
            "error": "Fehler",
            "select_folder": "Ordner auswählen? (Nein - Dateien auswählen)",
            "select_images": "Bilder auswählen",
            "select_save_folder": "Speicherordner auswählen",
            "no_images": "Keine Bilder zum Konvertieren!",
            "conversion_complete": "Konvertierung abgeschlossen!",
            "conversion_error": "Konvertierungsfehler für {}: {}",
            # Merge tab
            "merge": "Zusammenführen",
            "merge_direction": "Zusammenführungsrichtung",
            "horizontal": "Horizontal",
            "vertical": "Vertikal",
            "add_range": "Bereich Hinzufügen",
            "image": "Bild",
            "to": "bis",
            "delete": "Löschen",
            "merge_btn": "Zusammenführen",
            "no_merge_images": "Keine Bilder zum Zusammenführen!",
            "invalid_range": "Ungültiger Bereich für Bild {}!",
            "no_range_images": "Keine Bilder im Bereich {}!",
            "loading_error": "Fehler beim Laden der Bilder: {}",
            "saving_error": "Fehler beim Speichern des Bildes {}: {}",
            "merge_complete": "Zusammenführung abgeschlossen!",
            # About section
            "about": "Über",
            "version": "Version",
            "github": "GitHub Repository",
            "github_link": "Im Browser öffnen",
            "visible_formats": "Sichtbare Formate",
            "merge_output_format": "Ausgabeformat Zusammenführung",
        }
    }

    def __init__(self):
        self.current_language = "en"
        self.load_settings()

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.current_language = settings.get('language', 'en')
        except FileNotFoundError:
            pass

    def get(self, key):
        return self.TRANSLATIONS[self.current_language].get(key, key)

    def set_language(self, language):
        self.current_language = language


class AmiFile(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Load settings
        self.load_settings()
        # Initialize localization
        self.loc = Localization()
        # Apply theme from settings
        ctk.set_appearance_mode(self.settings.get('theme', 'dark'))
        self.loc.current_language = self.settings.get('language', 'en')
        # Main window settings with fixed size
        self.title("Ami File")
        self.geometry("800x600")
        self.resizable(False, False)  # Disable both horizontal and vertical resizing
        self.minsize(800, 600)  # Set minimum size same as geometry
        self.maxsize(800, 600)  # Set maximum size same as geometry
        
        # Center window on screen
        self.center_window()
        
        # Initialize variables
        self.format_var = ctk.StringVar(value="png")
        self.direction_var = ctk.StringVar(value="horizontal")
        self.theme_var = ctk.StringVar(value=self.settings.get('theme', 'dark'))
        self.language_var = ctk.StringVar(value=self.settings.get('language', 'en'))
        self.media_format_var = ctk.StringVar(value="mp4")
        self.range_entries = []
        # Add new variables
        self.visible_formats = self.settings.get('visible_formats', [
            "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
            "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
            "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
        ])
        self.merge_format_var = ctk.StringVar(value=self.settings.get('merge_format', 'png'))
        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        # Add tabs
        self.tab_convert = self.tabview.add(self.loc.get("convert"))
        self.tab_merge = self.tabview.add(self.loc.get("merge"))
        self.tab_settings = self.tabview.add(self.loc.get("settings"))
        # Setup tabs
        self.setup_convert_tab()
        self.setup_merge_tab()
        self.setup_settings_tab()

    def center_window(self):
        """Центрирует окно приложения на экране"""
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        
        # Set window position
        self.geometry(f"800x600+{x}+{y}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
                if 'visible_formats' not in self.settings:
                    self.settings['visible_formats'] = [
                        "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
                        "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
                        "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
                    ]
                if 'merge_format' not in self.settings:
                    self.settings['merge_format'] = 'png'
        except FileNotFoundError:
            self.settings = {
                'theme': 'dark',
                'language': 'en',
                'visible_formats': [
                    "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
                    "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
                    "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
                ],
                'merge_format': 'png'
            }

    def save_settings(self):
        self.settings['theme'] = self.theme_var.get()
        self.settings['language'] = self.language_var.get()
        self.settings['visible_formats'] = [fmt for fmt in self.visible_formats]
        self.settings['merge_format'] = self.merge_format_var.get()
        
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
            
        # Apply settings immediately
        ctk.set_appearance_mode(self.theme_var.get())
        self.loc.set_language(self.language_var.get())
        
        # Update interface
        self.refresh_interface()
        
        # Show success message
        messagebox.showinfo(
            self.loc.get("success"),
            self.loc.get("settings_saved")
        )

    def refresh_interface(self):
        """Полностью обновляет интерфейс при изменении настроек"""
        # Пересоздаём все вкладки
        for widget in self.tab_convert.winfo_children():
            widget.destroy()
        for widget in self.tab_merge.winfo_children():
            widget.destroy()
        for widget in self.tab_settings.winfo_children():
            widget.destroy()
            
        # Переустанавливаем все вкладки
        self.setup_convert_tab()
        self.setup_merge_tab()
        self.setup_settings_tab()
        
        # Обновляем заголовки вкладок
        self.tabview._tab_dict["Convert"].configure(text=self.loc.get("convert"))
        self.tabview._tab_dict["Merge"].configure(text=self.loc.get("merge"))
        self.tabview._tab_dict["Settings"].configure(text=self.loc.get("settings"))

    def update_interface(self):
        """Update the interface when settings change"""
        # Recreate convert tab with new formats
        for widget in self.tab_convert.winfo_children():
            widget.destroy()
        self.setup_convert_tab()
        
        # Update tab names
        self.tabview.set("Convert")  # Switch to first tab
        
        # Update text in all frames
        for widget in self.tab_settings.winfo_children():
            if isinstance(widget, ctk.CTkScrollableFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        if hasattr(child, "_text") and child._text in self.loc.TRANSLATIONS[self.loc.current_language]:
                            child.configure(text=self.loc.get(child._text))
        
        # Force update
        self.update()

    def setup_settings_tab(self):
        # Create scrollable frame for settings
        settings_scroll = ctk.CTkScrollableFrame(self.tab_settings)
        settings_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Theme selection
        theme_frame = ctk.CTkFrame(settings_scroll)
        theme_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(theme_frame, text=self.loc.get("appearance")).pack(pady=5)
        
        ctk.CTkRadioButton(
            theme_frame,
            text=self.loc.get("theme_light"),
            variable=self.theme_var,
            value="light"
        ).pack(pady=2)
        
        ctk.CTkRadioButton(
            theme_frame,
            text=self.loc.get("theme_dark"),
            variable=self.theme_var,
            value="dark"
        ).pack(pady=2)
        
        # Language selection
        language_frame = ctk.CTkFrame(settings_scroll)
        language_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(language_frame, text=self.loc.get("language")).pack(pady=5)
        
        ctk.CTkRadioButton(
            language_frame,
            text="English",
            variable=self.language_var,
            value="en"
        ).pack(pady=2)
        
        ctk.CTkRadioButton(
            language_frame,
            text="Русский",
            variable=self.language_var,
            value="ru"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            language_frame,
            text="中文",
            variable=self.language_var,
            value="zh"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            language_frame,
            text="日本語",
            variable=self.language_var,
            value="ja"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            language_frame,
            text="한국어",
            variable=self.language_var,
            value="ko"
        ).pack(pady=2)

        # Add new language options
        ctk.CTkRadioButton(
            language_frame,
            text="Español",
            variable=self.language_var,
            value="es"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            language_frame,
            text="Français",
            variable=self.language_var,
            value="fr"
        ).pack(pady=2)

        ctk.CTkRadioButton(
            language_frame,
            text="Deutsch",
            variable=self.language_var,
            value="de"
        ).pack(pady=2)
        
        # Format visibility settings
        formats_frame = ctk.CTkFrame(settings_scroll)
        formats_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(formats_frame, text=self.loc.get("visible_formats")).pack(pady=5)
        
        formats_grid = ctk.CTkFrame(formats_frame, fg_color="transparent")
        formats_grid.pack(pady=5)
        
        # Fixed number of columns for better visibility
        COLS = 6  # Maximum 6 formats per row
        
        formats = [
            "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
            "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
            "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
        ]
        
        # Create checkboxes dictionary to store references
        self.format_vars = {}
        
        for i, fmt in enumerate(formats):
            row = i // COLS
            col = i % COLS
            var = ctk.BooleanVar(value=fmt in self.visible_formats)
            self.format_vars[fmt] = var
            cb = ctk.CTkCheckBox(
                formats_grid,
                text=fmt,
                variable=var,
                command=lambda f=fmt: self.toggle_format(f)
            )
            cb.grid(row=row, column=col, padx=5, pady=2, sticky="w")

        # Merge format settings
        merge_frame = ctk.CTkFrame(settings_scroll)
        merge_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(merge_frame, text=self.loc.get("merge_output_format")).pack(pady=5)
        
        for fmt in ["PNG", "JPEG", "TIFF", "WEBP"]:
            ctk.CTkRadioButton(
                merge_frame,
                text=fmt,
                variable=self.merge_format_var,
                value=fmt.lower()
            ).pack(pady=2)

        # Save button
        save_btn = ctk.CTkButton(
            settings_scroll,
            text=self.loc.get("save_settings"),
            command=self.save_settings,
            fg_color="green",
            hover_color="#006400"
        )
        save_btn.pack(pady=20)
        
        # Separator
        separator = ctk.CTkFrame(settings_scroll, height=2)
        separator.pack(fill="x", pady=10)
        
        # About section
        about_frame = ctk.CTkFrame(settings_scroll)
        about_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(
            about_frame,
            text=self.loc.get("about"),
            font=("Arial", 16, "bold")
        ).pack(pady=5)
        
        # Version info
        version_frame = ctk.CTkFrame(about_frame)
        version_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text=f"{self.loc.get('version')}: 1.1",
            anchor="w"
        ).pack(side="left", padx=10)
        
        # GitHub link
        github_frame = ctk.CTkFrame(about_frame)
        github_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            github_frame,
            text=self.loc.get("github") + ":",
            anchor="w"
        ).pack(side="left", padx=10)
        
        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/Baconana-chan/Ami-File")
        
        github_button = ctk.CTkButton(
            github_frame,
            text=self.loc.get("github_link"),
            command=open_github,
            width=120,
            fg_color="gray",
            hover_color="#4a4a4a"
        )
        github_button.pack(side="left", padx=10)

    def toggle_format(self, format_name):
        """Update visible formats list when checkbox is toggled"""
        if self.format_vars[format_name].get():
            if format_name not in self.visible_formats:
                self.visible_formats.append(format_name)
        else:
            if format_name in self.visible_formats:
                self.visible_formats.remove(format_name)
        
        # Update convert tab immediately
        for widget in self.tab_convert.winfo_children():
            widget.destroy()
        self.setup_convert_tab()

    def setup_convert_tab(self):
        # File selection frame
        file_frame = ctk.CTkFrame(self.tab_convert)
        file_frame.pack(fill="x", padx=20, pady=10)
        self.entry_convert = ctk.CTkEntry(
            file_frame,
            placeholder_text=self.loc.get("select_files"),
            width=400
        )
        self.entry_convert.pack(side="left", padx=10, pady=10)
        browse_btn = ctk.CTkButton(
            file_frame,
            text=self.loc.get("browse"),
            command=self.select_input_convert
        )
        browse_btn.pack(side="left", padx=10)
        
        # Format selection frame
        format_frame = ctk.CTkFrame(self.tab_convert)
        format_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            format_frame,
            text=self.loc.get("conversion_format")
        ).pack(pady=5)
        
        # Create inner frame for grid layout
        formats_grid = ctk.CTkFrame(format_frame, fg_color="transparent")
        formats_grid.pack(pady=5)
        
        # Show only visible formats
        visible_formats = [fmt for fmt in self.visible_formats]
        if not visible_formats:  # If no formats are visible, show at least PNG
            visible_formats = ["PNG"]
            
        # Calculate columns for 3 rows layout
        cols = (len(visible_formats) + 2) // 3
        
        # Arrange formats in 3 rows
        for i, fmt in enumerate(visible_formats):
            row = i // cols
            col = i % cols
            ctk.CTkRadioButton(
                formats_grid,
                text=fmt,
                variable=self.format_var,
                value=fmt.lower()
            ).grid(row=row, column=col, padx=10, pady=2, sticky="w")
        
        # Convert button
        convert_btn = ctk.CTkButton(
            self.tab_convert,
            text=self.loc.get("convert_btn"),
            command=self.convert_images,
            fg_color="green",
            hover_color="#006400"
        )
        convert_btn.pack(pady=20)
        
        # Progress bar
        self.progress_convert = ctk.CTkProgressBar(self.tab_convert, width=400)
        self.progress_convert.pack(pady=10)
        self.progress_convert.set(0)

    def setup_merge_tab(self):
        # File selection frame
        file_frame = ctk.CTkFrame(self.tab_merge)
        file_frame.pack(fill="x", padx=20, pady=10)
        self.entry_merge = ctk.CTkEntry(
            file_frame,
            placeholder_text=self.loc.get("select_files"),
            width=400
        )
        self.entry_merge.pack(side="left", padx=10, pady=10)
        browse_btn = ctk.CTkButton(
            file_frame,
            text=self.loc.get("browse"),
            command=self.select_input_merge
        )
        browse_btn.pack(side="left", padx=10)
        
        # Merge direction frame
        direction_frame = ctk.CTkFrame(self.tab_merge)
        direction_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            direction_frame,
            text=self.loc.get("merge_direction")
        ).pack(pady=5)
        ctk.CTkRadioButton(
            direction_frame,
            text=self.loc.get("horizontal"),
            variable=self.direction_var,
            value="horizontal"
        ).pack(pady=2)
        ctk.CTkRadioButton(
            direction_frame,
            text=self.loc.get("vertical"),
            variable=self.direction_var,
            value="vertical"
        ).pack(pady=2)
        
        # Scrollable frame for ranges
        self.scrollable_frame = ctk.CTkScrollableFrame(self.tab_merge, height=200)
        self.scrollable_frame.pack(fill="x", padx=20, pady=10)
        
        # Add range button
        add_range_btn = ctk.CTkButton(
            self.tab_merge,
            text=self.loc.get("add_range"),
            command=self.add_range
        )
        add_range_btn.pack(pady=10)
        
        # Merge button
        merge_btn = ctk.CTkButton(
            self.tab_merge,
            text=self.loc.get("merge_btn"),
            command=self.merge_images,
            fg_color="green",
            hover_color="#006400"
        )
        merge_btn.pack(pady=20)
        
        # Progress bar
        self.progress_merge = ctk.CTkProgressBar(self.tab_merge, width=400)
        self.progress_merge.pack(pady=10)
        self.progress_merge.set(0)

    def select_input_convert(self):
        choice = messagebox.askquestion(
            self.loc.get("select_images"),
            self.loc.get("select_folder")
        )
        if choice == "yes":
            path = filedialog.askdirectory(title=self.loc.get("select_images"))
        else:
            path = ";".join(filedialog.askopenfilenames(
                title=self.loc.get("select_images"),
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico *.ppm *.svg *.pdf *.eps *.psd *.heic *.avif *.jpegxl *.rla *.pcx *.pnm *.xbm *.tga *.djvu")]
            ))
        if path:
            self.entry_convert.delete(0, "end")
            self.entry_convert.insert(0, path)

    def select_input_merge(self):
        choice = messagebox.askquestion(
            self.loc.get("select_images"),
            self.loc.get("select_folder")
        )
        if choice == "yes":
            path = filedialog.askdirectory(title=self.loc.get("select_images"))
        else:
            path = ";".join(filedialog.askopenfilenames(
                title=self.loc.get("select_images"),
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico *.ppm *.svg *.pdf *.eps *.psd *.heic *.avif *.jpegxl *.rla *.pcx *.pnm *.xbm *.tga *.djvu")]
            ))
        if path:
            self.entry_merge.delete(0, "end")
            self.entry_merge.insert(0, path)

    def add_range(self):
        range_frame = ctk.CTkFrame(self.scrollable_frame)
        range_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            range_frame,
            text=f"{self.loc.get('image')} {len(self.range_entries) + 1}:"
        ).pack(side="left", padx=5)
        start_entry = ctk.CTkEntry(range_frame, width=70)
        start_entry.pack(side="left", padx=5)
        ctk.CTkLabel(range_frame, text=self.loc.get("to")).pack(side="left", padx=5)
        end_entry = ctk.CTkEntry(range_frame, width=70)
        end_entry.pack(side="left", padx=5)
        
        def remove_range():
            range_frame.destroy()
            self.range_entries.remove((start_entry, end_entry))
        
        ctk.CTkButton(
            range_frame,
            text=self.loc.get("delete"),
            command=remove_range,
            fg_color="red",
            hover_color="#8B0000",
            width=70
        ).pack(side="left", padx=5)
        
        self.range_entries.append((start_entry, end_entry))

    def convert_images(self):
        input_path = self.entry_convert.get()
        if not input_path:
            messagebox.showerror(
                self.loc.get("error"),
                self.loc.get("no_images")
            )
            return
        output_format = self.format_var.get()
        output_folder = filedialog.askdirectory(title=self.loc.get("select_save_folder"))
        if not output_folder:
            return
        
        # Get image files
        if os.path.isdir(input_path):
            images = sorted([
                os.path.join(input_path, f) for f in os.listdir(input_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', 
                                       '.webp', '.svg', '.pdf', '.eps', '.psd', 
                                       '.heic', '.avif', '.jpegxl', '.ico', '.ppm',
                                       '.rla', '.pcx', '.pnm', '.xbm', '.tga', '.djvu'))
            ])
        else:
            images = sorted(input_path.split(";"))
        
        if not images:
            messagebox.showerror(
                self.loc.get("error"),
                self.loc.get("no_images")
            )
            return
        
        # Update progress bar
        self.progress_convert.configure(determinate_speed=1 / len(images))
        self.progress_convert.start()
        
        for input_path in images:
            try:
                with Image(filename=input_path) as img:
                    # Handle transparency for formats that don't support it
                    if output_format in ['jpg', 'jpeg', 'bmp'] and img.alpha_channel:
                        with Color('white') as background:
                            img.background_color = background
                            img.alpha_channel = 'remove'
                    
                    # Preserve original filename, just change extension
                    output_path = os.path.join(
                        output_folder,
                        f"{os.path.splitext(os.path.basename(input_path))[0]}.{output_format}"
                    )
                    
                    # Save the converted image
                    img.convert(output_format)
                    img.save(filename=output_path)
            
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("conversion_error").format(input_path, str(e))
                )
        
        # Finalize progress
        self.progress_convert.stop()
        self.progress_convert.set(1)
        messagebox.showinfo(
            self.loc.get("success"),
            self.loc.get("conversion_complete")
        )

    def merge_images(self):
        input_path = self.entry_merge.get()
        if not input_path:
            messagebox.showerror(
                self.loc.get("error"),
                self.loc.get("no_merge_images")
            )
            return
        
        if os.path.isdir(input_path):
            images = sorted([
                os.path.join(input_path, f) for f in os.listdir(input_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', 
                                       '.tiff', '.webp', '.svg', '.pdf', '.eps', '.psd', 
                                       '.heic', '.avif', '.jpegxl', '.ico', '.ppm',
                                       '.rla', '.pcx', '.pnm', '.xbm', '.tga', '.djvu'))
            ])
        else:
            images = sorted(input_path.split(";"))
        
        if not images:
            messagebox.showerror(
                self.loc.get("error"),
                self.loc.get("no_merge_images")
            )
            return
        
        output_folder = filedialog.askdirectory(title=self.loc.get("select_save_folder"))
        if not output_folder:
            return
        
        self.progress_merge.configure(determinate_speed=1 / len(self.range_entries))
        self.progress_merge.start()
        
        for i, (start_entry, end_entry) in enumerate(self.range_entries):
            try:
                start_index = int(start_entry.get()) - 1
                end_index = int(end_entry.get())
            except ValueError:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("invalid_range").format(i + 1)
                )
                continue
            
            range_images = images[start_index:end_index]
            if not range_images:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("no_range_images").format(i + 1)
                )
                continue
            
            try:
                # Open images with Wand
                imgs = [Image(filename=img) for img in range_images]
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("loading_error").format(e)
                )
                continue
            
            try:
                if self.direction_var.get() == "horizontal":
                    # Calculate total width and max height
                    total_width = sum(img.width for img in imgs)
                    max_height = max(img.height for img in imgs)
                    
                    # Create a new image
                    with Image(width=total_width, height=max_height, background=Color('white')) as new_img:
                        x_offset = 0
                        for img in imgs:
                            new_img.composite(img, left=x_offset, top=0)
                            x_offset += img.width
                        
                        # Save the merged image
                        output_path = os.path.join(output_folder, f"{i + 1}.{self.merge_format_var.get()}")
                        new_img.save(filename=output_path)
                
                else:  # Vertical merging
                    # Calculate total height and max width
                    total_height = sum(img.height for img in imgs)
                    max_width = max(img.width for img in imgs)
                    
                    # Create a new image
                    with Image(width=max_width, height=total_height, background=Color('white')) as new_img:
                        y_offset = 0
                        for img in imgs:
                            new_img.composite(img, left=0, top=y_offset)
                            y_offset += img.height
                        
                        # Save the merged image
                        output_path = os.path.join(output_folder, f"{i + 1}.{self.merge_format_var.get()}")
                        new_img.save(filename=output_path)
                
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("saving_error").format(i + 1, e)
                )
        
        # Close any remaining open images
        for img_list in imgs:
            img_list.close()
        
        self.progress_merge.stop()
        self.progress_merge.set(1)
        messagebox.showinfo(
            self.loc.get("success"),
            self.loc.get("merge_complete")
        )


if __name__ == "__main__":
    app = AmiFile()
    app.mainloop()
