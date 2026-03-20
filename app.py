import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)

# Una clave secreta aleatoria para que nadie hackee las sesiones
app.secret_key = 'mi-primo-es-el-mejor-barbero-de-granada-2026' 

# LA CONTRASEÑA QUE TÚ ELIJAS
ADMIN_PASSWORD = "gabirechulon" 

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
    
    # 1. Guardar en BD
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reservas (nombre, fecha) VALUES (?, ?)', (nombre, fecha))
    conn.commit()
    conn.close()

    # 2. Configurar WhatsApp (Pon el número de tu primo aquí sin el +)
    telefono_primo = "34600000000" 
    mensaje = f"Hola! Soy {nombre}, acabo de reservar una cita para el {fecha} a través de la web. ¿Me confirmas?"
    # Creamos el link (reemplazando espacios para que no de error)
    link_ws = f"https://wa.me/{telefono_primo}?text={mensaje.replace(' ', '%20')}"

    # 3. Mostrar la nueva página bonita
    return render_template('confirmacion.html', nombre=nombre, fecha=fecha, link_ws=link_ws)
# --- SECCIÓN DE ADMINISTRACIÓN CON CONTRASEÑA ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_ingresada = request.form.get('password')
        if password_ingresada == ADMIN_PASSWORD:
            session['admin_logueado'] = True
            return redirect(url_for('admin'))
        else:
            return "<h1>Error</h1><p>Contraseña incorrecta.</p><a href='/login'>Volver</a>"
    
    # Cambiamos el texto feo por el nuevo HTML
    return render_template('login.html')

@app.route('/admin')
def admin():
    # Verificamos si tiene la "pulsera" de entrada
    if not session.get('admin_logueado'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservas ORDER BY fecha DESC')
    todas_las_citas = cursor.fetchall()
    conn.close()
    return render_template('admin.html', citas=todas_las_citas)

@app.route('/logout')
def logout():
    session.pop('admin_logueado', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)