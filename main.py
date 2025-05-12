from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.add_transaction_screen import AddTransactionScreen
from screens.graphics_screen import GraphicsScreen
from Utilidades import database as db

class MainApp(MDApp):
    theme_mode = "Light"  # Cambia a "Dark" si prefieres iniciar en oscuro

    def build(self):
        self.theme_cls.theme_style = self.theme_mode
        Builder.load_file("kv/login_screen.kv")
        Builder.load_file("kv/home_screen.kv")
        Builder.load_file("kv/add_transaction_screen.kv")
        Builder.load_file("kv/graphics_screen.kv")
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddTransactionScreen(name="add_tx"))
        sm.add_widget(GraphicsScreen(name="graphics"))
        return sm

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"

if __name__ == "__main__":
    db.inicializar_db()
    MainApp().run()