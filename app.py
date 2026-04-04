import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'clave-secreta-alto-voltaje'
PASSWORD_ADMIN = "admin123"

# Duraciones por servicio (Asegúrate de que coincidan con los nombres del HTML)
DURACIONES = {
    "Corte de cabello": 30,
    "Barba": 30,
    "Corte y Barba": 30,
    "Afeitado de cabeza": 30,
    "Corte + Mechon color": 30,
    "Tinte completo + Corte": 30,
    "Corte + Mechas": 60
}

def init_db():
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            servicio TEXT NOT NULL,
            fin TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reservar', methods=['POST'])
def reservar():
    nombre = request.form.get('nombre')
    fecha_inicio_str = request.form.get('fecha')
    servicio = request.form.get('servicio')
    
    minutos = DURACIONES.get(servicio, 30)
    inicio_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M')
    fin_dt = inicio_dt + timedelta(minutes=minutos)
    fecha_fin_str = fin_dt.strftime('%Y-%m-%dT%H:%M')

    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    
    # Comprobar si se pisa con otra cita
    cursor.execute('SELECT * FROM reservas WHERE (? < fin AND ? > fecha)', (fecha_inicio_str, fecha_fin_str))
    
    if cursor.fetchone():
        conn.close()
        return f'''
        <div style="background:#1a1a1a; color:white; height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:sans-serif; text-align:center; padding:20px;">
            <h1 style="color:#ffea00;">⚡ HORARIO OCUPADO</h1>
            <p style="font-size:1.2rem; color:#bbb;">Lo sentimos, el barbero ya tiene una cita en ese horario.</p>
            <a href="/" style="color:#ffea00; text-decoration:none; border:1px solid #ffea00; padding:10px 20px; border-radius:5px; margin-top:20px;">ELEGIR OTRA HORA</a>
        </div>
        '''

    cursor.execute('INSERT INTO reservas (nombre, fecha, servicio, fin) VALUES (?, ?, ?, ?)', 
                   (nombre, fecha_inicio_str, servicio, fecha_fin_str))
    conn.commit()
    conn.close()

    telefono = "34690005656" # Pon el número de Gabi
    msg = f"Hola Gabi! Soy {nombre}. He reservado: {servicio} para el {fecha_inicio_str}."
    link_ws = f"https://wa.me/{telefono}?text={msg.replace(' ', '%20')}"
    
    return render_template('confirmacion.html', nombre=nombre, fecha=fecha_inicio_str, link_ws=link_ws)

# --- ESTA ES LA RUTA QUE TE FALTABA PARA EL BOTÓN EDITAR ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not session.get('admin_logueado'): return redirect(url_for('login'))
    
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        fecha = request.form.get('fecha')
        servicio = request.form.get('servicio')
        
        # Recalculamos el fin por si cambió la hora o el servicio
        minutos = DURACIONES.get(servicio, 30)
        inicio_dt = datetime.strptime(fecha, '%Y-%m-%dT%H:%M')
        fin_dt = inicio_dt + timedelta(minutes=minutos)
        fecha_fin_str = fin_dt.strftime('%Y-%m-%dT%H:%M')

        cursor.execute('''
            UPDATE reservas SET nombre=?, fecha=?, servicio=?, fin=? WHERE id=?
        ''', (nombre, fecha, servicio, fecha_fin_str, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    cursor.execute('SELECT * FROM reservas WHERE id=?', (id,))
    cita = cursor.fetchone()
    conn.close()
    
    if not cita: return "Cita no encontrada", 404
    return render_template('editar.html', cita=cita)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD_ADMIN:
            session['admin_logueado'] = True
            return redirect(url_for('admin'))
    return '''
        <body style="background:#1a1a1a; color:white; display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif;">
            <form method="post" style="background:#252525; padding:30px; border-radius:15px; border:2px solid #ffea00;">
                <h2 style="color:#ffea00; margin-bottom:20px;">STAFF LOGIN</h2>
                <input type="password" name="password" placeholder="Contraseña" style="padding:10px; width:100%; margin-bottom:10px; border-radius:5px; border:none;">
                <button type="submit" style="width:100%; padding:10px; background:#ffea00; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">ENTRAR ⚡</button>
            </form>
        </body>
    '''

@app.route('/admin')
def admin():
    if not session.get('admin_logueado'): return redirect(url_for('login'))
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, fecha, servicio FROM reservas ORDER BY fecha ASC')
    citas = cursor.fetchall()
    conn.close()
    return render_template('admin.html', citas=citas)

@app.route('/borrar/<int:id>')
def borrar(id):
    if not session.get('admin_logueado'): return redirect(url_for('login'))
    conn = sqlite3.connect('citas.db'); cursor = conn.cursor()
    cursor.execute('DELETE FROM reservas WHERE id = ?', (id,)); conn.commit(); conn.close()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)