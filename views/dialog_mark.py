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

        if (point_mark == None and mark_id != None):
            mark = self.controller.get_mark(mark_id)
            logging.info(
                f"Открытие диалога показа деталей метки ID: {mark_id} (Координаты x: {mark.x:4d}, {mark.y:4d} )")
            self.point_mark = (mark.x, mark.y)
        else:
            logging.info(
                f"Открытие диалога добавления деталей НОВОЙ метки (Координаты x: {point_mark[0]:4d}, {point_mark[1]:4d} )")
            self.point_mark = point_mark

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

    def save(self):
        if self.mark_id:
            mark_data = {
                'name': self.entries["name"].get(),
                'description': self.entries["description"].get(),
                'spare_parts': self.spare_parts_var.get()
            }
            self.controller.update_mark(self.mark_id, mark_data)
            self.parent2.update_mark_information()
        else:
            x, y = self.point_mark
            mark_data = {
                'name': self.entries["name"].get(),
                'description': self.entries["description"].get(),
                'schema_id': self.schema_id,
                'x': x,
                'y': y,
                'spare_parts': self.spare_parts_var.get(),
                'user_id': self.parent2.user_id
            }
            mark = self.controller.add_mark(mark_data)
            self.mark_id = mark.id
            self.parent2.add_mark(mark.id)


        for key, item in self.tmpMarks.items():
            if self.mark_id:
                item['mark_id'] = self.mark_id
            self.controller.add_mark_image(item)

        for mark_image_id in self.list_id_mark_images_for_delete:
            self.controller.delete_mark_image(mark_image_id)

        self.destroy()

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

    def delete_image(self):
        self.image_comment_text.config(state=NORMAL)
        self.image_comment_text.delete(1.0, tk.END)
        self.image_comment_text.config(state=DISABLED)
        self.delete_mark_image_btn.config(state=DISABLED)

        selected_item = self.marks_list.selection()
        if selected_item:  # если что-то выделено
            item = self.marks_list.item(selected_item)
            mark_id = item['values'][0]

            if mark_id < 0:
                del self.tmpMarks[mark_id]
            else:
                self.list_id_mark_images_for_delete.append(mark_id)
            self.marks_list.delete(selected_item[0])
            self.clear_image_display()
            if self.marks_list.get_children():
                first_item = self.marks_list.get_children()[0]
                self.marks_list.selection_set(first_item)
                self.marks_list.focus(first_item)


    def add_image(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Выберите изображение",
            filetypes=(
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp"),
            )
        )
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    name = os.path.basename(file_path)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавление файла: {e}", parent=self)

            dialog = self.ask_multi_line_input(
                title="Введите текст",
                prompt="Пожалуйста, введите ваш текст (10 строк):",
                width=60,
                height=15
            )

            if dialog:
                description = dialog
            else:
                description = ""

            if self.mark_id:
                logging.info(f"Добавление изображения к метке {self.mark_id} файл {str(Path(file_path).absolute())}")
            else:
                logging.info(f"Добавление изображения к новой метке файл {str(Path(file_path).absolute())}")

            mark_data = {
                'name': name,
                'data': resize_image_to_width(file_data),
                'description': description,
                'mark_id': self.mark_id,
                'user_id': self.user_id
            }

            tmp_id = -self.tmp_image_id - 1
            self.tmpMarks[tmp_id] = mark_data
            self.tmp_image_id += 1
            self.marks_list.insert("", tk.END, values=(tmp_id, mark_data['name'], mark_data['description']))

    def on_mark_image_select(self, event):
        selected_item = self.marks_list.selection()
        if selected_item:
            item = self.marks_list.item(selected_item)
            mark_id = item['values'][0]
            self.update_mark_image_info(mark_id)

    def update_mark_image_info(self, mark_id):
        self.selected_mark_image_id = mark_id
        if mark_id < 0:
            tmp_mark = self.tmpMarks[mark_id]
            self.image_comment_text.config(state=NORMAL)
            self.image_comment_text.delete(1.0, tk.END)
            self.image_comment_text.insert(tk.END, tmp_mark['description'])
            self.image_comment_text.config(state=DISABLED)

            data = tmp_mark['data']
        else:
            item = self.controller.get_mark_image(mark_id)
            self.image_comment_text.config(state=NORMAL)
            self.image_comment_text.delete(1.0, tk.END)
            self.image_comment_text.insert(tk.END, item.description)
            self.image_comment_text.config(state=DISABLED)

            data = item.data

        self.display_image(data)

    def display_image(self, image_data):
        self.clear_image_display()

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
            logging.info(f"Error displaying image: {e}")

    def clear_image_display(self):
        self.image_canvas.delete("all")
        if hasattr(self.image_canvas, 'image'):
            del self.image_canvas.image

    def ask_multi_line_input(self, title="Ввод текста", prompt="", width=40, height=10):
        """Функция для вызова многострочного диалога ввода"""

        dialog = MultilineInputDialog(self, title, prompt, width, height)
        return dialog.show()
