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
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, OneLineListItem

class HomeScreen(Screen):
    tx_rows = ListProperty([])
    tx_filtradas = ListProperty([])
    user_id = NumericProperty(0)
    presupuestos = {}  # { (categoria, mes): monto }

    def on_pre_enter(self):
        self.presupuestos = db.get_presupuestos(self.user_id)
        self.refresh_list()
        self.check_alertas()
        self.actualizar_presupuestos()
        self.actualizar_filtros()

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
        self.ids.balance_lbl.text = f"Balance mensual: ${balance:,.0f}"

    def exportar_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transacciones"
        ws.append(["ID", "Monto", "Categoria", "Tipo", "Fecha", "Nota"])
        for id_, monto, categoria, tipo, fecha, nota in self.tx_filtradas:
            ws.append([id_, monto, categoria, tipo, fecha, nota])
        for cell in ws["1:1"]:
            cell.font = Font(bold=True)
        try:
            wb.save("transacciones.xlsx")
            toast("Exportado como transacciones.xlsx")
        except Exception as e:
            toast(f"Error al guardar: {e}")

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
        try:
            monto = int(self.monto_input.text)
            db.set_presupuesto(self.user_id, cat, mes, monto)
            self.presupuestos = db.get_presupuestos(self.user_id)
            toast("¡Presupuesto guardado!")
            self.dialog_presupuesto.dismiss()
            self.check_alertas()
            self.actualizar_presupuestos()
        except Exception:
            toast("Monto inválido")

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
        for id_, monto, categoria, tipo, fecha, nota in self.tx_filtradas:
            item = OneLineListItem(
                text=f"{id_} | {fecha} | {tipo} | {categoria} | {monto:,.0f} | {nota}"
            )
            self.ids.transacciones_list.add_widget(item)

    def actualizar_presupuestos(self):
        self.ids.presupuestos_list.clear_widgets()
        for (cat, mes), monto in self.presupuestos.items():
            item = TwoLineIconListItem(
                text=f"{cat} ({mes})",
                secondary_text=f"Presupuesto: ${monto:,.0f}"
            )
            item.add_widget(IconLeftWidget(icon="wallet"))
            edit_btn = MDIconButton(
                icon="pencil",
                on_release=lambda x, c=cat, m=mes, mo=monto: self.editar_presupuesto(c, m, mo)
            )
            item.right_widget = edit_btn
            self.ids.presupuestos_list.add_widget(item)