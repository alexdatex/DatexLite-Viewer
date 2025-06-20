class AuthController:
    def __init__(self):
        self.users = [
            {"login": "admin", "password": "admin123", "id": 1},
            {"login": "user1", "password": "pass1", "id": 2},
            {"login": "user2", "password": "pass2", "id": 3},
            {"login": "user3", "password": "pass3", "id": 4},
            {"login": "user4", "password": "pass4", "id": 5},
            {"login": "user5", "password": "pass5", "id": 6},
            {"login": "user6", "password": "pass6", "id": 7}
        ]

    def authenticate(self, login, password):
        for user in self.users:
            if user["login"] == login and user["password"] == password:
                return user
        return None
