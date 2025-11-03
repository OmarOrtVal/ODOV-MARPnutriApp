from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'nutri_track_secret_key' 

@app.route('/')
def index():
    if 'usuario' in session:
        return render_template('index.html', usuario=session['usuario'])
    return redirect(url_for('login'))

@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html', usuario=session['usuario'])

@app.route('/seguimiento')
def seguimiento():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('seguimiento.html', usuario=session['usuario'])

@app.route('/recetas')
def recetas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('recetas.html', usuario=session['usuario'])

@app.route('/habitos')
def habitos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('habitos.html', usuario=session['usuario'])

@app.route('/alimentos', methods=['GET', 'POST'])
def alimentos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        alimento = request.form.get('alimento')
        calorias = request.form.get('calorias')
        return redirect(url_for('alimentos'))
    
    return render_template('alimentos.html', usuario=session['usuario'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email_login')
        password = request.form.get('password_login')

        if email == "omar@correo.com" and password == "1234":
            session['usuario'] = 'Omar'
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")
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
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
