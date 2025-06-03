# FINDTECH - Gestor de Finanzas Personales

FINDTECH es una aplicación de escritorio desarrollada en Python con KivyMD para la gestión de finanzas personales. Permite a los usuarios registrar ingresos y egresos, definir presupuestos mensuales por categoría, visualizar gráficos de gastos, exportar datos a Excel y recibir alertas cuando se superan los límites establecidos.

---

## Características principales

- **Registro de usuarios:** Inicio de sesión y registro seguro con contraseñas encriptadas.
- **Gestión de transacciones:** Agrega, edita y filtra ingresos y egresos por categoría y mes.
- **Presupuestos mensuales:** Define, edita y elimina presupuestos por categoría y mes.
- **Alertas automáticas:** Recibe avisos cuando superas el presupuesto asignado.
- **Visualización de datos:** Gráficos de torta y barras para analizar tus gastos.
- **Exportación a Excel:** Descarga tus transacciones en formato `.xlsx`.
- **Interfaz intuitiva:** Basada en Material Design, con soporte para temas claro y oscuro.
- **Soporte multiusuario:** Cada usuario gestiona sus propios datos.

---

## Instalación

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/tu_usuario/FINDTECH.git
   cd FINDTECH
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   > **Nota:** Requiere Python 3.10 o superior y KivyMD.

3. **Ejecuta la aplicación:**
   ```bash
   python main.py
   ```

---

## Estructura del proyecto

```
FINDTECH/
│
├── Fase_1/
│   ├── kv/
│   │   ├── home_screen.kv
│   │   ├── login_screen.kv
│   │   └── ...otros .kv
│   ├── screens/
│   │   ├── home_screen.py
│   │   ├── login_screen.py
│   │   └── ...otras pantallas
│   ├── Utilidades/
│   │   └── database.py
│   ├── main.py
│   └── ...otros archivos
└── README.md
```

---

## Uso

1. **Regístrate o inicia sesión** con tu usuario y contraseña.
2. **Agrega transacciones** de ingreso o egreso, seleccionando categoría, monto y fecha.
3. **Define presupuestos** mensuales por categoría para controlar tus gastos.
4. **Visualiza alertas** si superas algún presupuesto.
5. **Consulta gráficos** para analizar tus finanzas.
6. **Exporta tus datos** a Excel cuando lo necesites.

---

## Capturas de pantalla

> 

---

## Requisitos

- Python 3.10 o superior
- [Kivy](https://kivy.org/)
- [KivyMD](https://kivymd.readthedocs.io/)
- openpyxl
- matplotlib

Instala todo con:
```bash
pip install kivy kivymd openpyxl matplotlib
```

---

## Créditos

Desarrollado por Nicolas 

---

## Licencia

Este proyecto es de uso educativo y personal.  
Para uso comercial, contacta al autor.
