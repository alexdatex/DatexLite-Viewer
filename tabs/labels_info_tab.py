import tkinter as tk
from tkinter import ttk, DISABLED


class LabelsInfoTab:
    def __init__(self, parent, db_service, root):
        self.root = root
        self.db_service = db_service

        self.frame = tk.Frame(parent, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

    def update(self, component_id):
        self.current_component_id = component_id
