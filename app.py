import tkinter as tk

from controllers.auth_controller import AuthController
from controllers.equipment_controller import EquipmentController
from views.auth_view import AuthView
from views.main_view import MainView


class DatexLite:
    def __init__(self):
        self.root = tk.Tk()
        self.auth_controller = AuthController()
        self.current_user = None
        self.main_view = None

    def run(self):
        if self.authenticate():
            self.show_main_app()
            self.root.mainloop()

    def authenticate(self):
        auth_view = AuthView(self.root, self.auth_controller)
        self.current_user = auth_view.show()
        return self.current_user is not None

    def show_main_app(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.main_view = MainView(self.root, self.current_user)
        self.main_view.show()


if __name__ == "__main__":
    app = DatexLite()
    app.run()
