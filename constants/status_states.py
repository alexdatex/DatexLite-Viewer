# Файл: status_states.py
from typing import Dict, List, Tuple, Union


class StatusStates:
    """
    Класс для работы со статусами, содержащий:
    - ID и текстовые представления статусов
    - Методы для конвертации между разными форматами
    - Методы для работы с UI-элементами
    """

    # Константы статусов с ID и текстом
    NO = (0, "Нет")
    IN_PROGRESS = (1, "В процессе")
    YES = (2, "Да")

    # Словарь соответствий значений статусам
    VALUE_MAPPING: Dict[Tuple[int, str], List[Union[bool, int, str]]] = {
        NO: [False, 0, "0", "Нет", "нет", "НЕТ", "no", "No", "NO"],
        IN_PROGRESS: [None, "В процессе", "в процессе", "In Progress", "in progress", "1"],
        YES: [True, 1, "1", "Да", "да", "ДА", "yes", "Yes", "YES"]
    }

    @classmethod
    def get_status(cls, value: Union[bool, int, str]) -> Tuple[int, str]:
        """Возвращает кортеж (ID, текст) для переданного значения"""
        for status, values in cls.VALUE_MAPPING.items():
            if str(value).lower() in [str(v).lower() for v in values]:
                return status
        return cls.IN_PROGRESS  # Значение по умолчанию

    @classmethod
    def get_text_by_id(cls, status_id: int) -> str:
        """Возвращает текст статуса по ID"""
        for status in cls.VALUE_MAPPING.keys():
            if status[0] == status_id:
                return status[1]
        return cls.IN_PROGRESS[1]  # Значение по умолчанию

    @classmethod
    def get_id_by_text(cls, text: str) -> int:
        """Возвращает ID статуса по тексту"""
        for status in cls.VALUE_MAPPING.keys():
            if status[1].lower() == text.lower():
                return status[0]
        return cls.IN_PROGRESS[0]  # Значение по умолчанию

    @classmethod
    def get_combobox_values(cls) -> List[str]:
        """Возвращает список текстовых значений для ComboBox"""
        return [status[1] for status in sorted(cls.VALUE_MAPPING.keys())]

    @classmethod
    def get_all_statuses(cls) -> List[Tuple[int, str]]:
        """Возвращает список всех статусов в виде кортежей (ID, текст)"""
        return sorted(cls.VALUE_MAPPING.keys())
