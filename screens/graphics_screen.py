from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from io import BytesIO
import matplotlib.pyplot as plt
from Utilidades import database as db
from collections import defaultdict

class GraphicsScreen(Screen):
    user_id = None

    def on_pre_enter(self):
        self.user_id = self.manager.get_screen("home").user_id
        self.show_pie_chart()

    def show_pie_chart(self):
        txs = db.list_tx(self.user_id)
        categorias = {}
        for _, monto, categoria, tipo, _, _ in txs:
            if tipo == "egreso":
                categorias[categoria] = categorias.get(categoria, 0) + monto

        self.ids.chart_box.clear_widgets()
        if not categorias:
            return

        labels = list(categorias.keys())
        sizes = list(categorias.values())

        fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        im = CoreImage(buf, ext="png").texture
        self.ids.chart_box.add_widget(Image(texture=im))

    def show_bar_chart(self):
        txs = db.list_tx(self.user_id)
        meses = defaultdict(lambda: {"ingreso": 0, "egreso": 0})
        for _, monto, categoria, tipo, fecha, nota in txs:
            mes = fecha[:7]  # YYYY-MM
            meses[mes][tipo] += monto

        meses_ordenados = sorted(meses.keys())
        ingresos = [meses[mes]["ingreso"] for mes in meses_ordenados]
        egresos = [meses[mes]["egreso"] for mes in meses_ordenados]

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.bar(meses_ordenados, ingresos, label="Ingresos", color="green")
        ax.bar(meses_ordenados, egresos, label="Egresos", color="red", bottom=ingresos)
        ax.set_ylabel("Monto")
        ax.set_title("Comparación entre meses")
        ax.legend()
        plt.xticks(rotation=45)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        im = CoreImage(buf, ext="png").texture

        self.ids.chart_box.clear_widgets()
        self.ids.chart_box.add_widget(Image(texture=im))