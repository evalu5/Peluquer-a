import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Función para crear la base de datos si no existe
def init_db():
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/reservar', methods=['POST'])
def reservar():
    nombre = request.form.get('nombre')
    fecha = request.form.get('fecha')
    telefono_primo = "34600000000" # <-- Pon aquí el número de tu primo (con el 34 delante)

    # 1. Guardar en BD (esto ya lo tienes)
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reservas (nombre, fecha) VALUES (?, ?)', (nombre, fecha))
    conn.commit()
    conn.close()

    # 2. Crear el link de WhatsApp
    mensaje = f"Hola! Soy {nombre}, acabo de reservar una cita para el {fecha}. ¿Me confirmas?"
    # Reemplazamos espacios por %20 para que el link funcione
    link_whatsapp = f"https://wa.me/{telefono_primo}?text={mensaje.replace(' ', '%20')}"

    # 3. Mostrar confirmación con el botón
    return f"""
        <h1>¡Cita registrada!</h1>
        <p>Para asegurar tu hueco, pulsa el botón de abajo:</p>
        <a href="{link_whatsapp}" style="background-color: #25D366; color: white; padding: 15px; text-decoration: none; border-radius: 5px; display: inline-block;">
            Confirmar por WhatsApp
        </a>
    """

@app.route('/admin')
def admin():
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    # Traemos todas las reservas de la base de datos
    cursor.execute('SELECT * FROM reservas ORDER BY fecha DESC')
    todas_las_citas = cursor.fetchall()
    conn.close()
    
    # Se las pasamos a una nueva página HTML
    return render_template('admin.html', citas=todas_las_citas)


if __name__ == '__main__':
    init_db() # Creamos la tabla al arrancar
    app.run(debug=True)