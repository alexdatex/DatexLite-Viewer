import io
import logging
import os
import tkinter as tk
from pathlib import Path
from tkinter import Toplevel, Label, Entry, Frame, NORMAL
from tkinter import messagebox, DISABLED, filedialog
from tkinter import ttk

from PIL import Image, ImageTk

from constants import resize_image_to_width
from views.multiline_text_dialog import MultilineInputDialog


class MarkDialog(Toplevel):
    def __init__(self, parent, parent2, root, controller, main_root, user_id, schema_id, mark_id=None, point_mark=None):
        super().__init__(parent)
        self.parent2 = parent2
        self.controller = controller
        self.main_root = main_root
        self.mark_id = mark_id
        self.schema_id = schema_id
        self.user_id = user_id
        self.setup_ui()
        self.selected_mark_image_id = None

        mark = self.controller.get_mark(mark_id)
        logging.info(
            f"\t\tОткрытие диалога показа деталей метки ID: {mark_id} (Координаты x: {mark.x:4d}, {mark.y:4d} )")
        self.point_mark = (mark.x, mark.y)

        if mark_id:
            parent.after(100, self.fill_form)

    def setup_ui(self):
        self.title("Просмотр данных для метки")
        self.geometry("800x650")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = 800
        height = 650

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f'+{x}+{y}')

        self.resizable(False, False)

        self.resizable(False, False)
        self.iconphoto(False, self.main_root.icon_photo)
        self.grab_set()

        form_frame = Frame(self, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)

        form_frame_info = Frame(form_frame, padx=10, pady=10)
        form_frame_info.pack(fill="both", expand=True)

        self.entries = {}
        self.text_entries = {}

        Label(form_frame_info, text="Название").grid(row=1, column=0, sticky="e", pady=5)
        entry_text = tk.StringVar()
        entry = Entry(form_frame_info, width=30, textvariable=entry_text)
        entry.grid(row=1, column=1, pady=5)
        self.entries["name"] = entry
        self.text_entries["name"] = entry_text

        Label(form_frame_info, text="Артикул оборудования").grid(row=2, column=0, sticky="e", pady=5)
        entry_text = tk.StringVar()
        entry = Entry(form_frame_info, width=30, textvariable=entry_text)
        entry.grid(row=2, column=1, pady=5)
        self.entries["description"] = entry
        self.text_entries["description"] = entry_text

        self.spare_parts_var = tk.BooleanVar(value=False)
        important_check = ttk.Checkbutton(form_frame_info, text="Зап. часть", variable=self.spare_parts_var)
        important_check.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.paned_window = tk.PanedWindow(form_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.create_left_panel()
        self.create_right_panel()

        button_frame = Frame(form_frame)
        button_frame.pack(pady=10)

        self.list_id_mark_images_for_delete = []
        self.tmpMarks = {}
        self.tmp_image_id = 0

        ttk.Button(button_frame, text="Закрыть", command=self.destroy).pack(side="left", padx=5)

    def create_left_panel(self):
        self.left_panel = ttk.Frame(self.paned_window, width=150)
        self.paned_window.add(self.left_panel, minsize=150)

        self.tree_frame = ttk.Frame(self.left_panel)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.marks_list = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="browse",
                                       columns=("id", "name", "description"), show="headings")
        self.marks_list.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.marks_list.yview)

        # Настройка колонок
        self.marks_list.heading("id", text="ID", anchor=tk.W)
        self.marks_list.heading("name", text="Название", anchor=tk.W)
        self.marks_list.heading("description", text="Комментарий", anchor=tk.W)

        self.marks_list.column("id", width=0, stretch=tk.NO, minwidth=0)
        self.marks_list.column("name", width=50, stretch=tk.YES, minwidth=50)
        self.marks_list.column("description", width=100, stretch=tk.YES, minwidth=100)

        self.marks_list.bind("<<TreeviewSelect>>", self.on_mark_image_select)

        button_frame = Frame(self.left_panel)
        button_frame.pack(pady=10)

    def create_right_panel(self):
        self.right_panel = ttk.Frame(self.paned_window, width=500)
        self.paned_window.add(self.right_panel, minsize=500)

        top_panel = ttk.Frame(self.right_panel, width=500)
        top_panel.pack(fill="both", expand=True)

        self.image_canvas = tk.Canvas(top_panel, bg='white')
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        button_frame = Frame(self.right_panel)
        button_frame.pack(fill="both", expand=True)

        Label(button_frame, text="Комментарий").grid(row=0, column=0, sticky="e", pady=5)
        self.image_comment_text = tk.Text(button_frame, height=6, width=60, wrap=tk.WORD)
        self.image_comment_text.grid(row=0, column=5, columnspan=4, sticky=tk.EW)
        self.image_comment_text.config(state=DISABLED)

    def fill_form(self):
        mark = self.controller.get_mark(self.mark_id)
        mark_images = self.controller.get_mark_images(self.mark_id)

        logging.info(f"\t\t\tДля метки {self.mark_id} получено {len(mark_images)} изображений")
        for element in mark_images:
            if element.data is None:
                logging.info(f"\t\t\t\t {element.id} : '{element.description}' : (None)")
            else:
                logging.info(f"\t\t\t\t {element.id} : '{element.description}' : {len(element.data)} байт")

        self.text_entries["name"].set(mark.name)
        self.text_entries["description"].set(mark.description)
        self.spare_parts_var.set(mark.spare_parts)

        for item in self.marks_list.get_children():
            self.marks_list.delete(item)

        if len(mark_images) > 0:
            for item in mark_images:
                self.marks_list.insert("", tk.END, values=(item.id, mark.name, item.description))

            first_item = self.marks_list.get_children()[0]
            self.marks_list.selection_set(first_item)
            self.marks_list.focus(first_item)

    def on_mark_image_select(self, event):

        selected_item = self.marks_list.selection()
        if selected_item:
            item = self.marks_list.item(selected_item)
            mark_id = item['values'][0]
            self.update_mark_image_info(mark_id)

    def update_mark_image_info(self, mark_id):
        logging.info(f"\t\t\t\tВыбрано изображение {mark_id} для метки {self.mark_id} ")
        self.selected_mark_image_id = mark_id

        item = self.controller.get_mark_image(mark_id)
        self.image_comment_text.config(state=NORMAL)
        self.image_comment_text.delete(1.0, tk.END)
        self.image_comment_text.insert(tk.END, item.description)
        self.image_comment_text.config(state=DISABLED)

        data = item.data

        self.display_image(data)

    def display_image(self, image_data):
        self.clear_image_display()
        if image_data:
            logging.info(f"\t\t\t\t\tПоказ картинки: размер {len(image_data)}")
        else:
            logging.info(f"\t\t\t\t\tПоказ картинки: Изображения нет")
            return

        try:
            image = Image.open(io.BytesIO(image_data))

            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()

            img_width, img_height = image.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)

            image = image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2

            self.image_canvas.image = photo  # Keep a reference
            self.image_canvas.create_image(x, y, image=photo, anchor=tk.NW)
        except Exception as e:
            logging.info(f"\t\t\t\t\tОшибка отображения картинки {self.selected_mark_image_id} для метки {self.mark_id} : {e}")

    def clear_image_display(self):
        self.image_canvas.delete("all")
        if hasattr(self.image_canvas, 'image'):
            del self.image_canvas.image

    def ask_multi_line_input(self, title="Ввод текста", prompt="", width=40, height=10):
        """Функция для вызова многострочного диалога ввода"""

        dialog = MultilineInputDialog(self, title, prompt, width, height)
        return dialog.show()
