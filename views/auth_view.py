import tkinter as tk
from tkinter import ttk, messagebox


class AuthView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self._setup_window()

    def _setup_window(self):
        self.root.title("Authorization")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Login field
        ttk.Label(main_frame, text="Login:").grid(row=0, column=0, sticky=tk.W)
        self.login_entry = ttk.Entry(main_frame)
        self.login_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)

        # Password field
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, sticky=tk.EW)

        # Login button
        login_btn = ttk.Button(
            main_frame,
            text="Login",
            command=self._authenticate
        )
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.login_entry.focus()

    def _authenticate(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        user = self.controller.authenticate(login, password)
        if user:
            self.user = user
            self.root.quit()
        else:
            messagebox.showerror("Error", "Invalid login or password")
            self.password_entry.delete(0, tk.END)

    def show(self):
        self.root.mainloop()
        return getattr(self, 'user', None)
