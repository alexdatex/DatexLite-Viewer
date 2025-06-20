import io
import logging
import os
import tkinter as tk
from tkinter import Toplevel, Frame, messagebox
from tkinter import ttk, filedialog, simpledialog
from tkinter.constants import DISABLED, NORMAL

from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk

from views.dialog_mark import MarkDialog
import re


class SchemeDialog(Toplevel):
    def __init__(self, parent, root, db_service, main_root, user_id, schema_id):
        super().__init__(parent)
        self.main_root = main_root
        self.db_service = db_service
        self.schema_id = schema_id
        self.user_id = user_id
        self.annotations = []
        self.current_mark_id = -1
        self.selected_annotation = None
        self.selected_annotation_box = None
        self.image_data = None
        self.temp_bbox = {}
        self.ann_color = {}
        self.canvas_ann = {}
        self.scale_factor = 1.0
        self.scale_options = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
        self.last_canvas_size = (0, 0)
        self.schema = None
        self.original_image = None
        self.setup_ui()

        logging.info(f"Открытие диалога показа меток для схемы с ID: {schema_id}")

        if schema_id:
            parent.after(100, self.load_data)

    def load_data(self):
        self.load_image()
        self.fill_list_marks()

    def setup_ui(self):
        self.title("Просмотр меток на схеме")
        self.geometry("900x900")
        self.resizable(True, True)
        self.wm_minsize(800, 800)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        width = 900
        height = 900

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f'+{x}+{y}')

        self.iconphoto(False, self.main_root.icon_photo)

        self.grab_set()

        form_frame = Frame(self, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)

        self.paned_window = tk.PanedWindow(form_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_panel = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.left_panel, minsize=200)

        self.right_panel = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.right_panel, minsize=600)

        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
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
        self.marks_list.heading("description", text="Артикул оборудования", anchor=tk.W)
        self.marks_list.column("id", width=0, stretch=tk.NO, minwidth=0)
        self.marks_list.column("name", width=50, stretch=tk.YES, minwidth=50)
        self.marks_list.column("description", width=100, stretch=tk.YES, minwidth=100)

        self.marks_list.bind('<Double-1>', self.on_mark_click)
        self.marks_list.bind("<<TreeviewSelect>>", self.on_mark_select)

    def create_right_panel(self):
        button_frame = ttk.Frame(self.right_panel)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.scale_var = tk.StringVar()

        ttk.Label(button_frame, text="Масштаб: ").pack(side=tk.LEFT, padx=5)
        self.scale_combobox = ttk.Combobox(
            button_frame,
            textvariable=self.scale_var,
            values=[f"{int(opt * 100)}%" for opt in self.scale_options],
            state="readonly"
        )

        self.scale_combobox.pack(side=tk.LEFT, padx=5)
        self.scale_combobox.bind("<<ComboboxSelected>>", self.on_scale_change)
        self.scale_combobox.current(3)  # 100% по умолчанию

        self.canvas_container = ttk.Frame(self.right_panel)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)
        self.create_cansas(self.canvas_container)

    def create_cansas(self, canvas_container):
        # Создаем Canvas с прокруткой внутри canvas_container
        self.canvas = tk.Canvas(canvas_container, bg='#333333', highlightthickness=0)

        # Добавляем скроллбары
        self.h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Размещаем элементы с помощью grid
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)

        # Настраиваем расширение grid
        self.canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_container.grid_columnconfigure(0, weight=1)

        # Привязка событий изменения размера
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.last_canvas_size = (0, 0)

    def on_canvas_click(self, event):
        if (self.canvas["cursor"] == 'cross'):
            img_x = self.canvas.canvasx(event.x)
            img_y = self.canvas.canvasy(event.y)
            logging.info(f"img_x : {img_x}, img_y : {img_y}")
            self.canvas.config(cursor='')
            point_mark = (int(img_x / self.scale_factor), int(img_y / self.scale_factor))
            MarkDialog(self, self, None, self.db_service, self.main_root, self.user_id, self.schema_id, None,
                       point_mark)
        else:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            for i, ann in enumerate(self.annotations):
                if (ann['x'] <= x <= ann['x'] + ann['width'] and
                        ann['y'] <= y <= ann['y'] + ann['height']):
                    self.change_selection_in_list(ann['id'])
                    break

    def on_canvas_double_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        for i, ann in enumerate(self.annotations):
            if (ann['x'] <= x <= ann['x'] + ann['width'] and
                    ann['y'] <= y <= ann['y'] + ann['height']):
                MarkDialog(self, self, None, self.db_service, self.main_root, self.user_id, self.schema_id,
                           ann['id'])
                break

    def auto_select_scale(self, image_data):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width = image_data.width
        img_height = image_data.height

        if canvas_width <= 1 or canvas_height <= 1:  # Если canvas еще не инициализирован
            return

        # Вычисляем оптимальный масштаб
        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        optimal_scale = min(width_ratio, height_ratio, 1.5)  # Не больше 100%

        # Находим ближайший вариант из доступных
        closest_scale = min(self.scale_options, key=lambda x: abs(x - optimal_scale))
        self.scale_factor = closest_scale

        # Устанавливаем значение в комбобоксе
        scale_index = self.scale_options.index(closest_scale)
        self.scale_combobox.current(scale_index)

    def on_scale_change(self, event):
        selected = self.scale_var.get()
        scale_str = selected.rstrip("%")
        self.scale_factor = float(scale_str) / 100
        self.load_image()

    def on_canvas_resize(self, event):
        # Проверяем, действительно ли изменился размер
        if (self.last_canvas_size == (event.width, event.height)) or not self.original_image:
            return

        self.last_canvas_size = (event.width, event.height)

        # Автомасштабирование только если изображение не помещается
        bbox = self.canvas.bbox(tk.ALL)

        # if bbox and (bbox[2] > event.width or bbox[3] > event.height):
        if bbox:
            self.auto_select_scale(self.original_image)
            self.show_image(self.original_image)
            self.add_marks_to_preview()

    def on_mark_click(self, event):
        selected_item = self.marks_list.selection()
        if selected_item:
            item = self.marks_list.item(selected_item)
            mark_id = item['values'][0]
            MarkDialog(self, self, None, self.db_service, self.main_root, self.user_id, self.schema_id, mark_id)

    def open_add_mark(self):
        self.canvas.config(cursor='cross')

    def open_delete_mark(self):
        answer = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы точно хотите удалить эту метку?",
            icon='warning',
            parent=self
        )
        if answer:
            self.db_service.delete_mark(self.current_mark_id)
            found_item = next((item for item in self.annotations if item["id"] == self.current_mark_id), None)
            if found_item:
                self.annotations.remove(found_item)

            self.canvas.delete(self.canvas_ann[self.current_mark_id])
            self.canvas.delete(self.selected_annotation_box)

            self.current_mark_id = -1
            self.delete_btn.config(state=DISABLED)
            self.fill_list_marks()

    def fill_list_marks(self):
        for item in self.marks_list.get_children():
            self.marks_list.delete(item)

        marks = self.db_service.get_marks(self.schema_id)
        if len(marks) > 0:
            for mark in marks:
                self.marks_list.insert("", tk.END,
                                       iid=f"mark_{mark.id}",
                                       values=(mark.id, mark.name, mark.description))

            first_item = self.marks_list.get_children()[0]
            self.marks_list.selection_set(first_item)
            self.marks_list.focus(first_item)

    def update_mark_information(self):
        mark = self.db_service.get_mark(self.current_mark_id)

        found_item = next((item for item in self.annotations if item["id"] == self.current_mark_id), None)
        if found_item:
            self.annotations.remove(found_item)

        self.canvas.delete(self.canvas_ann[self.current_mark_id])
        self.canvas.delete(self.selected_annotation_box)

        self.draw_annotation(mark)

        self.current_mark_id = -1
        self.fill_list_marks()

    def add_mark(self, mark_id):
        mark = self.db_service.get_mark(mark_id)
        self.draw_annotation(mark)
        self.marks_list.insert("", tk.END,
                               iid=f"mark_{mark.id}",
                               values=(mark.id, mark.name, mark.description))

    def load_image(self):
        if self.schema == None:
            self.schema = self.db_service.get_schema(self.schema_id)
            self.original_image = Image.open(io.BytesIO(self.schema.data_image))
            self.auto_select_scale(self.original_image)

        self.show_image(self.original_image)
        self.add_marks_to_preview()

    def show_image(self, image_data):
        self.clear_image_display()

        try:
            img_width, img_height = image_data.size

            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)

            image = image_data.resize((new_width, new_height), Image.LANCZOS)

            photo = ImageTk.PhotoImage(image)

            x = 0
            y = 0

            self.canvas.image = photo  # Keep a reference
            self.canvas.create_image(x, y, image=photo, anchor=tk.NW)
        except Exception as e:
            print(f"Error displaying image: {e}")

    def clear_image_display(self):
        self.canvas.delete("all")
        if hasattr(self.canvas, 'image'):
            del self.canvas.image

    def add_marks_to_preview(self):
        marks = self.db_service.get_marks(self.schema_id)
        for mark in marks:
            self.draw_annotation(mark)

    def draw_annotation(self, mark):
        x = int(mark.x * self.scale_factor)
        y = int(mark.y * self.scale_factor)
        text = mark.name

        annotation = {
            'x': x,
            'y': y,
            'text': text,
            'width': 0,
            'height': 0,
            'id': mark.id
        }
        self.annotations.append(annotation)

        if mark.spare_parts:
            ann_color = 'blue'
        else:
            ann_color = 'red'

        self.ann_color[mark.id] = ann_color

        text_id = self.canvas.create_text(x, y, text=text, fill=ann_color, font=('Helvetica', 8), anchor=tk.NW,
                                          tags=f"ann_{mark.id}")
        self.canvas_ann[mark.id] = text_id

        bbox = self.canvas.bbox(text_id)

        if bbox:
            annotation['width'] = bbox[2] - bbox[0]
            annotation['height'] = bbox[3] - bbox[1]
            annotation['real_x'] = bbox[0]
            annotation['real_y'] = bbox[1]
            self.temp_bbox[mark.id] = bbox

    def on_mark_select(self, event):
        selected_item = self.marks_list.selection()
        if selected_item:
            item = self.marks_list.item(selected_item)
            mark_id = item['values'][0]
            self.current_mark_id = mark_id
            self.draw_rectangle_for_selected(mark_id)

    def draw_rectangle_for_selected(self, mark_id):
        if self.selected_annotation_box:
            self.canvas.delete(self.selected_annotation_box)
            self.selected_annotation_box = None

        if mark_id in self.temp_bbox:
            bbox = self.temp_bbox[mark_id]
            self.selected_annotation_box = self.canvas.create_rectangle(bbox[0] - 2, bbox[1] - 2, bbox[2] + 2,
                                                                        bbox[3] + 2,
                                                                        outline=self.ann_color[mark_id], width=2,
                                                                        tags=f"ann_{id}")

    def change_selection_in_list(self, mark_id):
        self.marks_list.selection_remove(self.marks_list.selection())
        item_id = f"mark_{mark_id}"
        self.marks_list.selection_add(item_id)
        self.marks_list.focus(item_id)

    def save_image(self):
        if not self.original_image:
            return

        schema_name = "schema"  # Значение по умолчанию
        if self.schema and hasattr(self.schema, 'name'):
            schema_name = os.path.splitext(self.schema.name)[0]

        safe_name = re.sub(r'[\\/*?:"<>|]', "_", schema_name)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{safe_name}_с_метками",  # Задаем начальное имя файла
            title="Сохранить схему с метками как",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )

        img_width, img_height = self.original_image.size

        font = ImageFont.truetype("arial.ttf", img_height / 80)

        if file_path:
            try:
                # Создаем копию оригинального изображения с метками
                image_to_save = self.original_image.copy()
                marks = self.db_service.get_marks(self.schema_id)
                if marks:
                    draw = ImageDraw.Draw(image_to_save)
                    for mark in marks:
                        if mark.spare_parts:
                            ann_color = 'blue'
                        else:
                            ann_color = 'red'
                        draw.text((mark.x, mark.y), mark.name, fill=ann_color, font=font)

                image_to_save.save(file_path)
                messagebox.showinfo("Сохранено", f"Изображение сохранено как:\n{file_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение:\n{e}", parent=self)
