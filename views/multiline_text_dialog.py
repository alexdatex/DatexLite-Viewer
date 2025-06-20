import tkinter as tk
from tkinter import scrolledtext, ttk


class MultilineInputDialog(tk.Toplevel):
    def __init__(self, parent, title="Ввод текста", prompt="", width=40, height=10):
        super().__init__(parent)
        self.title(title)
        self.prompt = prompt
        self.width = width
        self.height = height
        self.result = None

        self._previous_grab = parent.grab_current() if parent else None

        self.create_widgets()
        self.setup_geometry()

        self.make_modal(parent)

        self.text_area.focus_set()

    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Подсказка
        if self.prompt:
            ttk.Label(main_frame, text=self.prompt).pack(anchor=tk.W)

        # Многострочное текстовое поле с прокруткой
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            width=self.width,
            height=self.height,
            wrap=tk.WORD,
            font=('Arial', 10),
            padx=5,
            pady=5
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.focus_set()

        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Кнопка Отмена
        ttk.Button(
            button_frame,
            text="Отмена",
            command=self.on_cancel
        ).pack(side=tk.RIGHT, padx=5)

        # Кнопка ОК
        ttk.Button(
            button_frame,
            text="ОК",
            command=self.on_ok
        ).pack(side=tk.RIGHT)

        # Обработка нажатия Enter (с модификатором Ctrl)
        self.text_area.bind("<Control-Return>", lambda e: self.on_ok())
        self.text_area.bind("<KP_Enter>", lambda e: self.on_ok())

    def setup_geometry(self):
        self.update_idletasks()

        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = self.winfo_width()
        height = self.winfo_height()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")
        self.geometry(f'+{x}+{y}')

        self.resizable(False, False)

    def make_modal(self, parent):
        """Настройка модального поведения с учетом родительского окна"""
        if parent:
            # Временно отпускаем grab родителя, если он есть
            if self._previous_grab:
                self._previous_grab.grab_release()

            # Делаем это окно модальным
            self.grab_set()

            # Устанавливаем отношение transient (для правильного отображения поверх)
            self.transient(parent)

        # Перехватываем закрытие окна через крестик
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        """Обработка нажатия кнопки OK"""
        self.result = self.text_area.get("1.0", tk.END).strip()
        self.cleanup_and_destroy()


    def on_cancel(self):
        """Обработка нажатия кнопки Отмена"""
        self.cleanup_and_destroy()

    def cleanup_and_destroy(self):
        """Восстановление grab и закрытие окна"""
        # Отпускаем наш grab
        self.grab_release()

        # Восстанавливаем предыдущий grab, если он был
        if self._previous_grab:
            self._previous_grab.grab_set()

        self.destroy()

    def show(self):
        """Показать диалог и дождаться результата"""
        self.wait_window()
        return self.result