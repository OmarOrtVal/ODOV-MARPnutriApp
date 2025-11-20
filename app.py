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
            
            if sexo == 'Masculino':
                tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161
            
            if tmb < 1200:
                recomendacion = "Tu metabolismo basal es bajo. Consulta con un nutricionista para un plan personalizado."
            elif 1200 <= tmb < 1800:
                recomendacion = "Metabolismo normal. Esta es la energía que tu cuerpo necesita para funciones básicas en reposo."
            else:
                recomendacion = "Metabolismo alto. Tu cuerpo quema más calorías en reposo para mantener sus funciones vitales."
            
            return render_template('tmb.html', 
                                tmb_resultado=f"{tmb:.0f}",
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'edad': edad,
                                    'peso': peso,
                                    'altura': altura_cm,
                                    'sexo': sexo
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('tmb.html')
    
    return render_template('tmb.html')

@app.route('/gct', methods=['GET', 'POST'])
def gct():
    if request.method == 'POST':
        try:
            tmb = float(request.form.get('tmb'))
            actividad = request.form.get('actividad')
            
            factores_actividad = {
                'sedentario': {'factor': 1.2, 'descripcion': 'Sedentario (x1.2)'},
                'ligero': {'factor': 1.375, 'descripcion': 'Ligero (x1.375)'},
                'moderado': {'factor': 1.55, 'descripcion': 'Moderado (x1.55)'},
                'intenso': {'factor': 1.725, 'descripcion': 'Intenso (x1.725)'},
                'muy_intenso': {'factor': 1.9, 'descripcion': 'Muy intenso (x1.9)'}
            }
            
            if actividad in factores_actividad:
                factor = factores_actividad[actividad]['factor']
                gct = tmb * factor
                descripcion_actividad = factores_actividad[actividad]['descripcion']
            else:
                factor = 1.2
                gct = tmb * factor
                descripcion_actividad = factores_actividad['sedentario']['descripcion']
                actividad = 'sedentario'
            
            niveles_comparacion = {}
            for key, value in factores_actividad.items():
                niveles_comparacion[key] = {
                    'gct': tmb * value['factor'],
                    'descripcion': value['descripcion'],
                    'factor': value['factor']
                }
            
            if gct < 1500:
                recomendacion = "Tu gasto calórico es bajo. Considera aumentar tu actividad física gradualmente."
            elif 1500 <= gct < 2500:
                recomendacion = "Gasto calórico moderado. Ideal para mantener un estilo de vida equilibrado."
            else:
                recomendacion = "Gasto calórico alto. Asegúrate de consumir suficientes nutrientes para tu nivel de actividad."
            
            return render_template('gct.html', 
                                gct_resultado=f"{gct:.0f}",
                                factor_actividad=factor,
                                descripcion_actividad=descripcion_actividad,
                                niveles_comparacion=niveles_comparacion,
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'tmb': tmb,
                                    'actividad': actividad
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('gct.html')
    
    return render_template('gct.html')

@app.route('/peso_ideal', methods=['GET', 'POST'])
def peso_ideal():
    if request.method == 'POST':
        try:
            altura_cm = float(request.form.get('altura'))
            sexo = request.form.get('sexo')
            imc_objetivo = float(request.form.get('imc'))
            
            altura_m = altura_cm / 100
            
            peso_ideal_formula = (2.2 * imc_objetivo) + (3.5 * imc_objetivo * (altura_m - 1.5))
            
            peso_minimo_imc = 18.5 * (altura_m ** 2)
            peso_maximo_imc = 24.9 * (altura_m ** 2)
            peso_medio_imc = (peso_minimo_imc + peso_maximo_imc) / 2
            
            if imc_objetivo < 18.5:
                recomendacion = "IMC objetivo en rango bajo. Consulta con un profesional de la salud."
            elif 18.5 <= imc_objetivo <= 24.9:
                recomendacion = "IMC objetivo en rango saludable. Excelente elección."
            else:
                recomendacion = "IMC objetivo en rango de sobrepeso. Considera un objetivo más bajo para mejor salud."
            
            return render_template('peso_ideal.html', 
                                peso_ideal_formula=f"{peso_ideal_formula:.2f}",
                                peso_medio_imc=f"{peso_medio_imc:.2f}",
                                imc_objetivo=imc_objetivo,
                                rango_saludable={
                                    'minimo': peso_minimo_imc,
                                    'maximo': peso_maximo_imc
                                },
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'altura': altura_cm,
                                    'sexo': sexo,
                                    'imc': imc_objetivo
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('peso_ideal.html')
    
    return render_template('peso_ideal.html')

if __name__ == '__main__':
    app.run(debug=True)
