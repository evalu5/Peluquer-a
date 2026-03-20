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
    
    # Guardar en la base de datos
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reservas (nombre, fecha) VALUES (?, ?)', (nombre, fecha))
    conn.commit()
    conn.close()
    
    return f"<h1>¡Cita guardada en la base de datos!</h1><p>Vuelve atrás para agendar otra.</p>"

if __name__ == '__main__':
    init_db() # Creamos la tabla al arrancar
    app.run(debug=True)