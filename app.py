from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'nutri_track_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nutritrackop'

mysql = MySQL(app)

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


def crear_tablas():
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                fecha_nacimiento DATE,
                genero ENUM('Mujer', 'Hombre', 'Personalizado'),
                peso DECIMAL(5,2),
                altura DECIMAL(5,2),
                actividad_fisica VARCHAR(50),
                dieta_especifica VARCHAR(50),
                experiencia_cocina VARCHAR(50),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario_objetivos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                objetivo VARCHAR(100),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario_alergias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                alergia VARCHAR(100),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario_intolerancias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                intolerancia VARCHAR(100),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        ''')
        
        mysql.connection.commit()
        print("Tablas creadas exitosamente")
    except Exception as e:
        print(f"Error creando tablas: {e}")

def email_existe(email):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error verificando email: {e}")
        return False

def registrar_usuario_db(nombre, apellido, email, password, fecha_nacimiento=None, 
                        genero=None, peso=None, altura=None, actividad_fisica=None, 
                        dieta_especifica=None, experiencia_cocina=None, objetivos=None, 
                        alergias=None, intolerancias=None):
    try:
        cursor = mysql.connection.cursor()
        
        hashed_password = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, password, fecha_nacimiento, 
                                genero, peso, altura, actividad_fisica, dieta_especifica, experiencia_cocina) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nombre, apellido, email, hashed_password, fecha_nacimiento, genero, 
            peso, altura, actividad_fisica, dieta_especifica, experiencia_cocina))
        
        usuario_id = cursor.lastrowid
        
        if objetivos:
            for objetivo in objetivos:
                cursor.execute('''
                    INSERT INTO usuario_objetivos (usuario_id, objetivo) 
                    VALUES (%s, %s)
                ''', (usuario_id, objetivo))
        
        if alergias:
            for alergia in alergias:
                cursor.execute('''
                    INSERT INTO usuario_alergias (usuario_id, alergia) 
                    VALUES (%s, %s)
                ''', (usuario_id, alergia))
        
        if intolerancias:
            for intolerancia in intolerancias:
                cursor.execute('''
                    INSERT INTO usuario_intolerancias (usuario_id, intolerancia) 
                    VALUES (%s, %s)
                ''', (usuario_id, intolerancia))
        
        mysql.connection.commit()
        return True, "Usuario registrado exitosamente"
    except Exception as e:
        mysql.connection.rollback()
        return False, f"Error registrando usuario: {e}"

def verificar_usuario(email, password):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nombre, email, password FROM usuarios WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        
        if usuario and check_password_hash(usuario[3], password):
            return {
                'id': usuario[0],
                'nombre': usuario[1],
                'email': usuario[2]
            }
        return None
    except Exception as e:
        print(f"Error verificando usuario: {e}")
        return None


@app.context_processor
def inject_user_data():
    current_user = 'user_id' in session
    user_nombre = session.get('user_nombre', 'Invitado')
    return dict(current_user=current_user, user_nombre=user_nombre)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    
    cursor.execute('''
        SELECT nombre, apellido, email, fecha_nacimiento, genero, peso, altura, 
            actividad_fisica, dieta_especifica, experiencia_cocina 
        FROM usuarios 
        WHERE id = %s
    ''', (session['user_id'],))
    
    usuario = cursor.fetchone()
    
    cursor.execute('SELECT objetivo FROM usuario_objetivos WHERE usuario_id = %s', (session['user_id'],))
    objetivos = cursor.fetchall()
    
    cursor.execute('SELECT alergia FROM usuario_alergias WHERE usuario_id = %s', (session['user_id'],))
    alergias = cursor.fetchall()
    
    cursor.execute('SELECT intolerancia FROM usuario_intolerancias WHERE usuario_id = %s', (session['user_id'],))
    intolerancias = cursor.fetchall()
    
    datos_usuario = {}
    if usuario:
        datos_usuario = {
            'nombre': f"{usuario[0]} {usuario[1]}" if usuario[0] and usuario[1] else '',
            'email': usuario[2] if usuario[2] else '',
            'fecha_nacimiento': usuario[3] if usuario[3] else '',
            'sexo': usuario[4] if usuario[4] else '',
            'peso': usuario[5] if usuario[5] else '',
            'altura': usuario[6] if usuario[6] else '',
            'actividad_fisica': usuario[7] if usuario[7] else '',
            'dieta_especifica': usuario[8] if usuario[8] else '',
            'experiencia_cocina': usuario[9] if usuario[9] else '',
            'objetivos': [objetivo[0] for objetivo in objetivos] if objetivos else [],
            'alergias': [alergia[0] for alergia in alergias] if alergias else [],
            'intolerancias': [intolerancia[0] for intolerancia in intolerancias] if intolerancias else []
        }
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        peso = request.form.get('peso')
        altura = request.form.get('altura')
        objetivo = request.form.get('objetivo')
        
        datos_usuario.update({
            'nombre': nombre,
            'edad': edad,
            'sexo': sexo,
            'peso': peso,
            'altura': altura,
            'objetivo': objetivo
        })
        
        flash('Perfil actualizado correctamente', 'success')
        return render_template('perfil.html', datos=datos_usuario)
    
    return render_template('perfil.html', datos=datos_usuario)

@app.route('/seguimiento')
def seguimiento():
    if 'user_id' not in session:
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
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    return render_template('recetas.html')

@app.route('/analizador_de_recetas')
def analizador_de_recetas():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    return render_template('analizador_de_recetas.html')

@app.route('/habitos')
def habitos():
    return render_template('habitos.html')

@app.route('/alimentos')
def alimentos():    
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    return render_template('alimentos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_login = request.form.get('email_login')
        password_login = request.form.get('password_login')
        
        usuario = verificar_usuario(email_login, password_login)
        
        if usuario:
            session['user_id'] = usuario['id']
            session['user_email'] = usuario['email']
            session['user_nombre'] = usuario['nombre']
            flash(f"¡Bienvenido de nuevo, {usuario['nombre']}!", 'success')
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
        
        dia_nacimiento = request.form.get('dia')
        mes_nacimiento = request.form.get('mes')
        anio_nacimiento = request.form.get('anio')
        genero = request.form.get('genero')
        peso = request.form.get('peso')
        altura = request.form.get('altura')
        actividad_fisica = request.form.get('actividad_fisica')
        objetivos = request.form.getlist('objetivos')
        alergias = request.form.getlist('alergias')
        intolerancias = request.form.getlist('intolerancias')
        dieta_especifica = request.form.get('dieta_especifica')
        experiencia_cocina = request.form.get('experiencia_cocina')
        
        if not nombre or not apellido or not email or not contrasena:
            flash('Por favor complete todos los campos obligatorios.', 'danger')
            return render_template('registro.html')
        
        if contrasena != confirma:
            flash("Las contraseñas no coinciden.", 'danger')
            return render_template('registro.html')
        
        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('registro.html')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Por favor ingrese un email válido.', 'danger')
            return render_template('registro.html')
        
        if email_existe(email):
            flash("Este correo ya está registrado.", 'warning')
            return render_template('registro.html')
        
        fecha_nacimiento = None
        if dia_nacimiento and mes_nacimiento and anio_nacimiento:
            try:
                fecha_nacimiento = f"{anio_nacimiento}-{mes_nacimiento}-{dia_nacimiento}"
            except:
                pass
        
        try:
            peso = float(peso) if peso else None
        except:
            peso = None
            
        try:
            altura = float(altura) if altura else None
        except:
            altura = None
        
        success, message = registrar_usuario_db(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=contrasena,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            peso=peso,
            altura=altura,
            actividad_fisica=actividad_fisica,
            dieta_especifica=dieta_especifica,
            experiencia_cocina=experiencia_cocina,
            objetivos=objetivos,
            alergias=alergias,
            intolerancias=intolerancias
        )
        
        if success:
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Error en el registro: {message}', 'danger')
        
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_nombre', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/calculadoras')
def calculadoras():
    return render_template('calculadoras.html')

@app.route('/herramientas_de_recetas')
def herramientas_de_recetas():
    return render_template('herramientas_de_recetas.html')

@app.route('/imc', methods=['GET', 'POST'])
def imc():
    if request.method == 'POST':
        try:
            peso = float(request.form.get('peso'))
            altura_cm = float(request.form.get('altura'))
            
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
                                recomendacion=recomendacion)
            
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
                                recomendacion=recomendacion)
            
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
                'sedentario': 1.2,
                'ligero': 1.375,
                'moderado': 1.55,
                'intenso': 1.725,
                'muy_intenso': 1.9
            }
            
            if actividad in factores_actividad:
                factor = factores_actividad[actividad]
                gct = tmb * factor
            else:
                factor = 1.2
                gct = tmb * factor
                actividad = 'sedentario'
            
            if gct < 1500:
                recomendacion = "Tu gasto calórico es bajo. Considera aumentar tu actividad física gradualmente."
            elif 1500 <= gct < 2500:
                recomendacion = "Gasto calórico moderado. Ideal para mantener un estilo de vida equilibrado."
            else:
                recomendacion = "Gasto calórico alto. Asegúrate de consumir suficientes nutrientes para tu nivel de actividad."
            
            return render_template('gct.html', 
                                gct_resultado=f"{gct:.0f}",
                                recomendacion=recomendacion)
            
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
            
            if sexo == 'Masculino':
                peso_ideal_formula = (altura_cm - 100) - ((altura_cm - 150) / 4)
            else: 
                peso_ideal_formula = (altura_cm - 100) - ((altura_cm - 150) / 2.5)
            
            altura_m = altura_cm / 100
            
            peso_minimo_imc = 18.5 * (altura_m ** 2)
            peso_maximo_imc = 24.9 * (altura_m ** 2)
            peso_medio_imc = (peso_minimo_imc + peso_maximo_imc) / 2
            
            if peso_ideal_formula < peso_minimo_imc:
                recomendacion = f"Tu peso ideal según Lorentz ({peso_ideal_formula:.1f} kg) está por debajo del rango saludable mínimo ({peso_minimo_imc:.1f} kg). Considera consultar con un nutricionista."
            elif peso_ideal_formula > peso_maximo_imc:
                recomendacion = f"Tu peso ideal según Lorentz ({peso_ideal_formula:.1f} kg) está por encima del rango saludable máximo ({peso_maximo_imc:.1f} kg). Un profesional puede ayudarte a establecer metas realistas."
            else:
                recomendacion = f"¡Excelente! Tu peso ideal según Lorentz ({peso_ideal_formula:.1f} kg) está dentro del rango saludable recomendado ({peso_minimo_imc:.1f} - {peso_maximo_imc:.1f} kg)."
            
            return render_template('peso_ideal.html', 
                                peso_ideal_formula=f"{peso_ideal_formula:.2f}",
                                peso_medio_imc=f"{peso_medio_imc:.2f}",
                                rango_saludable={
                                    'minimo': peso_minimo_imc,
                                    'maximo': peso_maximo_imc
                                },
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'altura': altura_cm,
                                    'sexo': sexo
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('peso_ideal.html')
    
    return render_template('peso_ideal.html')

@app.route('/macronutrientes', methods=['GET', 'POST'])
def macronutrientes():
    if 'user_email' not in session:
        flash('Debes iniciar sesión para acceder a esta función.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            objetivo = request.form.get('objetivo')
            peso = float(request.form.get('peso'))
            altura = float(request.form.get('altura'))
            edad = int(request.form.get('edad'))
            sexo = request.form.get('sexo')
            nivel_actividad = request.form.get('nivel_actividad')
            
            if sexo == 'Masculino':
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161
            
            factores_actividad = {
                'sedentario': 1.2,
                'ligero': 1.375,
                'moderado': 1.55,
                'intenso': 1.725,
                'atleta': 1.9
            }
            
            get = tmb * factores_actividad.get(nivel_actividad, 1.2)
            
            if objetivo == 'perder':
                calorias_objetivo = get - 500
            elif objetivo == 'ganar':
                calorias_objetivo = get + 500
            else: 
                calorias_objetivo = get
            
            proteinas_gramos = peso * 2.0
            proteinas_calorias = proteinas_gramos * 4
            
            grasas_calorias = calorias_objetivo * 0.25
            grasas_gramos = grasas_calorias / 9
            
            carbohidratos_calorias = calorias_objetivo - proteinas_calorias - grasas_calorias
            carbohidratos_gramos = carbohidratos_calorias / 4
            
            porc_proteinas = (proteinas_calorias / calorias_objetivo) * 100
            porc_grasas = (grasas_calorias / calorias_objetivo) * 100
            porc_carbohidratos = (carbohidratos_calorias / calorias_objetivo) * 100
            
            if objetivo == 'perder':
                recomendacion = f"Para perder peso, se recomienda un déficit de 500 calorías. Tu distribución ideal es: {porc_proteinas:.0f}% proteínas, {porc_carbohidratos:.0f}% carbohidratos, {porc_grasas:.0f}% grasas."
            elif objetivo == 'ganar':
                recomendacion = f"Para ganar masa muscular, se recomienda un superávit de 500 calorías. Asegúrate de consumir suficientes proteínas ({proteinas_gramos:.0f}g) para apoyar el crecimiento muscular."
            else:
                recomendacion = f"Para mantener tu peso, sigue consumiendo {calorias_objetivo:.0f} calorías diarias con esta distribución balanceada de macronutrientes."
            
            return render_template('macronutrientes.html', 
                                tmb=f"{tmb:.0f}",
                                get=f"{get:.0f}",
                                calorias_objetivo=f"{calorias_objetivo:.0f}",
                                macronutrientes={
                                    'proteinas_gramos': f"{proteinas_gramos:.1f}",
                                    'proteinas_calorias': f"{proteinas_calorias:.0f}",
                                    'proteinas_porcentaje': f"{porc_proteinas:.1f}",
                                    'grasas_gramos': f"{grasas_gramos:.1f}",
                                    'grasas_calorias': f"{grasas_calorias:.0f}",
                                    'grasas_porcentaje': f"{porc_grasas:.1f}",
                                    'carbohidratos_gramos': f"{carbohidratos_gramos:.1f}",
                                    'carbohidratos_calorias': f"{carbohidratos_calorias:.0f}",
                                    'carbohidratos_porcentaje': f"{porc_carbohidratos:.1f}"
                                },
                                recomendacion=recomendacion,
                                datos_formulario={
                                    'objetivo': objetivo,
                                    'peso': peso,
                                    'altura': altura,
                                    'edad': edad,
                                    'sexo': sexo,
                                    'nivel_actividad': nivel_actividad
                                })
            
        except (ValueError, TypeError):
            flash('Por favor ingresa valores válidos para todos los campos.', 'danger')
            return render_template('macronutrientes.html')
    
    return render_template('macronutrientes.html')

if __name__ == '__main__':
    with app.app_context():
        crear_tablas()
    app.run(debug=True)