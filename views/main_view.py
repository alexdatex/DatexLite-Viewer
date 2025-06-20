import tkinter as tk
from tkinter import ttk

from db import SessionLocal, DBController
from tabs import ComponentInfoTab, SchemaInfoTab


class MainView:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.current_component_id = -1

        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        self.root.title(f"DATEX Lite (User: {self.user['login']})")
        self.root.geometry("1000x800")

    def _create_widgets(self):
        self._create_toolbar()
        self._create_paned_window()
        self._create_left_panel()
        self._create_right_panel()

    def _create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        exit_btn = ttk.Button(toolbar, text="Exit", command=self.root.destroy)
        exit_btn.pack(side=tk.RIGHT, padx=2, pady=2)

    def _create_paned_window(self):
        self.paned_window = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_panel = tk.Frame(self.paned_window, width=100)
        self.right_panel = tk.Frame(self.paned_window)

        self.paned_window.add(self.left_panel)
        self.paned_window.add(self.right_panel)
        self.paned_window.paneconfigure(self.left_panel, minsize=150)

    def _create_left_panel(self):
        self._create_filters()
        self._create_treeview()
        self._create_buttons()

    def _create_right_panel(self):
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.component_info_tab = ComponentInfoTab(self.notebook, self.controller, self)
        self.schema_info_tab = SchemaInfoTab(self.notebook, self.controller, self)

        self.notebook.add(self.component_info_tab.frame, text="Equipment Data")
        self.notebook.add(self.schema_info_tab.frame, text="Equipment Schema")

    def show(self):
        self.root.mainloop()
