import sys
from datetime import datetime
import logging
import os
import os.path
import tkinter as tk
from configparser import ConfigParser
from pathlib import Path
from tkinter import ttk, messagebox, DISABLED

from PIL import ImageTk

from constants.constants import INI_FILE
from constants.icons import image
from constants.status_states import StatusStates
from db import DBController, Database
from tabs import ComponentInfoTab, SchemaInfoTab
from version import VERSION


class DatexLite:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._setup_auth_window()
        self._init_users()
        self._setup_ui()

        if os.getenv("APP_DEBUG", "false").lower() == "true":
            self.current_user = {'login': 'Admin', 'id': 0}
            self.root.destroy()
            self._run_main_app()


    def _setup_auth_window(self) -> None:
        """Настройка окна авторизации."""
        self.root.title("Авторизация")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

    def _init_db_connection(self) -> None:
        """Инициализация подключения к базе данных."""
        # self.database = Database(echo=True)
        self.database = Database()
        self.db = self.database.get_session()
        self.db_controller = DBController(self.db)

    def _init_users(self) -> None:
        """Инициализация тестовых пользователей."""
        self.users = [
            {"login": "admin", "password": "admin123", "id": 1},
            {"login": "control", "password": "password", "id": 2},
        ]
        self.user_id = 0
        self.current_user = None
        self.current_component_id = -1

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self._configure_styles()
        self.center_window(self.root)

        main_frame = self._create_main_frame()
        self._create_login_fields(main_frame)
        self._create_login_button(main_frame)
        self._configure_grid_layout(main_frame)

    def _configure_styles(self) -> None:
        """Конфигурация стилей виджетов."""
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Arial', 10))
        style.configure("TButton", padding=5, font=('Arial', 10))

    def _create_main_frame(self) -> ttk.Frame:
        """Создание основного фрейма авторизации."""
        main_frame = ttk.Frame(self.root, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame

    def center_window(self, main_frame):
        main_frame.update_idletasks()
        width = main_frame.winfo_width()
        height = main_frame.winfo_height()
        x = (main_frame.winfo_screenwidth() // 2) - (width // 2)
        y = (main_frame.winfo_screenheight() // 2) - (height // 2)
        main_frame.geometry(f'+{x}+{y}')

    def _create_login_fields(self, parent: ttk.Frame) -> None:
        """Создание полей для ввода логина и пароля."""
        # Поле логина
        ttk.Label(parent, text="Логин:").grid(row=0, column=0, sticky=tk.W)
        self.login_entry = ttk.Entry(parent)
        self.login_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)

        # Поле пароля
        ttk.Label(parent, text="Пароль:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(parent, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, sticky=tk.EW)
        self.password_entry.bind("<Return>", lambda e: self.check_credentials())

    def _create_login_button(self, parent: ttk.Frame) -> None:
        """Создание кнопки входа."""
        login_btn = ttk.Button(
            parent,
            text="Войти",
            command=self.check_credentials
        )
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def _configure_grid_layout(self, frame: ttk.Frame) -> None:
        """Конфигурация сетки layout."""
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        self.login_entry.focus()

    def check_credentials(self) -> None:
        """Проверка учетных данных пользователя."""
        login = self.login_entry.get()
        password = self.password_entry.get()

        for user in self.users:
            if user["login"] == login and user["password"] == password:
                self.current_user = user
                self.root.destroy()
                self._run_main_app()
                return

        messagebox.showerror("Ошибка", "Неверный логин или пароль")
        self.password_entry.delete(0, tk.END)

    def _run_main_app(self) -> None:
        """Запуск основного окна приложения."""
        logging.info(f"DATEX Lite - Просмоторщик (Пользователь: {self.current_user['login']}) ver. {VERSION:03d}")
        logging.info(f"Пользователь: {self.current_user['login']} (ID: {self.current_user['id']}) ver. {VERSION:03d}")
        self.main_root = tk.Tk()

        self.main_root.title(f"DATEX Lite (Пользователь: {self.current_user['login']}) ver. {VERSION:03d}")

        self._init_db_connection()
        self._init_window_settings()
        self.user_id = self.current_user['id']
        self._create_main_interface()

        icon_photo = ImageTk.PhotoImage(image)

        # Сохраняем ссылку, чтобы изображение не удалилось
        self.icon_photo = icon_photo

        self.main_root.iconphoto(False, self.icon_photo)
        self._load_and_setup_ui()

        self.main_root.mainloop()

    def _init_window_settings(self) -> None:
        """Инициализация настроек окна."""
        self.main_root.minsize(800, 800)
        self.default_width = 1000
        self.default_height = 800
        self.default_x = None
        self.default_y = None
        self.config = ConfigParser()
        self.config_file = INI_FILE
        self.main_root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Дополнительные поля (изначально скрыты)
        self.extra_fields = []
        # Переменная для отслеживания состояния
        self.fields_visible = False

    def _create_main_interface(self) -> None:
        """Создание основного интерфейса приложения."""
        self._create_paned_window()
        self._create_left_panel()
        self._create_right_panel()

    def _create_paned_window(self) -> None:
        # Создаем toolbar (фрейм вверху окна)
        toolbar = tk.Frame(self.main_root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        exit_btn = ttk.Button(toolbar, text="Выход", command=self.on_closing)
        exit_btn.pack(side=tk.RIGHT, padx=2, pady=2)

        """Создание разделяемого окна."""
        self.paned_window = tk.PanedWindow(
            self.main_root,
            orient=tk.HORIZONTAL,
            sashrelief=tk.RAISED,
            sashwidth=5
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_panel = tk.Frame(self.paned_window, width=100)
        self.right_panel = tk.Frame(self.paned_window)

        self.paned_window.add(self.left_panel)
        self.paned_window.add(self.right_panel)
        self.paned_window.paneconfigure(self.left_panel, minsize=150)

    def _create_left_panel(self) -> None:
        """Создание левой панели со списком оборудования."""
        self._create_filters()
        self._create_treeview_frame()

    def _create_treeview_frame(self) -> None:
        """Создание фрейма с Treeview."""
        self.tree_frame = ttk.Frame(self.left_panel)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._configure_equipment_tree()

    def _sort_treeview_column(self, col: str) -> None:
        """Сортировка Treeview по указанной колонке."""
        # Получаем текущее состояние сортировки для колонки
        reverse = self.sort_states[col]

        # Получаем все элементы
        items = [(self.equipments_list.set(k, col), k) for k in self.equipments_list.get_children('')]

        # Сортируем в зависимости от типа данных
        if col == "id":  # Числовая сортировка для ID
            try:
                items.sort(key=lambda t: int(t[0]), reverse=reverse)
            except ValueError:
                items.sort(reverse=reverse)
        else:  # Текстовая сортировка для остальных колонок
            items.sort(reverse=reverse)

        # Перемещаем элементы в отсортированном порядке
        for index, (_, k) in enumerate(items):
            self.equipments_list.move(k, '', index)

        # Обновляем состояние сортировки и заголовок
        self.sort_states[col] = not reverse
        self._update_column_heading(col, not reverse)

    def _update_column_heading(self, col: str, reverse: bool) -> None:
        """Обновление заголовка колонки с указанием направления сортировки."""
        # Получаем исходный текст заголовка (без стрелки)
        original_text = next(
            v["text"] for k, v in {
                "id": {"text": "ID"},
                "group_name": {"text": "Группа"},
                # "korpus": {"text": "Корпус по ГП"},
                # "position": {"text": "Позиция"},
                "code": {"text": "Номер"},
                "name": {"text": "Название"},
                "type": {"text": "Тип"},
                "purpose": {"text": "Назначение"},
                "manufacturer": {"text": "Производитель"}
            }.items() if k == col
        )

        # Устанавливаем новый текст с символом стрелки
        arrow = " ↓" if reverse else " ↑"
        self.equipments_list.heading(col, text=original_text + arrow)

    def _configure_equipment_tree(self) -> None:
        self.equipments_list = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=self.tree_scroll.set,
            selectmode="browse",
            columns=("id",
                     "group_name",
                     "code", "name",
                     "type",
                     "purpose",
                     "manufacturer",
                     ),
            show="headings"
        )

        self.equipments_list.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.equipments_list.yview)

        # Настройка колонок
        columns = {
            "id": {"text": "ID", "width": 0, "stretch": tk.NO, "minwidth": 0},
            "group_name": {"text": "Группа", "width": 50, "stretch": tk.YES, "minwidth": 50},
            "code": {"text": "Номер", "width": 50, "stretch": tk.YES, "minwidth": 50},
            "name": {"text": "Название", "width": 200, "stretch": tk.YES, "minwidth": 50},
            "type": {"text": "Тип", "width": 50, "stretch": tk.YES, "minwidth": 50},
            "purpose": {"text": "Назначение", "width": 50, "stretch": tk.YES, "minwidth": 50},
            "manufacturer": {"text": "Производитель", "width": 50, "stretch": tk.YES, "minwidth": 50}
        }

        self.sort_states = {col: False for col in columns}

        for col, params in columns.items():
            self.equipments_list.heading(col,
                                         text=params["text"],
                                         command=lambda c=col: self._sort_treeview_column(c),
                                         anchor=tk.W)
            self.equipments_list.column(col, width=params["width"],
                                        stretch=params["stretch"],
                                        minwidth=params["minwidth"])

        self.equipments_list.bind("<<TreeviewSelect>>", self.on_equipments_list_select)

    def _create_filters(self):
        button_frame = ttk.Frame(self.left_panel)
        button_frame.pack(fill="x", padx=20, pady=5)

        self.toggle_button = ttk.Button(
            button_frame,
            text="Показать фильтр",
            command=self.toggle_fields
        )
        self.toggle_button.pack(pady=10)

        self.extra_container = ttk.Frame(button_frame)
        # Список названий дополнительных полей
        field_labels = [
            ("Корпус по ГП", "korpus"),
            ("Позиция", "position"),
            ("Технологический номер", "code"),
            ("Наименование оборудования", "name"),
            ("Тип", "type"),
            ("Назначение", "purpose"),
            ("Производитель", "manufacturer"),
            ("Группа", "group_name"),
            ("Аудит выполнен", "is_audit_completed")
        ]
        self.extra_entries = []
        self.text_entries = {}
        for i, (text, name) in enumerate(field_labels):
            entry_text = tk.StringVar()
            frame = ttk.Frame(self.extra_container)
            frame.pack(fill='x', padx=20, pady=5)
            ttk.Label(frame, text=text).pack(side='left')

            if name == "is_audit_completed":
                combobox = ttk.Combobox(frame, values=[""] + StatusStates.get_combobox_values())
                combobox.pack(side='right', expand=True, fill='x')
                combobox.set("")
                self.text_entries[name] = combobox
            else:
                entry = ttk.Entry(frame, width=30, textvariable=entry_text)
                entry.pack(side='right', expand=True, fill='x')
                self.extra_entries.append(entry)
                self.text_entries[name] = entry_text

        add_btn = ttk.Button(
            self.extra_container,
            text="Фильтровать",
            command=self.update_equipments_list
        )
        add_btn.pack(side="left", padx=5)

    def _create_right_panel(self) -> None:
        """Создание правой панели с информацией."""
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.component_info_tab = ComponentInfoTab(
            self.notebook,
            self.db_controller,
            self
        )
        self.schema_info_tab = SchemaInfoTab(
            self.notebook,
            self.db_controller,
            self,
            self.main_root
        )

        self.notebook.add(self.component_info_tab.frame, text="Данные оборудования")
        self.notebook.add(self.schema_info_tab.frame, text="Схема оборудования")

    def toggle_fields(self):
        if not self.fields_visible:
            # Показываем дополнительные поля перед кнопкой отправки
            self.extra_container.pack(fill='x', pady=10)
            self.toggle_button.config(text="Скрыть фильтр и очистить")
            # self.submit_button.config(state='normal')
        else:
            # Скрываем дополнительные поля
            self.extra_container.pack_forget()
            self.toggle_button.config(text="Показать фильтр")
            for field in self.text_entries:
                field_widget = self.text_entries[field]
                if isinstance(field_widget, ttk.Combobox):
                    field_widget.set("")
                else:
                    field_widget.set("")
            # self.submit_button.config(state='disabled')

        self.fields_visible = not self.fields_visible

        if not self.fields_visible:
            self.update_equipments_list()

    def _load_and_setup_ui(self) -> None:
        """Загрузка данных и настройка интерфейса."""
        self.update_equipments_list()
        self.load_settings()
        self.setup_initial_layout()

    def update_equipments_list(self) -> None:
        """Обновление списка оборудования."""
        self.empty_component_info()

        for item in self.equipments_list.get_children():
            self.equipments_list.delete(item)

        if not self.fields_visible:
            components = self.db_controller.get_components()
        else:
            components = self.db_controller.get_components(self.text_entries)

        if components:
            for equipment in components:
                self.insert_to_equipments_list(equipment)

        if self.equipments_list.get_children():
            first_item = self.equipments_list.get_children()[0]
            self.equipments_list.selection_set(first_item)
            self.equipments_list.focus(first_item)

    def setup_initial_layout(self) -> None:
        """Настройка начального расположения элементов."""
        geometry = f"{self.window_width}x{self.window_height}"
        if self.window_x and self.window_y:
            geometry += f"+{self.window_x}+{self.window_y}"
        self.main_root.geometry(geometry)

    def load_settings(self) -> None:
        """Загрузка настроек из файла."""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                self.window_width = self.config.getint(
                    'Window', 'width', fallback=self.default_width
                )
                self.window_height = self.config.getint(
                    'Window', 'height', fallback=self.default_height
                )
                self.window_x = self.config.getint(
                    'Window', 'x', fallback=self.default_x
                )
                self.window_y = self.config.getint(
                    'Window', 'y', fallback=self.default_y
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки настроек: {e}", parent=self)
                self.reset_to_defaults()
        else:
            self.reset_to_defaults()

    def save_settings(self) -> None:
        """Сохранение текущих настроек в файл."""
        try:
            self.config['Window'] = {
                'width': self.main_root.winfo_width(),
                'height': self.main_root.winfo_height(),
                'x': self.main_root.winfo_x(),
                'y': self.main_root.winfo_y(),
            }
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения настроек: {e}")

    def on_equipments_list_select(self, event: tk.Event) -> None:
        """Обработчик выбора элемента в Treeview."""
        selected = self.equipments_list.selection()
        if selected:
            item = self.equipments_list.item(selected)
            self.update_component_info(item['values'][0])

    def update_equipment(self, equipment_id: int, data: dict) -> None:
        logging.info(f"Обновление данных оборудования ID {equipment_id}")
        equipment = self.db_controller.get_component(equipment_id)
        if equipment:
            for key, value in data.items():
                if key != "id":
                    setattr(equipment, key, value)
            self.db.commit()
            self.current_component_id = -1
            self.empty_component_info()
            self.update_equipments_list()
            self.select_row_by_column1_value(equipment.id)

    def select_row_by_column1_value(self, value):
        items = self.equipments_list.get_children()

        # Ищем элемент с нужным значением в первой колонке
        for item in items:
            if self.equipments_list.item(item, 'values')[0] == str(value):
                # Устанавливаем фокус и выделение
                self.equipments_list.selection_set(item)
                self.equipments_list.focus(item)
                self.equipments_list.see(item)
                return True
        return False

    def delete_equipment(self) -> None:
        answer = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы точно хотите удалить это оборудование?",
            icon='warning'
        )
        if answer:
            self.db_controller.delete_equipment(self.current_component_id)
            self.delete_btn.config(state=tk.DISABLED)
            self.current_component_id = -1
            self.empty_component_info()
            self.update_equipments_list()

    def update_component_info(self, component_id: int) -> None:
        """Обновление информации о компоненте."""
        logging.info(f"Чтение данных по компоненту ID: {component_id}")
        self.current_component_id = component_id
        self.component_info_tab.update(component_id)
        self.schema_info_tab.update(component_id)

    def empty_component_info(self) -> None:
        """Очистка информации о компоненте."""
        self.current_component_id = -1
        self.component_info_tab.clean()
        self.schema_info_tab.clean()

    def on_closing(self) -> None:
        """Обработчик закрытия приложения."""
        self.database.close()
        self.save_settings()
        self.main_root.destroy()

    def reset_to_defaults(self) -> None:
        """Сброс настроек к значениям по умолчанию."""
        self.window_width = self.default_width
        self.window_height = self.default_height
        self.window_x = self.default_x
        self.window_y = self.default_y

    def insert_to_equipments_list(self, equipment):
        self.equipments_list.insert("", tk.END,
                                    values=(equipment.id, equipment.code,
                                            equipment.group_name,
                                            equipment.name,
                                            equipment.type,
                                            equipment.purpose,
                                            equipment.manufacturer)
                                    )


def _setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"DatexLite_{timestamp}.log"

    # Проверяем переменную окружения
    debug_mode = os.getenv("APP_DEBUG", "false").lower() == "true"

    logging.getLogger().handlers = []

    # Создаем FileHandler для записи в новый файл
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')

    # Создаем Formatter для определения формата записи
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Добавляем FileHandler к logger
    logging.getLogger().addHandler(file_handler)

    if debug_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    _setup_logging()
    root = tk.Tk()
    app = DatexLite(root)
    root.mainloop()
