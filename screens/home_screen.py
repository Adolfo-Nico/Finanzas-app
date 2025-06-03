import openpyxl
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, NumericProperty
from Utilidades import database as db
from openpyxl.styles import Font

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivymd.uix.list import (
    IconLeftWidget,
    OneLineAvatarIconListItem,
)
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.app import App

class HomeScreen(Screen):
    tx_rows = ListProperty([])
    tx_filtradas = ListProperty([])
    user_id = NumericProperty(0)
    presupuestos = {}  # { (categoria, mes): monto }
    menu = None

    def on_pre_enter(self):
        self.presupuestos = db.get_presupuestos(self.user_id)
        self.refresh_list()
        self.check_alertas()
        self.actualizar_presupuestos()
        self.actualizar_filtros()
        self.setup_menu()

    def setup_menu(self):
        if self.menu:
            return
        menu_items = [
            {"text": "+ Nueva transacción", "on_release": lambda x=None: self.menu_action("add_tx")},
            {"text": "Ver gráficos", "on_release": lambda x=None: self.menu_action("graphics")},
            {"text": "Exportar a Excel", "on_release": lambda x=None: self.menu_action("exportar")},
            {"text": "Definir presupuesto", "on_release": lambda x=None: self.menu_action("presupuesto")},
            {"text": "Cambiar Tema", "on_release": lambda x=None: self.menu_action("tema")},
            {"text": "Cerrar sesión", "on_release": lambda x=None: self.menu_action("logout")},
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.fab_menu,
            items=menu_items,
            width_mult=4,
        )

    def open_menu(self):
        self.menu.caller = self.ids.fab_menu
        self.menu.open()

    def menu_action(self, action):
        self.menu.dismiss()
        app = App.get_running_app()
        if action == "add_tx":
            self.manager.current = "add_tx"
        elif action == "graphics":
            self.manager.current = "graphics"
        elif action == "exportar":
            self.exportar_excel()
        elif action == "presupuesto":
            self.popup_presupuesto()
        elif action == "tema":
            app.toggle_theme()
        elif action == "logout":
            self.manager.current = "login"

    def refresh_list(self):
        if self.user_id:
            self.tx_rows = db.list_tx(self.user_id)
            self.tx_filtradas = self.tx_rows[:]
            self.update_balance()
            self.actualizar_lista()
            self.check_alertas()
            self.actualizar_filtros()

    def actualizar_filtros(self):
        categorias = sorted(set([cat for _, _, cat, _, _, _ in self.tx_rows]))
        meses = sorted(set([fecha[:7] for _, _, _, _, fecha, _ in self.tx_rows]))
        self.ids.filtro_categoria.values = ["Todas"] + categorias if categorias else ["Todas"]
        self.ids.filtro_mes.values = ["Todos"] + meses if meses else ["Todos"]

    def filtrar(self):
        cat = self.ids.filtro_categoria.text
        mes = self.ids.filtro_mes.text
        self.tx_filtradas = [
            tx for tx in self.tx_rows
            if (cat == "Todas" or tx[2] == cat)
            and (mes == "Todos" or tx[4][:7] == mes)
        ]
        self.update_balance()
        self.actualizar_lista()
        self.check_alertas()

    def limpiar_filtros(self):
        self.ids.filtro_categoria.text = "Todas"
        self.ids.filtro_mes.text = "Todos"
        self.tx_filtradas = self.tx_rows[:]
        self.update_balance()
        self.actualizar_lista()
        self.check_alertas()

    def update_balance(self):
        ingresos = sum(m for _, m, _, t, _, _ in self.tx_filtradas if t == "ingreso")
        egresos = sum(m for _, m, _, t, _, _ in self.tx_filtradas if t == "egreso")
        balance = ingresos - egresos
        self.ids.balance_lbl.text = f"${balance:,.0f}"

    def exportar_excel(self):
        spinner = MDSpinner(size_hint=(None, None), size=(46, 46), pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(spinner)
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Transacciones"
            ws.append(["ID", "Monto", "Categoria", "Tipo", "Fecha", "Nota"])
            for id_, monto, categoria, tipo, fecha, nota in self.tx_filtradas:
                ws.append([id_, monto, categoria, tipo, fecha, nota])
            for cell in ws["1:1"]:
                cell.font = Font(bold=True)
            wb.save("transacciones.xlsx")
            toast("Exportado como transacciones.xlsx")
        except Exception as e:
            toast(f"Error al guardar: {e}")
        self.remove_widget(spinner)

    def popup_presupuesto(self):
        self.cat_input = MDTextField(
            hint_text="Categoría",
            mode="rectangle"
        )
        self.mes_input = MDTextField(
            hint_text="Mes (YYYY-MM)",
            mode="rectangle"
        )
        self.monto_input = MDTextField(
            hint_text="Monto",
            mode="rectangle",
            input_filter="int"
        )

        box = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="200dp"
        )
        box.add_widget(self.cat_input)
        box.add_widget(self.mes_input)
        box.add_widget(self.monto_input)

        self.dialog_presupuesto = MDDialog(
            title="Definir presupuesto",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog_presupuesto.dismiss()
                ),
                MDFlatButton(
                    text="GUARDAR",
                    on_release=lambda x: self.guardar_presupuesto()
                ),
            ],
        )
        self.dialog_presupuesto.open()

    def guardar_presupuesto(self):
        cat = self.cat_input.text.strip()
        mes = self.mes_input.text.strip()
        if not cat or not mes or not self.monto_input.text.strip():
            Snackbar(text="Completa todos los campos.").open()
            return
        try:
            monto = int(self.monto_input.text)
            db.set_presupuesto(self.user_id, cat, mes, monto)
            self.presupuestos = db.get_presupuestos(self.user_id)
            toast("¡Presupuesto guardado!")
            self.dialog_presupuesto.dismiss()
            self.check_alertas()
            self.actualizar_presupuestos()
        except Exception:
            Snackbar(text="Monto inválido.").open()

    def editar_presupuesto(self, categoria, mes, monto_actual):
        self.cat_input = MDTextField(
            hint_text="Categoría",
            text=categoria,
            mode="rectangle"
        )
        self.mes_input = MDTextField(
            hint_text="Mes (YYYY-MM)",
            text=mes,
            mode="rectangle"
        )
        self.monto_input = MDTextField(
            hint_text="Monto",
            text=str(monto_actual),
            mode="rectangle",
            input_filter="int"
        )

        box = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="200dp"
        )
        box.add_widget(self.cat_input)
        box.add_widget(self.mes_input)
        box.add_widget(self.monto_input)

        self.dialog_presupuesto = MDDialog(
            title="Editar presupuesto",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text="ELIMINAR",
                    theme_text_color="Error",
                    on_release=lambda x: self.confirmar_eliminar_presupuesto(categoria, mes)
                ),
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog_presupuesto.dismiss()
                ),
                MDFlatButton(
                    text="GUARDAR",
                    on_release=lambda x: self.guardar_presupuesto()
                ),
            ],
        )
        self.dialog_presupuesto.open()

    def confirmar_eliminar_presupuesto(self, categoria, mes):
        try:
            self.dialog_presupuesto.dismiss()
        except Exception:
            pass
        self.dialog_confirmar = MDDialog(
            title="Eliminar presupuesto",
            text=f"¿Seguro que deseas eliminar el presupuesto de '{categoria}' para {mes}?",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog_confirmar.dismiss()
                ),
                MDFlatButton(
                    text="ELIMINAR",
                    theme_text_color="Error",
                    on_release=lambda x: self.eliminar_presupuesto(categoria, mes)
                ),
            ],
        )
        self.dialog_confirmar.open()

    def eliminar_presupuesto(self, categoria, mes):
        db.eliminar_presupuesto(self.user_id, categoria, mes)
        self.presupuestos = db.get_presupuestos(self.user_id)
        self.actualizar_presupuestos()
        self.check_alertas()
        self.dialog_confirmar.dismiss()
        toast("Presupuesto eliminado")

    def check_alertas(self):
        alertas = []
        for (cat, mes), monto_max in self.presupuestos.items():
            gastado = sum(
                m for _, m, c, t, f, _ in self.tx_filtradas
                if t == "egreso" and c == cat and f[:7] == mes
            )
            if gastado > monto_max:
                alertas.append(f"[b][color=ff3333]¡Alerta![/color][/b] Superaste el presupuesto de [b]{cat}[/b] en {mes}: ${gastado:,.0f}/${monto_max:,.0f}")
        self.ids.alerta_lbl.text = "\n".join(alertas) if alertas else ""

    def actualizar_lista(self):
        self.ids.transacciones_list.clear_widgets()
        if not self.tx_filtradas:
            self.ids.transacciones_list.add_widget(
                MDLabel(
                    text="No hay transacciones",
                    halign="center",
                    theme_text_color="Hint",
                    font_style="Subtitle1"
                )
            )
        else:
            for id_, monto, categoria, tipo, fecha, nota in self.tx_filtradas:
                item = OneLineAvatarIconListItem(
                    text=f"{fecha} | {categoria} | ${monto:,.0f} | {nota}"
                )
                icon = "arrow-up-bold" if tipo == "ingreso" else "arrow-down-bold"
                color = (0, 0.7, 0, 1) if tipo == "ingreso" else (0.8, 0, 0, 1)
                item.add_widget(IconLeftWidget(icon=icon, theme_text_color="Custom", text_color=color))
                self.ids.transacciones_list.add_widget(item)

    def actualizar_presupuestos(self):
        self.ids.presupuestos_list.clear_widgets()
        if not self.presupuestos:
            self.ids.presupuestos_list.add_widget(
                MDLabel(
                    text="No hay presupuestos activos",
                    halign="center",
                    theme_text_color="Hint",
                    font_style="Subtitle1"
                )
            )
        else:
            for (cat, mes), monto in self.presupuestos.items():
                box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="56dp", padding=(8, 0, 8, 0), spacing=8)
                icon = IconLeftWidget(icon="wallet")
                box.add_widget(icon)
                label_box = MDBoxLayout(orientation="vertical", size_hint_x=0.7)
                label_box.add_widget(MDLabel(text=f"{cat} ({mes})", font_style="Subtitle1", halign="left"))
                label_box.add_widget(MDLabel(text=f"Presupuesto: ${monto:,.0f}", font_style="Caption", halign="left"))
                box.add_widget(label_box)
                edit_btn = MDIconButton(
                    icon="pencil",
                    on_release=lambda x, c=cat, m=mes, mo=monto: self.editar_presupuesto(c, m, mo)
                )
                delete_btn = MDIconButton(
                    icon="delete",
                    theme_text_color="Error",
                    on_release=lambda x, c=cat, m=mes: self.confirmar_eliminar_presupuesto(c, m)
                )
                box.add_widget(edit_btn)
                box.add_widget(delete_btn)
                self.ids.presupuestos_list.add_widget(box)