import tkinter as tk
from tkinter import ttk


class TabBase(ttk.Frame):
    def __init__(self, notebook, name):
        super().__init__(notebook)
        self.notebook = notebook
        self.name = name
        self.is_active = False

        # Регистрируем себя в notebook
        notebook.add(self, text=name)
        self.bind_events()

    def bind_events(self):
        self.notebook.bind("<<NotebookTabChanged>>", self.check_active_status)

    def check_active_status(self, event=None):
        current_tab = self.notebook.select()
        if current_tab == str(self):
            if not self.is_active:
                self.is_active = True
                self.on_activate()
        else:
            if self.is_active:
                self.is_active = False
                self.on_deactivate()

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
