from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from Utilidades import database as db
from kivymd.toast import toast

class AddTransactionScreen(Screen):
    error_msg = StringProperty("")

    def save_tx(self, monto, categoria, tipo, fecha, nota):
        try:
            monto = float(monto)
            if not categoria or tipo not in ["ingreso", "egreso"]:
                self.error_msg = "Completa todos los campos obligatorios"
                return
            if not fecha:
                from datetime import datetime
                fecha = datetime.now().strftime("%Y-%m-%d")
            user_id = self.manager.get_screen("home").user_id
            db.add_tx(user_id, monto, categoria, tipo, fecha, nota)
            self.error_msg = ""
            toast("Transacción guardada")
            self.manager.get_screen("home").refresh_list()
            self.manager.current = "home"
        except Exception as e:
            self.error_msg = "Error al guardar"