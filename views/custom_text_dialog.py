import tkinter as tk
from tkinter import simpledialog, scrolledtext


class CustomTextDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt=""):
        self.prompt = prompt
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(pady=5)

        # Создаем многострочное текстовое поле
        self.text_area = scrolledtext.ScrolledText(
            master,
            width=40,  # Примерно 20 символов в ширину
            height=10,  # 10 строк
            wrap=tk.WORD,  # Перенос по словам
            font=('Arial', 10)
        )
        self.text_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        return self.text_area

    def apply(self):
        # Получаем текст из текстового поля
        self.result = self.text_area.get("1.0", tk.END).strip()