import logging
import time
from io import BytesIO

from PIL import Image


def resize_to_width_pillow(image_data: bytes, target_width: int = 800) -> bytes:
    """Уменьшает изображение до указанной ширины с сохранением пропорций (Pillow)"""
    with Image.open(BytesIO(image_data)) as img:
        # Рассчитываем новую высоту
        logging.info(f"\t\t\tШирина изображения : {img.width}  ( нужно : {target_width} )")
        if img.width > target_width:
            logging.info(f"\t\t\t\tТребуется уменьшение")
            width_percent = target_width / float(img.width)
            target_height = int(float(img.height) * float(width_percent))

            # Масштабируем
            img = img.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS
            )

            # Сохраняем в bytes
            output = BytesIO()
            img.save(output, format="PNG")
            return output.getvalue()
        else:
            logging.info(f"\t\t\t\tОбработка не требуется!")
            return image_data


def _format_size(size_in_bytes: int) -> str:
    """Форматирует размер в удобочитаемом виде (автоматически выбирает единицы)"""
    if size_in_bytes >= 1024 * 1024:  # Больше 1 МБ
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    elif size_in_bytes >= 1024:  # Больше 1 КБ
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} bytes"


def resize_image_to_width(image_data: bytes, target_width: int = 800):
    start_time = time.perf_counter()
    ret_value = resize_to_width_pillow(image_data, target_width)
    end_time = time.perf_counter()
    logging.info \
        (f"\t\tИзменения размера изображения с {_format_size(len(image_data))} до {_format_size(len(ret_value))} ({(end_time - start_time):.4f} сек)")
    return ret_value
