import sqlite3
import os
from Utilidades.security import hash_password, verify_password

DB_NAME = 'finanzas.db'

def db_path():
    # Guarda la base de datos en la carpeta del proyecto
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', DB_NAME)

def _get_conn():
    return sqlite3.connect(db_path())

# --- Usuarios ---
def crear_tabla_usuarios():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

def add_user(username, password):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )

def get_user(username):
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT id, username, password FROM usuarios WHERE username=?",
            (username,)
        )
        return cur.fetchone()

def verificar_usuario(username, password):
    user = get_user(username)
    if user and verify_password(password, user[2]):
        return user[0]  # Devuelve el id del usuario
    return None

# --- Transacciones ---
def crear_tabla_transacciones():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                monto REAL,
                categoria TEXT,
                tipo TEXT,
                fecha TEXT,
                nota TEXT,
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
        """)

def add_tx(user_id, monto, categoria, tipo, fecha, nota):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO transacciones (user_id, monto, categoria, tipo, fecha, nota) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, monto, categoria, tipo, fecha, nota)
        )

def list_tx(user_id):
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT id, monto, categoria, tipo, fecha, nota FROM transacciones WHERE user_id=? ORDER BY fecha DESC",
            (user_id,)
        )
        return cur.fetchall()

# --- Presupuestos ---
def crear_tabla_presupuestos():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS presupuestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                categoria TEXT,
                mes TEXT,
                monto INTEGER,
                UNIQUE(user_id, categoria, mes)
            )
        """)

def set_presupuesto(user_id, categoria, mes, monto):
    with _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO presupuestos (user_id, categoria, mes, monto)
            VALUES (?, ?, ?, ?)
        """, (user_id, categoria, mes, monto))

def get_presupuestos(user_id):
    with _get_conn() as conn:
        cur = conn.execute("""
            SELECT categoria, mes, monto FROM presupuestos WHERE user_id=?
        """, (user_id,))
        res = cur.fetchall()
        return {(cat, mes): monto for cat, mes, monto in res}

def eliminar_presupuesto(user_id, categoria, mes):
    with _get_conn() as conn:
        conn.execute("""
            DELETE FROM presupuestos WHERE user_id=? AND categoria=? AND mes=?
        """, (user_id, categoria, mes))

# --- Inicialización general ---
def inicializar_db():
    crear_tabla_usuarios()
    crear_tabla_transacciones()
    crear_tabla_presupuestos()