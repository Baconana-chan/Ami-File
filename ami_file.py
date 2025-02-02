import sys
import os
import json
import time
import concurrent.futures
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading

# Устанавливаем путь к ImageMagick
IMAGEMAGICK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ImageMagick")
if getattr(sys, 'frozen', False):
    # Если запускается из exe
    IMAGEMAGICK_PATH = os.path.join(sys._MEIPASS, "ImageMagick")
os.environ['MAGICK_HOME'] = IMAGEMAGICK_PATH
os.environ['PATH'] = f"{IMAGEMAGICK_PATH};{os.environ['PATH']}"

# Флаги доступности библиотек
HAVE_PIL = True
HAVE_CV2 = True
HAVE_WAND = True
HAVE_VIPS = True

# Пробуем импортировать библиотеки с обработкой ошибок
try:
    from PIL import Image as PILImage
except ImportError:
    HAVE_PIL = False
    print("PIL not available")

try:
    import cv2
    import numpy as np
except ImportError:
    HAVE_CV2 = False
    print("OpenCV not available")

try:
    from wand.image import Image as WandImage
    from wand.color import Color
    from wand.api import library
except ImportError:
    HAVE_WAND = False
    print("ImageMagick/Wand not available")

try:
    import pyvips
except ImportError:
    HAVE_VIPS = False
    print("Pyvips not available")

# Проверяем и выводим информацию о доступных библиотеках
print(f"Available libraries: PIL={HAVE_PIL}, OpenCV={HAVE_CV2}, Wand={HAVE_WAND}, Vips={HAVE_VIPS}")
print(f"ImageMagick path: {IMAGEMAGICK_PATH}")

# Проверяем, есть ли хотя бы одна библиотека для работы с изображениями
if not any([HAVE_PIL, HAVE_CV2, HAVE_WAND, HAVE_VIPS]):
    messagebox.showerror(
        "Error",
        "No image processing libraries found!\n"
        "Please install at least one of:\n"
        "- Pillow (pip install Pillow)\n"
        "- OpenCV (pip install opencv-python)\n"
        "- Wand (pip install Wand)\n"
        "- Pyvips (pip install pyvips)"
    )
    sys.exit(1)

# Поддерживаемые форматы для каждой библиотеки
SUPPORTED_FORMATS = {
    'wand': {
        'input': {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp', 'svg', 
                 'pdf', 'eps', 'psd', 'heic', 'avif', 'jpegxl', 'ico', 'ppm',
                 'rla', 'pcx', 'pnm', 'xbm', 'tga', 'djvu'},
        'output': {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp', 'svg', 
                 'pdf', 'eps', 'psd', 'heic', 'avif', 'jpegxl', 'ico', 'ppm',
                 'rla', 'pcx', 'pnm', 'xbm', 'tga', 'djvu'}
    },
    'pil': {
        'input': {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp', 'ico', 'ppm'},
        'output': {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp', 'ico'}
    },
    'cv2': {
        'input': {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'},
        'output': {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    },
    'vips': {
        'input': {'png', 'jpg', 'jpeg', 'webp', 'tiff', 'gif', 'pdf', 'svg', 'heif', 'avif'},
        'output': {'png', 'jpg', 'jpeg', 'webp', 'tiff', 'gif', 'heif', 'avif'}
    }
}

class ProcessingLibrary:
    WAND = "wand"
    PIL = "pil"
    CV2 = "cv2"
    VIPS = "vips"

def convert_image(args):
    """Оптимизированная функция конвертации с резервными вариантами"""
    input_path, output_path, output_format, needs_alpha_removal = args
    
    # Пробуем разные библиотеки по порядку
    errors = []
    
    # 1. Попытка использовать PIL
    if HAVE_PIL:
        try:
            with PILImage.open(input_path) as img:
                if needs_alpha_removal and img.mode == 'RGBA':
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    background.save(output_path, format=output_format.upper())
                else:
                    img.save(output_path, format=output_format.upper())
            return True
        except Exception as e:
            errors.append(f"PIL: {str(e)}")
    
    # 2. Попытка использовать OpenCV
    if HAVE_CV2:
        try:
            img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if needs_alpha_removal and img.shape[-1] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(output_path, img)
                return True
        except Exception as e:
            errors.append(f"OpenCV: {str(e)}")
    
    # 3. Попытка использовать Wand
    if HAVE_WAND:
        try:
            with WandImage(filename=input_path) as img:
                if needs_alpha_removal and img.alpha_channel:
                    with Color('white') as background:
                        img.background_color = background
                        img.alpha_channel = 'remove'
                img.format = output_format.upper()
                img.save(filename=output_path)
            return True
        except Exception as e:
            errors.append(f"Wand: {str(e)}")
    
    # 4. Попытка использовать Pyvips
    if HAVE_VIPS:
        try:
            image = pyvips.Image.new_from_file(input_path)
            if needs_alpha_removal and image.hasalpha():
                # Удаляем альфа-канал
                image = image.flatten(background=[255, 255, 255])
            
            # Сохраняем с учетом формата
            if output_format.lower() in ['jpg', 'jpeg']:
                image.jpegsave(output_path, Q=95)
            elif output_format.lower() == 'png':
                image.pngsave(output_path)
            elif output_format.lower() == 'webp':
                image.webpsave(output_path, Q=95)
            elif output_format.lower() == 'tiff':
                image.tiffsave(output_path)
            else:
                image.write_to_file(output_path)
            return True
        except Exception as e:
            errors.append(f"Vips: {str(e)}")
    
    # Если все методы не сработали, возвращаем ошибку
    return (input_path, "\n".join(errors))

def merge_images_optimized(images, direction='horizontal', output_path=None, output_format='png'):
    """Оптимизированная функция слияния с резервными вариантами"""
    errors = []
    
    # 1. Попытка использовать PIL
    if HAVE_PIL:
        try:
            if direction == 'horizontal':
                imgs = [PILImage.open(img) for img in images]
                total_width = sum(img.width for img in imgs)
                max_height = max(img.height for img in imgs)
                merged_image = PILImage.new('RGB', (total_width, max_height), (255, 255, 255))
                x_offset = 0
                for img in imgs:
                    merged_image.paste(img, (x_offset, 0))
                    x_offset += img.width
                    img.close()
            else:
                imgs = [PILImage.open(img) for img in images]
                total_height = sum(img.height for img in imgs)
                max_width = max(img.width for img in imgs)
                merged_image = PILImage.new('RGB', (max_width, total_height), (255, 255, 255))
                y_offset = 0
                for img in imgs:
                    merged_image.paste(img, (0, y_offset))
                    y_offset += img.height
                    img.close()
            
            if output_path:
                merged_image.save(output_path, format=output_format.upper())
            return merged_image
        except Exception as e:
            errors.append(f"PIL: {str(e)}")
    
    # 2. Попытка использовать OpenCV
    if HAVE_CV2:
        try:
            cv_images = [cv2.imread(img) for img in images]
            if direction == 'horizontal':
                merged_image = np.hstack(cv_images)
            else:
                merged_image = np.vstack(cv_images)
            cv2.imwrite(output_path, merged_image)
            return True
        except Exception as e:
            errors.append(f"OpenCV: {str(e)}")
    
    # 3. Попытка использовать Wand
    if HAVE_WAND:
        try:
            with WandImage() as merged_image:
                with WandImage(filename=images[0]) as first:
                    merged_image.format = first.format
                    if direction == 'horizontal':
                        for img_path in images[1:]:
                            with WandImage(filename=img_path) as img:
                                merged_image.sequence.append(img)
                        merged_image.reset_sequence()
                    else:
                        for img_path in images[1:]:
                            with WandImage(filename=img_path) as img:
                                merged_image.sequence.extend(img.sequence)
                if output_path:
                    merged_image.save(filename=output_path)
                return merged_image
        except Exception as e:
            errors.append(f"Wand: {str(e)}")
    
    # 4. Попытка использовать Pyvips
    if HAVE_VIPS:
        try:
            # Загружаем изображения
            vips_images = [pyvips.Image.new_from_file(img) for img in images]
            
            # Объединяем изображения
            if direction == 'horizontal':
                merged = pyvips.Image.arrayjoin(vips_images, across=len(vips_images))
            else:
                merged = pyvips.Image.arrayjoin(vips_images, across=1)
            
            # Сохраняем результат
            if output_path:
                if output_format.lower() in ['jpg', 'jpeg']:
                    merged.jpegsave(output_path, Q=95)
                elif output_format.lower() == 'png':
                    merged.pngsave(output_path)
                elif output_format.lower() == 'webp':
                    merged.webpsave(output_path, Q=95)
                elif output_format.lower() == 'tiff':
                    merged.tiffsave(output_path)
                else:
                    merged.write_to_file(output_path)
            return True
        except Exception as e:
            errors.append(f"Vips: {str(e)}")
    
    raise Exception("Failed to merge images using any method:\n" + "\n".join(errors))

def batch_convert(conversion_args, progress_callback, batch_size=10):
    """Обновленная версия с поддержкой расширенного прогресса"""
    errors = []
    total = len(conversion_args)
    progress_info = ProgressInfo(total)
    
    for i in range(0, total, batch_size):
        batch = conversion_args[i:i + batch_size]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(os.cpu_count(), len(batch))) as executor:
            futures = {executor.submit(convert_image, args): args[0] for args in batch}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if isinstance(result, tuple):
                    errors.append(result)
                
                progress_info.complete_file()
                progress_callback(1.0, progress_info)  # Файл завершен
                
    return errors

class ProgressInfo:
    """Класс для хранения информации о прогрессе"""
    def __init__(self, total_files):
        self.total_files = total_files
        self.processed_files = 0
        self.current_file = 0
        self.start_time = time.time()
        self.file_start_time = time.time()
        self.avg_file_time = 0
        
    def update_file_progress(self, progress):
        """Обновляет прогресс текущего файла"""
        self.current_file = progress
        
    def complete_file(self):
        """Отмечает завершение обработки файла"""
        self.processed_files += 1
        current_time = time.time()
        file_time = current_time - self.file_start_time
        self.avg_file_time = (self.avg_file_time * (self.processed_files - 1) + file_time) / self.processed_files
        self.file_start_time = current_time
        
    def get_eta(self):
        """Возвращает расчетное время до завершения"""
        if self.processed_files == 0:
            return "Calculating..."
        
        elapsed_time = time.time() - self.start_time
        files_left = self.total_files - self.processed_files
        avg_time_per_file = elapsed_time / self.processed_files
        eta_seconds = files_left * avg_time_per_file
        
        if eta_seconds < 60:
            return f"{int(eta_seconds)}s"
        elif eta_seconds < 3600:
            return f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
        else:
            hours = int(eta_seconds/3600)
            minutes = int((eta_seconds%3600)/60)
            return f"{hours}h {minutes}m"

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
            # Progress bar translations
            "progress_current": "Current file: ",
            "progress_time": "Time per file: ",
            "progress_overall": "Overall progress: ",
            "progress_eta": "Estimated time remaining: ",
            "calculating": "Calculating...",
            
            # Library descriptions
            "recommended": "Recommended",
            "basic_formats": "Basic formats",
            "fast_standard": "Fast for standard formats",
            "fast_large": "Fast for large images",
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
            # Progress bar translations
            "progress_current": "Текущий файл: ",
            "progress_time": "Время на файл: ",
            "progress_overall": "Общий прогресс: ",
            "progress_eta": "Осталось времени: ",
            "calculating": "Вычисление...",
            
            # Library descriptions
            "recommended": "Рекомендуется",
            "basic_formats": "Базовые форматы",
            "fast_standard": "Быстрая для стандартных форматов",
            "fast_large": "Быстрая для больших изображений",
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
            "merge_output_format": "合并输出格式",
            # Progress bar translations
            "progress_current": "当前文件: ",
            "progress_time": "每个文件的时间: ",
            "progress_overall": "总体进度: ",
            "progress_eta": "预计剩余时间: ",
            "calculating": "计算中...",
            
            # Library descriptions
            "recommended": "推荐",
            "basic_formats": "基本格式",
            "fast_standard": "标准格式快速",
            "fast_large": "大图像快速",
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
            "merge_output_format": "結合出力形式",
            # Progress bar translations
            "progress_current": "現在のファイル: ",
            "progress_time": "ファイルごとの時間: ",
            "progress_overall": "全体の進捗: ",
            "progress_eta": "残り時間の見積もり: ",
            "calculating": "計算中...",
            
            # Library descriptions
            "recommended": "推奨",
            "basic_formats": "基本フォーマット",
            "fast_standard": "標準フォーマットの高速",
            "fast_large": "大きな画像の高速",
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
            "merge_output_format": "병합 출력 형식",
            # Progress bar translations
            "progress_current": "현재 파일: ",
            "progress_time": "파일당 시간: ",
            "progress_overall": "전체 진행 상황: ",
            "progress_eta": "예상 남은 시간: ",
            "calculating": "계산 중...",
            
            # Library descriptions
            "recommended": "추천",
            "basic_formats": "기본 형식",
            "fast_standard": "표준 형식에 빠름",
            "fast_large": "큰 이미지에 빠름",
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
            # Progress bar translations
            "progress_current": "Archivo actual: ",
            "progress_time": "Tiempo por archivo: ",
            "progress_overall": "Progreso general: ",
            "progress_eta": "Tiempo estimado restante: ",
            "calculating": "Calculando...",
            
            # Library descriptions
            "recommended": "Recomendado",
            "basic_formats": "Formatos básicos",
            "fast_standard": "Rápido para formatos estándar",
            "fast_large": "Rápido para imágenes grandes",
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
            # Progress bar translations
            "progress_current": "Fichier actuel: ",
            "progress_time": "Temps par fichier: ",
            "progress_overall": "Progression globale: ",
            "progress_eta": "Temps restant estimé: ",
            "calculating": "Calcul...",
            
            # Library descriptions
            "recommended": "Recommandé",
            "basic_formats": "Formats de base",
            "fast_standard": "Rapide pour les formats standard",
            "fast_large": "Rapide pour les grandes images",
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
            # Progress bar translations
            "progress_current": "Aktuelle Datei: ",
            "progress_time": "Zeit pro Datei: ",
            "progress_overall": "Gesamtfortschritt: ",
            "progress_eta": "Geschätzte verbleibende Zeit: ",
            "calculating": "Berechnung...",
            
            # Library descriptions
            "recommended": "Empfohlen",
            "basic_formats": "Grundformate",
            "fast_standard": "Schnell für Standardformate",
            "fast_large": "Schnell für große Bilder",
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


class ToolTip:
    """Улучшенный класс для всплывающих подсказок"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.show_timer = None
        
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<Destroy>', self.on_destroy)
    
    def enter(self, event=None):
        # Отменяем предыдущий таймер если есть
        self.cancel_timer()
        # Запускаем новый таймер на появление подсказки
        self.show_timer = self.widget.after(500, self.show_tooltip)
    
    def leave(self, event=None):
        # Отменяем таймер и скрываем подсказку
        self.cancel_timer()
        self.hide_tooltip()
    
    def show_tooltip(self):
        # Очищаем предыдущую подсказку если есть
        self.hide_tooltip()
        
        # Создаем новую подсказку
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty()
        
        self.tooltip = ctk.CTkToplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            justify="left",
            wraplength=300
        )
        label.pack(padx=5, pady=5)
        
        # Делаем подсказку поверх других окон
        self.tooltip.lift()
        self.tooltip.attributes('-topmost', True)
        
        # Привязываем дополнительные обработчики
        self.tooltip.bind('<Enter>', self.enter)
        self.tooltip.bind('<Leave>', self.leave)
    
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def cancel_timer(self):
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
    
    def on_destroy(self, event=None):
        self.hide_tooltip()
        self.cancel_timer()

def create_tooltip(widget, text):
    """Создает всплывающую подсказку для виджета"""
    return ToolTip(widget, text)

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, button_color="green", button_hover_color="#006400"):
        super().__init__(parent)
        self.title(title)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        window_width = 400
        window_height = 200
        
        # Get parent's center
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)
        
        # Message
        label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=350,
            justify="center"
        )
        label.pack(pady=20, padx=20)
        
        # OK button
        button = ctk.CTkButton(
            self,
            text="OK",
            command=self.destroy,
            fg_color=button_color,
            hover_color=button_hover_color
        )
        button.pack(pady=20)
        
        # Set focus and bind Enter
        button.focus_set()
        self.bind("<Return>", lambda e: self.destroy())

class SelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, command_yes, command_no):
        super().__init__(parent)
        self.title(title)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        window_width = 400
        window_height = 200
        
        # Get parent's center
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)
        
        # Message
        label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=350,
            justify="center"
        )
        label.pack(pady=20, padx=20)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Yes button
        yes_button = ctk.CTkButton(
            button_frame,
            text="Yes",
            command=lambda: self.handle_choice(command_yes),
            fg_color="green",
            hover_color="#006400",
            width=120
        )
        yes_button.pack(side="left", padx=10)
        
        # No button
        no_button = ctk.CTkButton(
            button_frame,
            text="No",
            command=lambda: self.handle_choice(command_no),
            fg_color="gray",
            hover_color="#4a4a4a",
            width=120
        )
        no_button.pack(side="left", padx=10)
        
        # Set focus
        yes_button.focus_set()
        
    def handle_choice(self, command):
        self.destroy()
        if command:
            command()

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
        self.processing_lib = ctk.StringVar(value=self.settings.get('processing_lib', ProcessingLibrary.WAND))
        self.conversion_running = False
        self.merge_running = False
        # Создаем вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Добавляем вкладки
        self.tab_convert = self.tabview.add(self.loc.get("convert"))
        self.tab_merge = self.tabview.add(self.loc.get("merge"))
        self.tab_settings = self.tabview.add(self.loc.get("settings"))
        
        # Настраиваем вкладки
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
                if 'processing_lib' not in self.settings:
                    self.settings['processing_lib'] = ProcessingLibrary.WAND
        except FileNotFoundError:
            self.settings = {
                'theme': 'dark',
                'language': 'en',
                'visible_formats': [
                    "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
                    "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
                    "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
                ],
                'merge_format': 'png',
                'processing_lib': ProcessingLibrary.WAND
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
        
        # Update interface and stay on settings tab
        self.refresh_interface()

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
        
        # Возвращаемся на вкладку настроек
        self.tabview.set(self.loc.get("settings"))

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

        # Processing library selection with tooltips
        library_frame = ctk.CTkFrame(settings_scroll)
        library_frame.pack(fill="x", pady=10)
        
        header_frame = ctk.CTkFrame(library_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text=self.loc.get("processing_library")
        ).pack(side="left", pady=5, padx=5)
        
        info_btn = ctk.CTkButton(
            header_frame,
            text="i",
            width=20,
            height=20,
            corner_radius=10
        )
        info_btn.pack(side="left", padx=5)
        
        # Функция для форматирования строки с форматами
        def format_supported_formats(formats):
            return ", ".join(sorted(formats))
        
        # Создаем строки с поддерживаемыми форматами для каждой библиотеки
        library_info = {
            ProcessingLibrary.WAND: {
                'name': f"ImageMagick/Wand ({self.loc.get('recommended')})",
                'formats': SUPPORTED_FORMATS['wand']
            },
            ProcessingLibrary.PIL: {
                'name': f"Pillow/PIL ({self.loc.get('basic_formats')})",
                'formats': SUPPORTED_FORMATS['pil']
            },
            ProcessingLibrary.CV2: {
                'name': f"OpenCV ({self.loc.get('fast_standard')})",
                'formats': SUPPORTED_FORMATS['cv2']
            },
            ProcessingLibrary.VIPS: {
                'name': f"Pyvips ({self.loc.get('fast_large')})",
                'formats': SUPPORTED_FORMATS['vips']
            }
        }
        
        def create_library_tooltip():
            tooltip_text = f"{self.loc.get('supported_formats')}:\n\n"
            for lib_key, lib_info in library_info.items():
                if getattr(sys.modules[__name__], f'HAVE_{lib_key.upper()}'):
                    tooltip_text += f"{lib_info['name']}:\n"
                    tooltip_text += f"{self.loc.get('input_formats')}"
                    tooltip_text += format_supported_formats(lib_info['formats']['input'])
                    tooltip_text += f"\n{self.loc.get('output_formats')}"
                    tooltip_text += format_supported_formats(lib_info['formats']['output'])
                    tooltip_text += "\n\n"
            return tooltip_text
        
        create_tooltip(info_btn, create_library_tooltip())
        
        # Создаем радио-кнопки для каждой доступной библиотеки
        if HAVE_WAND:
            radio = ctk.CTkRadioButton(
                library_frame,
                text=library_info[ProcessingLibrary.WAND]['name'],
                variable=self.processing_lib,
                value=ProcessingLibrary.WAND,
                command=self.update_format_visibility
            )
            radio.pack(pady=2)
            create_tooltip(radio, format_supported_formats(library_info[ProcessingLibrary.WAND]['formats']['output']))
        
        if HAVE_PIL:
            radio = ctk.CTkRadioButton(
                library_frame,
                text=library_info[ProcessingLibrary.PIL]['name'],
                variable=self.processing_lib,
                value=ProcessingLibrary.PIL,
                command=self.update_format_visibility
            )
            radio.pack(pady=2)
            create_tooltip(radio, format_supported_formats(library_info[ProcessingLibrary.PIL]['formats']['output']))
        
        if HAVE_CV2:
            radio = ctk.CTkRadioButton(
                library_frame,
                text=library_info[ProcessingLibrary.CV2]['name'],
                variable=self.processing_lib,
                value=ProcessingLibrary.CV2,
                command=self.update_format_visibility
            )
            radio.pack(pady=2)
            create_tooltip(radio, format_supported_formats(library_info[ProcessingLibrary.CV2]['formats']['output']))
        
        if HAVE_VIPS:
            radio = ctk.CTkRadioButton(
                library_frame,
                text=library_info[ProcessingLibrary.VIPS]['name'],
                variable=self.processing_lib,
                value=ProcessingLibrary.VIPS,
                command=self.update_format_visibility
            )
            radio.pack(pady=2)
            create_tooltip(radio, format_supported_formats(library_info[ProcessingLibrary.VIPS]['formats']['output']))

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
            text=f"{self.loc.get('version')}: 1.2",
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
        """Обновленная версия с двумя прогресс-барами"""
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
        
        # Progress frame with translations
        progress_frame = ctk.CTkFrame(self.tab_convert)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        # Current file progress
        self.current_progress_label = ctk.CTkLabel(
            progress_frame, 
            text=f"{self.loc.get('progress_current')}0/0"
        )
        self.current_progress_label.pack(pady=2)
        
        self.progress_convert = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_convert.pack(pady=2)
        self.progress_convert.set(0)
        
        self.current_time_label = ctk.CTkLabel(
            progress_frame, 
            text=f"{self.loc.get('progress_time')}--"
        )
        self.current_time_label.pack(pady=2)
        
        # Overall progress
        self.total_progress_label = ctk.CTkLabel(
            progress_frame, 
            text=f"{self.loc.get('progress_overall')}0/0"
        )
        self.total_progress_label.pack(pady=2)
        
        self.total_progress = ctk.CTkProgressBar(progress_frame, width=400)
        self.total_progress.pack(pady=2)
        self.total_progress.set(0)
        
        self.eta_label = ctk.CTkLabel(
            progress_frame, 
            text=f"{self.loc.get('progress_eta')}--"
        )
        self.eta_label.pack(pady=2)

    def setup_merge_tab(self):
        """Setup merge tab UI"""
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
        """Выбор файлов/папки для конвертации"""
        def select_folder():
            path = filedialog.askdirectory(title=self.loc.get("select_images"))
            if path:
                self.entry_convert.delete(0, "end")
                self.entry_convert.insert(0, path)

        def select_files():
            files = filedialog.askopenfilenames(
                title=self.loc.get("select_images"),
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico *.ppm *.svg *.pdf *.eps *.psd *.heic *.avif *.jpegxl *.rla *.pcx *.pnm *.xbm *.tga *.djvu")]
            )
            if files:
                path = ";".join(files)
                self.entry_convert.delete(0, "end")
                self.entry_convert.insert(0, path)

        SelectionDialog(
            self,
            self.loc.get("select_images"),
            self.loc.get("select_folder"),
            select_folder,
            select_files
        )

    def select_input_merge(self):
        """Выбор файлов/папки для склеивания"""
        def select_folder():
            path = filedialog.askdirectory(title=self.loc.get("select_images"))
            if path:
                self.entry_merge.delete(0, "end")
                self.entry_merge.insert(0, path)

        def select_files():
            files = filedialog.askopenfilenames(
                title=self.loc.get("select_images"),
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico *.ppm *.svg *.pdf *.eps *.psd *.heic *.avif *.jpegxl *.rla *.pcx *.pnm *.xbm *.tga *.djvu")]
            )
            if files:
                path = ";".join(files)
                self.entry_merge.delete(0, "end")
                self.entry_merge.insert(0, path)

        SelectionDialog(
            self,
            self.loc.get("select_images"),
            self.loc.get("select_folder"),
            select_folder,
            select_files
        )

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

    def update_progress(self, file_progress, progress_info):
        """Обновляет информацию о прогрессе"""
        self.after(0, lambda: self._update_progress_ui(file_progress, progress_info))

    def _update_progress_ui(self, file_progress, progress_info):
        """Обновляет UI прогресса в главном потоке с переводами"""
        # Обновляем прогресс текущего файла
        self.progress_convert.set(file_progress)
        self.current_progress_label.configure(
            text=f"{self.loc.get('progress_current')}{progress_info.processed_files}/{progress_info.total_files}"
        )
        
        # Обновляем общий прогресс
        total_progress = progress_info.processed_files / progress_info.total_files
        self.total_progress.set(total_progress)
        self.total_progress_label.configure(
            text=f"{self.loc.get('progress_overall')}{progress_info.processed_files}/{progress_info.total_files}"
        )
        
        # Обновляем метки времени
        if progress_info.avg_file_time > 0:
            time_per_file = f"{self.loc.get('progress_time')}{progress_info.avg_file_time:.1f}s"
            self.current_time_label.configure(text=time_per_file)
            
            eta = progress_info.get_eta()
            self.eta_label.configure(text=f"{self.loc.get('progress_eta')}{eta}")
        
        # Обновляем UI
        self.update_idletasks()

    def convert_images(self):
        """Обновленная версия с поддержкой расширенного прогресса"""
        if self.conversion_running:
            return
            
        self.conversion_running = True
        input_path = self.entry_convert.get()
        
        if not input_path:
            messagebox.showerror(self.loc.get("error"), self.loc.get("no_images"))
            self.conversion_running = False
            return
                
        output_format = self.format_var.get()
        output_folder = filedialog.askdirectory(title=self.loc.get("select_save_folder"))
        if not output_folder:
            self.conversion_running = False
            return

        # Set of valid extensions for quick lookup
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', 
                           '.webp', '.svg', '.pdf', '.eps', '.psd', '.heic',
                           '.avif', '.jpegxl', '.ico', '.ppm', '.rla', '.pcx',
                           '.pnm', '.xbm', '.tga', '.djvu'}
        
        # Get image files
        if os.path.isdir(input_path):
            images = [
                os.path.join(input_path, f) for f in os.listdir(input_path)
                if os.path.splitext(f.lower())[1] in valid_extensions
            ]
        else:
            images = [f for f in input_path.split(";") if os.path.splitext(f.lower())[1] in valid_extensions]
        
        if not images:
            messagebox.showerror(self.loc.get("error"), self.loc.get("no_images"))
            self.conversion_running = False
            return

        # Prepare conversion arguments
        needs_alpha_removal = output_format in ['jpg', 'jpeg', 'bmp']
        conversion_args = []
        
        lib = self.processing_lib.get()
        supported_input = SUPPORTED_FORMATS[lib]['input']
        
        # Фильтруем изображения по поддерживаемым форматам
        images = [img for img in images 
                 if os.path.splitext(img.lower())[1][1:] in supported_input]
        
        if not images:
            messagebox.showerror(self.loc.get("error"), 
                               "No supported images found for selected processing library")
            self.conversion_running = False
            return

        for input_path in images:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(input_path))[0]}.{output_format}"
            )
            conversion_args.append((input_path, output_path, output_format, needs_alpha_removal))

        # Запускаем конвертацию в отдельном потоке
        def conversion_thread():
            try:
                # Сбрасываем прогресс
                self.progress_convert.set(0)
                self.total_progress.set(0)
                
                # Конвертируем изображения
                errors = batch_convert(conversion_args, self.update_progress, batch_size=10)
                
                # Показываем результаты
                self.after(0, lambda: self.show_conversion_results(errors))
            finally:
                self.conversion_running = False
        
        threading.Thread(target=conversion_thread, daemon=True).start()

    def show_conversion_results(self, errors):
        """Показывает результаты конвертации с улучшенным дизайном"""
        if errors:
            dialog = CustomDialog(
                self,
                title=self.loc.get("error"),
                message="\n".join(
                    self.loc.get("conversion_error").format(path, error)
                    for path, error in errors
                ),
                button_color="red",
                button_hover_color="#8B0000"
            )
        else:
            dialog = CustomDialog(
                self,
                title=self.loc.get("success"),
                message=self.loc.get("conversion_complete"),
                button_color="green",
                button_hover_color="#006400"
            )
        dialog.wait_window()

    def merge_images(self):
        """Обновленная версия с исправленным скроллом"""
        if self.merge_running:
            return
            
        self.merge_running = True
        input_path = self.entry_merge.get()
        
        if not input_path:
            dialog = CustomDialog(
                self,
                title=self.loc.get("error"),
                message=self.loc.get("no_merge_images"),
                button_color="red",
                button_hover_color="#8B0000"
            )
            dialog.wait_window()
            self.merge_running = False
            return

        # Проверяем были ли добавлены диапазоны
        if not self.range_entries:
            dialog = CustomDialog(
                self,
                title=self.loc.get("error"),
                message=self.loc.get("no_merge_images"),
                button_color="red",
                button_hover_color="#8B0000"
            )
            dialog.wait_window()
            self.merge_running = False
            return

        # Кэшируем проверку расширений
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', 
                           '.webp', '.svg', '.pdf', '.eps', '.psd', '.heic',
                           '.avif', '.jpegxl', '.ico', '.ppm', '.rla', '.pcx',
                           '.pnm', '.xbm', '.tga', '.djvu'}

        if os.path.isdir(input_path):
            images = sorted([
                os.path.join(input_path, f) for f in os.listdir(input_path)
                if os.path.splitext(f.lower())[1] in valid_extensions
            ])
        else:
            images = sorted([f for f in input_path.split(";") if os.path.splitext(f.lower())[1] in valid_extensions])
        
        if not images:
            dialog = CustomDialog(
                self,
                title=self.loc.get("error"),
                message=self.loc.get("no_merge_images"),
                button_color="red",
                button_hover_color="#8B0000"
            )
            dialog.wait_window()
            self.merge_running = False
            return
        
        output_folder = filedialog.askdirectory(title=self.loc.get("select_save_folder"))
        if not output_folder:
            self.merge_running = False
            return
        
        def merge_thread():
            try:
                self.progress_merge.start()
                
                for i, (start_entry, end_entry) in enumerate(self.range_entries):
                    try:
                        start_index = int(start_entry.get()) - 1
                        end_index = int(end_entry.get())
                        range_images = images[start_index:end_index]
                        
                        if not range_images:
                            raise ValueError(f"No images in range {i + 1}")
                            
                        output_path = os.path.join(output_folder, f"{i + 1}.{self.merge_format_var.get()}")
                        merge_images_optimized(
                            range_images, 
                            direction=self.direction_var.get(),
                            output_path=output_path,
                            output_format=self.merge_format_var.get()
                        )
                        
                        # Обновляем прогресс
                        progress = (i + 1) / len(self.range_entries)
                        self.after(0, lambda p=progress: self.progress_merge.set(p))
                        
                    except Exception as e:
                        self.after(0, lambda: CustomDialog(
                            self,
                            title=self.loc.get("error"),
                            message=self.loc.get("saving_error").format(i + 1, str(e)),
                            button_color="red",
                            button_hover_color="#8B0000"
                        ).wait_window())
                        continue
                
                # Показываем сообщение об успешном завершении
                self.after(0, lambda: CustomDialog(
                    self,
                    title=self.loc.get("success"),
                    message=self.loc.get("merge_complete"),
                    button_color="green",
                    button_hover_color="#006400"
                ).wait_window())
                
            finally:
                self.merge_running = False
                self.after(0, lambda: self.progress_merge.stop())
                self.after(0, lambda: self.progress_merge.set(1))
        
        # Запускаем процесс склейки в отдельном потоке
        threading.Thread(target=merge_thread, daemon=True).start()

    def update_format_visibility(self):
        """Обновляет видимость форматов в зависимости от выбранной библиотеки"""
        lib = self.processing_lib.get()
        supported = SUPPORTED_FORMATS[lib]['output']
        
        # Автоматически восстанавливаем форматы в зависимости от библиотеки
        if lib == ProcessingLibrary.WAND:
            # Для Wand включаем все форматы
            self.visible_formats = [
                "PNG", "JPEG", "GIF", "WEBP", "BMP", "TIFF", "SVG", "PDF", 
                "EPS", "PSD", "HEIC", "AVIF", "JPEGXL", "ICO", "PPM",
                "RLA", "PCX", "PNM", "XBM", "TGA", "DJVU"
            ]
        elif lib == ProcessingLibrary.VIPS:
            # Для Pyvips включаем поддерживаемые форматы
            self.visible_formats = [
                fmt.upper() for fmt in SUPPORTED_FORMATS['vips']['output']
            ]
        elif lib == ProcessingLibrary.PIL:
            # Для PIL включаем только поддерживаемые форматы
            self.visible_formats = [
                fmt.upper() for fmt in SUPPORTED_FORMATS['pil']['output']
            ]
        else:  # CV2
            # Для OpenCV включаем только его форматы
            self.visible_formats = [
                fmt.upper() for fmt in SUPPORTED_FORMATS['cv2']['output']
            ]
        
        # Обновляем чекбоксы
        for fmt, var in self.format_vars.items():
            if lib == ProcessingLibrary.WAND:
                # Для Wand включаем все форматы
                var.set(fmt in self.visible_formats)
                self.format_vars[fmt]._checkbox.configure(state="normal")
            else:
                # Для других библиотек проверяем поддержку
                if fmt.lower() in supported:
                    var.set(True)  # Автоматически включаем поддерживаемые форматы
                    self.format_vars[fmt]._checkbox.configure(state="normal")
                else:
                    var.set(False)
                    self.format_vars[fmt]._checkbox.configure(state="disabled")
        
        # Обновляем интерфейс
        self.refresh_interface()

if __name__ == "__main__":
    app = AmiFile()
    app.mainloop()
