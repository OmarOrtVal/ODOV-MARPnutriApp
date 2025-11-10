from flask import Flask, render_template, request, redirect, url_for, session,flash

app = Flask(__name__)
app.secret_key = 'nutri_track_secret_key'

USERS = [
    {
        'nombre': 'Omar', 
        'apellido': 'Ortega',
        'email': 'omar@correo.com',
        'password': '1234'  
    },
    {
        'nombre': 'Angel', 
        'apellido': 'Roman',
        'email': 'angel@correo.com',
        'password': '1234'  
    }
]

@app.context_processor
def inject_user_data():
    current_user = 'user_email' in session
    user_nombre = session.get('user_nombre', 'Invitado')
    return dict(current_user=current_user, user_nombre=user_nombre)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user_email' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    elif 'datos_usuario' not in globals():
        global datos_usuario
        datos_usuario = {
            'nombre': '',
            'edad': '',
            'sexo': 'Masculino', 
            'peso': '',
            'altura': '',
            'objetivo': 'Mantener peso'  
        }
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        peso = request.form.get('peso')
        altura = request.form.get('altura')
        objetivo = request.form.get('objetivo')
        
        if not nombre or not edad or not peso or not altura:
            flash('Error: Todos los campos son obligatorios.', 'danger')
        else:
            datos_usuario = {
                'nombre': nombre,
                'edad': int(edad),
                'sexo': sexo,
                'peso': float(peso),
                'altura': float(altura),
                'objetivo': objetivo
            }
            
            flash('¡Cambios guardados con éxito!', 'success')
            print("Datos Recibidos:", datos_usuario)

    return render_template('perfil.html', datos=datos_usuario)

@app.route('/seguimiento')
def seguimiento():
    return render_template('seguimiento.html')

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

@app.route('/habitos')
def habitos():
    return render_template('habitos.html')

@app.route('/alimentos', methods=['GET', 'POST'])
def alimentos():    
    if request.method == 'POST':
        alimento = request.form.get('alimento')
        calorias = request.form.get('calorias')
        return redirect(url_for('alimentos'))
    
    return render_template('alimentos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_login = request.form.get('email_login')
        password_login = request.form.get('password_login')
        
        user_found = None
        for user in USERS:
            if user['email'] == email_login and user['password'] == password_login:
                user_found = user
                break
        
        if user_found:
            session['user_email'] = user_found['email']
            session['user_nombre'] = user_found['nombre']
            flash(f"¡Bienvenido de nuevo, {user_found['nombre']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('contacto')
        contrasena = request.form.get('contrasena')
        confirma = request.form.get('confirmaContraseña')
        
        if contrasena != confirma:
            return render_template('registro.html', error="Las contraseñas no coinciden.")
        return redirect(url_for('login'))
        
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_nombre', None) 
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))  

@app.route('/calculadoras')
def calculadoras():
    return render_template('calculadoras.html')

@app.route('/imc')
def imc():
    return render_template('imc.html')

@app.route('/tmb')
def tmb():
    return render_template('tmb.html')

@app.route('/gct')
def gct():
    return render_template('gct.html')

@app.route('/peso_ideal')
def peso_ideal():
    return render_template('peso_ideal.html')


if __name__ == '__main__':
    app.run(debug=True)
