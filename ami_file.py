import customtkinter as ctk
import os
import json
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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
            "github_link": "Open in browser"
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
            "github_link": "Открыть в браузере"
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
        # Main window settings
        self.title("Ami File")
        self.geometry("800x600")
        # Initialize variables
        self.format_var = ctk.StringVar(value="png")
        self.direction_var = ctk.StringVar(value="horizontal")
        self.theme_var = ctk.StringVar(value=self.settings.get('theme', 'dark'))
        self.language_var = ctk.StringVar(value=self.settings.get('language', 'en'))
        self.range_entries = []
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

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {'theme': 'dark', 'language': 'en'}

    def save_settings(self):
        self.settings['theme'] = self.theme_var.get()
        self.settings['language'] = self.language_var.get()
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
        # Apply settings
        ctk.set_appearance_mode(self.theme_var.get())
        self.loc.set_language(self.language_var.get())
        # Show success message
        messagebox.showinfo(
            self.loc.get("success"),
            self.loc.get("settings_saved")
        )
        # Restart application message
        messagebox.showinfo(
            self.loc.get("success"),
            "Please restart the application for all changes to take effect."
        )

    def setup_settings_tab(self):
        # Theme selection
        theme_frame = ctk.CTkFrame(self.tab_settings)
        theme_frame.pack(fill="x", padx=20, pady=10)
        
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
        language_frame = ctk.CTkFrame(self.tab_settings)
        language_frame.pack(fill="x", padx=20, pady=10)
        
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
        
        # Save button
        save_btn = ctk.CTkButton(
            self.tab_settings,
            text=self.loc.get("save_settings"),
            command=self.save_settings,
            fg_color="green",
            hover_color="#006400"
        )
        save_btn.pack(pady=20)
        
        # Separator
        separator = ctk.CTkFrame(self.tab_settings, height=2)
        separator.pack(fill="x", padx=20, pady=10)
        
        # About section
        about_frame = ctk.CTkFrame(self.tab_settings)
        about_frame.pack(fill="x", padx=20, pady=10)
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
            text=f"{self.loc.get('version')}: 1.0",
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
        formats = ["PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF"]
        for fmt in formats:
            ctk.CTkRadioButton(
                format_frame,
                text=fmt,
                variable=self.format_var,
                value=fmt.lower()
            ).pack(pady=2)
        
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
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico *.ppm")]
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
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
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
        if os.path.isdir(input_path):
            images = sorted([
                os.path.join(input_path, f) for f in os.listdir(input_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp', '.ico', '.ppm'))
            ])
        else:
            images = sorted(input_path.split(";"))
        if not images:
            messagebox.showerror(
                self.loc.get("error"),
                self.loc.get("no_images")
            )
            return
        self.progress_convert.configure(determinate_speed=1 / len(images))
        self.progress_convert.start()
        for input_path in images:
            try:
                img = Image.open(input_path)
                output_path = os.path.join(
                    output_folder,
                    f"{os.path.splitext(os.path.basename(input_path))[0]}.{output_format}"
                )
                if output_format == "jpeg" and img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(output_path, format=output_format)
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("conversion_error").format(input_path, e)
                )
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
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
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
                imgs = [Image.open(img) for img in range_images]
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("loading_error").format(e)
                )
                continue
            if self.direction_var.get() == "horizontal":
                total_width = sum(img.width for img in imgs)
                max_height = max(img.height for img in imgs)
                new_img = Image.new("RGB", (total_width, max_height))
                x_offset = 0
                for img in imgs:
                    new_img.paste(img, (x_offset, 0))
                    x_offset += img.width
            else:
                total_height = sum(img.height for img in imgs)
                max_width = max(img.width for img in imgs)
                new_img = Image.new("RGB", (max_width, total_height))
                y_offset = 0
                for img in imgs:
                    new_img.paste(img, (0, y_offset))
                    y_offset += img.height
            output_path = os.path.join(output_folder, f"{i + 1}.png")
            try:
                new_img.save(output_path)
            except Exception as e:
                messagebox.showerror(
                    self.loc.get("error"),
                    self.loc.get("saving_error").format(i + 1, e)
                )
        self.progress_merge.stop()
        self.progress_merge.set(1)
        messagebox.showinfo(
            self.loc.get("success"),
            self.loc.get("merge_complete")
        )


if __name__ == "__main__":
    app = AmiFile()
    app.mainloop()