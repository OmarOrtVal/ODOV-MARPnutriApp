from flask import Flask, render_template, request, redirect, url_for, session, flash

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

ARTICLES = [
    {
        'id': 1,
        'titulo': '¿Cómo leer las etiquetas nutricionales?',
        'contenido': 'Las etiquetas nutricionales son una herramienta esencial para comprender lo que estás consumiendo. Permiten comparar productos, controlar calorías y conocer los nutrientes que aportan los alimentos.',
        'categoria': 'Educación nutricional'
    },
    {
        'id': 2,
        'titulo': 'Mitos y verdades sobre las dietas de moda',
        'contenido': 'Muchas dietas prometen resultados rápidos, pero no todas son saludables o sostenibles. Analiza la evidencia científica antes de seguir una tendencia alimentaria.',
        'categoria': 'Dietas y salud'
    },
    {
        'id': 3,
        'titulo': 'Guías sobre macronutrientes y su función',
        'contenido': 'Los macronutrientes son los principales aportadores de energía. Incluyen proteínas, carbohidratos y grasas, todos esenciales para el correcto funcionamiento del cuerpo.',
        'categoria': 'Nutrición básica'
    },
    {
        'id': 4,
        'titulo': 'La importancia de la hidratación, la fibra, etc.',
        'contenido': 'El agua y la fibra juegan un papel vital en la salud digestiva, la regulación del apetito y el bienestar general. Su consumo diario es clave para mantener el equilibrio corporal.',
        'categoria': 'Salud general'
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

@app.route('/seguimiento', methods=['GET', 'POST'])
def seguimiento():
    if 'user_email' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    return render_template('seguimiento.html')

@app.route('/educacion')
def educacion():
    return render_template('educacion.html', articles=ARTICLES)


@app.route('/articulo/<int:article_id>')
def articulo(article_id):
    article = next((a for a in ARTICLES if a['id'] == article_id), None)
    if article:
        return render_template('articulo.html', article=article)
    else:
        flash('Artículo no encontrado', 'danger')
        return redirect(url_for('educacion'))

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

@app.route('/habitos')
def habitos():
    return render_template('habitos.html')

@app.route('/alimentos', methods=['GET', 'POST'])
def alimentos():    
    if 'user_email' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
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
            flash("Las contraseñas no coinciden.", 'danger')
            return render_template('registro.html')
        
        for user in USERS:
            if user['email'] == email:
                flash("Este correo ya está registrado.", 'warning')
                return render_template('registro.html')
        
        nuevo_usuario = {
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'password': contrasena
        }
        USERS.append(nuevo_usuario)
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
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

@app.route('/imc', methods=['GET', 'POST'])
def imc():
    if request.method == 'POST':
        try:
            peso = float(request.form.get('peso'))
            altura_cm = float(request.form.get('altura'))
            edad = int(request.form.get('edad'))
            sexo = request.form.get('sexo')
            
            altura_m = altura_cm / 100
            
            imc = peso / (altura_m ** 2)
            
            if imc < 18.5:
                clasificacion = "Bajo peso"
                categoria = "text-warning"
                recomendacion = "Consulta a un nutricionista para ganar peso de forma saludable."
            elif 18.5 <= imc < 25:
                clasificacion = "Peso normal"
                categoria = "text-success"
                recomendacion = "¡Excelente! Mantén tus hábitos saludables."
            elif 25 <= imc < 30:
                clasificacion = "Sobrepeso"
                categoria = "text-warning"
                recomendacion = "Considera realizar más actividad física y ajustar tu alimentación."
            elif 30 <= imc < 35:
                clasificacion = "Obesidad grado I"
                categoria = "text-danger"
                recomendacion = "Recomendable consultar con un profesional de la salud."
            elif 35 <= imc < 40:
                clasificacion = "Obesidad grado II"
                categoria = "text-danger"
                recomendacion = "Es importante buscar atención médica especializada."
            else:
                clasificacion = "Obesidad grado III"
                categoria = "text-danger"
                recomendacion = "Consulta urgente con un médico especialista."
            
            
            return render_template('imc.html', 
                                imc_resultado=f"{imc:.2f}", 
                                clasificacion=clasificacion,
                                categoria=categoria,
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'peso': peso,
                                    'altura': altura_cm,
                                    'edad': edad,
                                    'sexo': sexo
                                })
            
        except (ValueError, TypeError, ZeroDivisionError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('imc.html')
    
    return render_template('imc.html')

@app.route('/tmb', methods=['GET', 'POST'])
def tmb():
    if request.method == 'POST':
        try:
            edad = int(request.form.get('edad'))
            peso = float(request.form.get('peso'))
            altura_cm = float(request.form.get('altura'))
            sexo = request.form.get('sexo')
            actividad = request.form.get('actividad')
            
            if sexo == 'Masculino':
                tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161
            
            factores_actividad = {
                'sedentario': {'factor': 1.2, 'descripcion': 'Poco o ningún ejercicio'},
                'ligero': {'factor': 1.375, 'descripcion': 'Ejercicio ligero 1-3 días/semana'},
                'moderado': {'factor': 1.55, 'descripcion': 'Ejercicio moderado 3-5 días/semana'},
                'intenso': {'factor': 1.725, 'descripcion': 'Ejercicio intenso 6-7 días/semana'},
                'muy_intenso': {'factor': 1.9, 'descripcion': 'Atletas profesionales, entrenamiento muy intenso'}
            }
            
            if actividad in factores_actividad:
                factor = factores_actividad[actividad]['factor']
                calorias_actividad = tmb * factor
                descripcion_actividad = factores_actividad[actividad]['descripcion']
            else:
                factor = 1.2
                calorias_actividad = tmb * factor
                descripcion_actividad = factores_actividad['sedentario']['descripcion']
                actividad = 'sedentario'
            
            niveles_actividad = {}
            for key, value in factores_actividad.items():
                niveles_actividad[key] = {
                    'calorias': tmb * value['factor'],
                    'descripcion': value['descripcion'],
                    'factor': value['factor']
                }
            
            if tmb < 1200:
                recomendacion = "Tu metabolismo basal es bajo. Consulta con un nutricionista para un plan personalizado."
            elif 1200 <= tmb < 1800:
                recomendacion = "Metabolismo normal. Mantén una dieta equilibrada y actividad física regular."
            else:
                recomendacion = "Metabolismo alto. Asegúrate de consumir suficientes nutrientes para mantener tu energía."
            
            objetivo_mantener = calorias_actividad
            objetivo_bajar = calorias_actividad * 0.85  
            objetivo_subir = calorias_actividad * 1.15  
            
            return render_template('tmb.html', 
                                tmb_resultado=f"{tmb:.0f}",
                                calorias_actividad=f"{calorias_actividad:.0f}",
                                descripcion_actividad=descripcion_actividad,
                                factor_actividad=factor,
                                niveles_actividad=niveles_actividad,
                                recomendacion=recomendacion,
                                objetivo_mantener=f"{objetivo_mantener:.0f}",
                                objetivo_bajar=f"{objetivo_bajar:.0f}",
                                objetivo_subir=f"{objetivo_subir:.0f}",
                                datos_formulario={
                                    'edad': edad,
                                    'peso': peso,
                                    'altura': altura_cm,
                                    'sexo': sexo,
                                    'actividad': actividad
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('tmb.html')
    
    return render_template('tmb.html')

@app.route('/gct')
def gct():
    return render_template('gct.html')

@app.route('/peso_ideal')
def peso_ideal():
    return render_template('peso_ideal.html')

if __name__ == '__main__':
    app.run(debug=True)
