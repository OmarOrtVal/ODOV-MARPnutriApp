from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'nutri_track_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

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
        email = request.form.get('email_login')
        password = request.form.get('password_login')

        if email == "omar@correo.com" and password == "1234":
            session['usuario'] = 'Omar'
            return redirect(url_for('index'))
            
        elif email == "angel@correo.com" and password == "1234": 
            session['usuario'] = 'Ángel'
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
