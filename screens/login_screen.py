from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from Utilidades import database as db

class LoginScreen(Screen):
    error_msg = StringProperty("")

    def login(self, username, password):
        user_id = db.verificar_usuario(username, password)
        if user_id:
            self.manager.get_screen("home").user_id = user_id
            self.manager.current = "home"
            self.error_msg = ""
        else:
            self.error_msg = "Usuario o contraseña incorrectos"

    def register(self, username, password):
        if not username or not password:
            self.error_msg = "Completa usuario y contraseña"
            return
        try:
            db.add_user(username, password)
            self.error_msg = "Usuario registrado. Ahora puedes ingresar."
        except Exception as e:
            self.error_msg = "Usuario ya existe"