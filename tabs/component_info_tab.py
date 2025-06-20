import tkinter as tk
from tkinter import ttk, DISABLED

from constants.status_states import StatusStates

import logging

class ComponentInfoTab:
    def __init__(self, parent, db_service, root):
        self.db_service = db_service
        self.current_component_id = -1
        self.root = root

        self.frame = tk.Frame(parent, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        self.frame_info = tk.Frame(self.frame, padx=10, pady=10)
        self.frame_info.pack(fill="both", expand=True)

        fields = [
            ("Корпус по ГП:", "korpus"),
            ("Технологический номер:", "code"),
            ("Наименование оборудования:", "name"),
            ("Назначение:", "purpose"),
            ("Производитель:", "manufacturer"),
            ("Тип:", "type"),
            ("Серийный номер:", "serial_number"),
            ("Дата изготовления (год):", "production_date"),
            ("Группа:", "group_name"),
            ("Аудит выполнен:", "is_audit_completed"),
            ("Позиция:", "position")
        ]

        self.entries = {}
        self.text_entries = {}

        for i, (text, name) in enumerate(fields):
            ttk.Label(self.frame_info, text=text).grid(row=i, column=0, sticky="e", pady=5)

            if name == "position":  # Многострочное поле
                text_widget = tk.Text(self.frame_info, width=30, height=10, wrap="word")
                scrollbar = tk.Scrollbar(self.frame_info, command=text_widget.yview)
                text_widget.config(yscrollcommand=scrollbar.set)

                text_widget.grid(row=i, column=1, pady=5, sticky="ns")
                scrollbar.grid(row=i, column=2, sticky="ns")

                text_widget.config(state="normal")
                text_widget.config(state="disabled")
                self.entries[name] = text_widget
                self.text_entries[name] = text_widget
            else:
                if name == "is_audit_completed":
                    combobox = ttk.Combobox(self.frame_info, values=StatusStates.get_combobox_values(),
                                            state="disabled")
                    combobox.grid(row=i, column=1, pady=5)
                    combobox.set("Нет, в процессе")  # Устанавливаем значение по умолчанию
                    self.entries[name] = combobox
                    self.text_entries[name] = combobox
                else:
                    entry_text = tk.StringVar()
                    entry = tk.Entry(self.frame_info, width=30, textvariable=entry_text)
                    entry.grid(row=i, column=1, pady=5)
                    entry.config(state="readonly")
                    self.entries[name] = entry
                    self.text_entries[name] = entry_text


    def update(self, component_id):
        self.current_component_id = component_id
        equipment = self.db_service.get_component(component_id)
        self.update_entries_from_equipment(equipment)

    def update_entries_from_equipment(self, equipment):
        """Обновляет все поля формы из атрибутов объекта equipment"""
        for field_name, field_widget in self.text_entries.items():
            # Получаем значение из equipment или пустую строку по умолчанию
            field_value = getattr(equipment, field_name, "")

            # Обработка для виджета Text
            if isinstance(field_widget, tk.Text):
                self._update_text_widget(field_widget, field_value)
                continue

            # Обработка для Combobox
            if isinstance(field_widget, ttk.Combobox):
                self._update_combobox_widget(field_widget, field_value)
                continue

            # Обработка для всех остальных виджетов (Entry, Spinbox и т.д.)
            self._update_standard_widget(field_widget, field_value)

    def _update_text_widget(self, widget, value):
        """Обновляет содержимое текстового виджета"""
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", str(value))
        widget.config(state=tk.DISABLED)

    def _update_combobox_widget(self, widget, value):
        widget.set(StatusStates.get_text_by_id(value))

    def _update_standard_widget(self, widget, value):
        try:
            widget.set(str(value))
        except AttributeError:
            widget.delete(0, tk.END)
            widget.insert(0, str(value))

    def clean(self):
        self.current_component_id = -1
        value = ""
        for name, entry in self.text_entries.items():
            if isinstance(entry, tk.Text):
                entry.config(state="normal")
                entry.delete("1.0", tk.END)
                entry.insert("1.0", value)
                entry.config(state=tk.DISABLED)
            else:
                entry.set(value)
