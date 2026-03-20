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
    
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reservas (nombre, fecha) VALUES (?, ?)', (nombre, fecha))
    conn.commit()
    conn.close()
    
    # Aquí puedes poner el link de WhatsApp que hablamos antes
    return f"<h1>¡Cita guardada!</h1><p>Gracias {nombre}. <a href='/'>Volver</a></p>"

# --- SECCIÓN DE ADMINISTRACIÓN CON CONTRASEÑA ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_ingresada = request.form.get('password')
        if password_ingresada == ADMIN_PASSWORD:
            session['admin_logueado'] = True
            return redirect(url_for('admin'))
        else:
            return "Contraseña incorrecta. <a href='/login'>Intentar de nuevo</a>"
    
    return '''
        <form method="post">
            <h2>Acceso para el Jefe</h2>
            <input type="password" name="password" placeholder="Introduce la clave">
            <button type="submit">Entrar</button>
        </form>
    '''

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