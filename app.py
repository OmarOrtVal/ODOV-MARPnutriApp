from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'nutri_track_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nutritrack'

mysql = MySQL(app)

USDA_API_KEY = 'eIQi6Rf8Ew3HUMZCJTVLaxe4DC8P4UsalKvWK6Xn'  
USDA_API_URL = 'https://api.nal.usda.gov/fdc/v1'

ARTICLES = [
    {
        'id': 1,
        'titulo': '¿Cómo leer las etiquetas nutricionales?',
        'contenido': 'Las etiquetas nutricionales son una herramienta esencial para comprender lo que estás consumiendo. Permiten comparar productos, controlar calorías y conocer los nutrientes que aportan los alimentos.',
        'categoria': 'Educación nutricional',
        'tiempo_lectura': '5 min'
    },
    {
        'id': 2,
        'titulo': 'Mitos y verdades sobre las dietas de moda',
        'contenido': 'Muchas dietas prometen resultados rápidos, pero no todas son saludables o sostenibles. Analiza la evidencia científica antes de seguir una tendencia alimentaria.',
        'categoria': 'Dietas y salud',
        'tiempo_lectura': '7 min'
    },
    {
        'id': 3,
        'titulo': 'Guías sobre macronutrientes y su función',
        'contenido': 'Los macronutrientes son los principales aportadores de energía. Incluyen proteínas, carbohidratos y grasas, todos esenciales para el correcto funcionamiento del cuerpo.',
        'categoria': 'Nutrición básica',
        'tiempo_lectura': '6 min'
    },
    {
        'id': 4,
        'titulo': 'La importancia de la hidratación, la fibra, etc.',
        'contenido': 'El agua y la fibra juegan un papel vital en la salud digestiva, la regulación del apetito y el bienestar general. Su consumo diario es clave para mantener el equilibrio corporal.',
        'categoria': 'Salud general',
        'tiempo_lectura': '5 min'
    },
    {
        'id': 5,
        'titulo': 'Planificación de comidas para una semana saludable',
        'contenido': 'Aprende a organizar tus comidas semanales para mantener una alimentación balanceada, ahorrar tiempo y dinero, y evitar decisiones impulsivas poco saludables.',
        'categoria': 'Planificación alimentaria',
        'tiempo_lectura': '8 min'
    },
    {
        'id': 6,
        'titulo': 'El rol de los antioxidantes en la salud',
        'contenido': 'Los antioxidantes combaten el estrés oxidativo y previenen el envejecimiento celular. Descubre qué alimentos son ricos en estos compuestos y cómo incorporarlos en tu dieta.',
        'categoria': 'Nutrición avanzada',
        'tiempo_lectura': '6 min'
    },
    {
        'id': 7,
        'titulo': 'Alimentación para el control de la diabetes',
        'contenido': 'Conoce los principios básicos de la alimentación para el manejo de la glucosa en sangre, incluyendo el índice glucémico y el conteo de carbohidratos.',
        'categoria': 'Condiciones específicas',
        'tiempo_lectura': '10 min'
    },
    {
        'id': 8,
        'titulo': 'Suplementos nutricionales: ¿Cuándo y por qué?',
        'contenido': 'Analizamos cuándo es necesario considerar suplementos vitamínicos, qué tipos existen y cómo elegirlos de manera segura y efectiva.',
        'categoria': 'Suplementación',
        'tiempo_lectura': '9 min'
    },
    {
        'id': 9,
        'titulo': 'Alimentación consciente: Más allá de lo que comes',
        'contenido': 'La alimentación consciente no solo se trata de qué comes, sino de cómo comes. Aprende técnicas para mejorar tu relación con la comida y reconocer señales de hambre y saciedad.',
        'categoria': 'Psicología alimentaria',
        'tiempo_lectura': '7 min'
    },
    {
        'id': 10,
        'titulo': 'Nutrición para el rendimiento deportivo',
        'contenido': 'Optimiza tu alimentación antes, durante y después del ejercicio para maximizar tu rendimiento físico y mejorar tu recuperación.',
        'categoria': 'Nutrición deportiva',
        'tiempo_lectura': '8 min'
    }
]

RECETAS = [
    {
        'id': 1,
        'nombre': 'Omelette Proteico',
        'categoria': 'Desayuno',
        'tiempo': 15,
        'dificultad': 'Principiante',
        'calorias': 250,
        'ingredientes': ['2 huevos', '50g queso fresco', '1 tomate', 'Espinacas'],
        'instrucciones': 'Batir los huevos, agregar vegetales y cocinar en sartén antiadherente.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 2,
        'nombre': 'Avena con Frutos Rojos',
        'categoria': 'Desayuno',
        'tiempo': 10,
        'dificultad': 'Principiante',
        'calorias': 180,
        'ingredientes': ['1/2 taza avena', '1 taza leche almendra', '1/2 taza frutos rojos', '1 cda miel'],
        'instrucciones': 'Cocinar avena con leche, agregar frutos rojos y endulzar con miel.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 3,
        'nombre': 'Tostadas de Aguacate',
        'categoria': 'Desayuno',
        'tiempo': 5,
        'dificultad': 'Principiante',
        'calorias': 220,
        'ingredientes': ['2 rebanadas pan integral', '1/2 aguacate', '1 huevo', 'Sal y pimienta'],
        'instrucciones': 'Tostar pan, untar aguacate y agregar huevo cocido.',
        'tipo_dieta': 'Vegetariano',
        'ingredientes_principales': 4
    },
    {
        'id': 4,
        'nombre': 'Smoothie Verde Energético',
        'categoria': 'Desayuno',
        'tiempo': 5,
        'dificultad': 'Principiante',
        'calorias': 190,
        'ingredientes': ['1 plátano', '1 taza espinacas', '1 taza leche almendra', '1 cda chía'],
        'instrucciones': 'Licuar todos los ingredientes hasta obtener consistencia suave.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 5,
        'nombre': 'Yogurt con Granola',
        'categoria': 'Desayuno',
        'tiempo': 2,
        'dificultad': 'Principiante',
        'calorias': 200,
        'ingredientes': ['1 taza yogurt griego', '1/4 taza granola', '1/2 taza frutas frescas', 'Miel al gusto'],
        'instrucciones': 'Servir yogurt, agregar granola y frutas, endulzar con miel.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 6,
        'nombre': 'Huevos Revueltos con Espinacas',
        'categoria': 'Desayuno',
        'tiempo': 10,
        'dificultad': 'Principiante',
        'calorias': 230,
        'ingredientes': ['2 huevos', '1 taza espinacas', '1/4 cebolla', 'Aceite de oliva'],
        'instrucciones': 'Saltear espinacas y cebolla, agregar huevos batidos y revolver.',
        'tipo_dieta': 'Vegetariano',
        'ingredientes_principales': 4
    },
    {
        'id': 7,
        'nombre': 'Pancakes de Avena',
        'categoria': 'Desayuno',
        'tiempo': 20,
        'dificultad': 'Intermedio',
        'calorias': 280,
        'ingredientes': ['1 taza avena', '1 huevo', '1/2 taza leche', '1 cda miel'],
        'instrucciones': 'Mezclar ingredientes, cocinar en sartén y servir con frutas.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 8,
        'nombre': 'Pudín de Chía',
        'categoria': 'Desayuno',
        'tiempo': 5,
        'dificultad': 'Principiante',
        'calorias': 170,
        'ingredientes': ['3 cdas chía', '1 taza leche almendra', '1 cda miel', 'Frutas al gusto'],
        'instrucciones': 'Mezclar chía con leche, refrigerar toda la noche, agregar frutas.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 9,
        'nombre': 'Tortilla de Claras',
        'categoria': 'Desayuno',
        'tiempo': 10,
        'dificultad': 'Principiante',
        'calorias': 150,
        'ingredientes': ['3 claras de huevo', '1 taza vegetales mixtos', 'Especias al gusto'],
        'instrucciones': 'Batir claras, agregar vegetales y cocinar en sartén.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 3
    },
    {
        'id': 10,
        'nombre': 'Batido de Proteína',
        'categoria': 'Desayuno',
        'tiempo': 5,
        'dificultad': 'Principiante',
        'calorias': 210,
        'ingredientes': ['1 scoop proteína', '1 taza leche', '1/2 plátano', '1 cda mantequilla maní'],
        'instrucciones': 'Licuar todos los ingredientes hasta mezclar completamente.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },

    {
        'id': 11,
        'nombre': 'Ensalada César Saludable',
        'categoria': 'Almuerzo',
        'tiempo': 15,
        'dificultad': 'Principiante',
        'calorias': 320,
        'ingredientes': ['2 tazas lechuga', '100g pollo', '2 cdas aderezo light', '30g queso parmesano'],
        'instrucciones': 'Mezclar todos los ingredientes y agregar aderezo al servir.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 12,
        'nombre': 'Wrap de Atún y Aguacate',
        'categoria': 'Almuerzo',
        'tiempo': 10,
        'dificultad': 'Principiante',
        'calorias': 280,
        'ingredientes': ['1 tortilla integral', '1 lata atún', '1/2 aguacate', 'Verduras al gusto'],
        'instrucciones': 'Rellenar tortilla con ingredientes y enrollar.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 13,
        'nombre': 'Buddha Bowl Vegano',
        'categoria': 'Almuerzo',
        'tiempo': 20,
        'dificultad': 'Intermedio',
        'calorias': 350,
        'ingredientes': ['1/2 taza quinoa', '1 taza garbanzos', 'Verduras asadas', 'Aguacate'],
        'instrucciones': 'Cocinar quinoa, asar vegetales y armar bowl con todos los ingredientes.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 14,
        'nombre': 'Salmón con Espárragos',
        'categoria': 'Almuerzo',
        'tiempo': 25,
        'dificultad': 'Intermedio',
        'calorias': 380,
        'ingredientes': ['200g salmón', '1 manojo espárragos', 'Aceite de oliva', 'Limón'],
        'instrucciones': 'Sazonar salmón y espárragos, hornear a 180°C por 20 minutos.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 15,
        'nombre': 'Ensalada de Quinoa',
        'categoria': 'Almuerzo',
        'tiempo': 15,
        'dificultad': 'Principiante',
        'calorias': 290,
        'ingredientes': ['1 taza quinoa cocida', 'Verduras picadas', 'Aceite de oliva', 'Limón'],
        'instrucciones': 'Mezclar quinoa con vegetales y aderezar.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 16,
        'nombre': 'Pollo al Curry',
        'categoria': 'Almuerzo',
        'tiempo': 30,
        'dificultad': 'Intermedio',
        'calorias': 420,
        'ingredientes': ['200g pollo', '1 cebolla', '1 lata leche de coco', '2 cdas curry'],
        'instrucciones': 'Sofreír ingredientes, agregar leche de coco y cocinar 20 min.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 17,
        'nombre': 'Sopa de Lentejas',
        'categoria': 'Almuerzo',
        'tiempo': 40,
        'dificultad': 'Intermedio',
        'calorias': 310,
        'ingredientes': ['1 taza lentejas', '2 zanahorias', '1 cebolla', 'Caldo vegetal'],
        'instrucciones': 'Cocinar todos los ingredientes hasta que las lentejas estén tiernas.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 18,
        'nombre': 'Tacos de Pescado',
        'categoria': 'Almuerzo',
        'tiempo': 20,
        'dificultad': 'Intermedio',
        'calorias': 340,
        'ingredientes': ['200g filete de pescado', '4 tortillas', 'Repollo', 'Salsa yogurt'],
        'instrucciones': 'Cocinar pescado, armar tacos con vegetales y salsa.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 19,
        'nombre': 'Risotto de Champiñones',
        'categoria': 'Almuerzo',
        'tiempo': 35,
        'dificultad': 'Avanzado',
        'calorias': 380,
        'ingredientes': ['1 taza arroz arbóreo', '200g champiñones', 'Caldo vegetal', 'Queso parmesano'],
        'instrucciones': 'Cocinar arroz agregando caldo poco a poco, incorporar champiñones.',
        'tipo_dieta': 'Vegetariano',
        'ingredientes_principales': 4
    },
    {
        'id': 20,
        'nombre': 'Enchiladas Saludables',
        'categoria': 'Almuerzo',
        'tiempo': 30,
        'dificultad': 'Intermedio',
        'calorias': 360,
        'ingredientes': ['4 tortillas', '200g pollo', 'Salsa tomate', 'Queso light'],
        'instrucciones': 'Rellenar tortillas, enrollar, cubrir con salsa y hornear.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },

    {
        'id': 21,
        'nombre': 'Pescado al Horno con Verduras',
        'categoria': 'Cena',
        'tiempo': 30,
        'dificultad': 'Principiante',
        'calorias': 280,
        'ingredientes': ['200g filete de pescado', 'Verduras mixtas', 'Aceite de oliva', 'Limón'],
        'instrucciones': 'Sazonar y hornear pescado con verduras a 180°C por 25 min.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 22,
        'nombre': 'Crema de Calabacín',
        'categoria': 'Cena',
        'tiempo': 25,
        'dificultad': 'Principiante',
        'calorias': 190,
        'ingredientes': ['2 calabacines', '1 cebolla', 'Caldo vegetal', 'Especias'],
        'instrucciones': 'Cocinar vegetales, licuar y servir caliente.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 23,
        'nombre': 'Tortilla de Espinacas',
        'categoria': 'Cena',
        'tiempo': 15,
        'dificultad': 'Principiante',
        'calorias': 220,
        'ingredientes': ['3 huevos', '2 tazas espinacas', 'Queso feta', 'Aceite de oliva'],
        'instrucciones': 'Saltear espinacas, agregar huevos batidos y cocinar.',
        'tipo_dieta': 'Vegetariano',
        'ingredientes_principales': 4
    },
    {
        'id': 24,
        'nombre': 'Pechuga de Pollo a la Plancha',
        'categoria': 'Cena',
        'tiempo': 20,
        'dificultad': 'Principiante',
        'calorias': 250,
        'ingredientes': ['150g pechuga pollo', 'Verduras al vapor', 'Aceite de oliva', 'Especias'],
        'instrucciones': 'Sazonar pollo y cocinar a la plancha, servir con verduras.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 25,
        'nombre': 'Ensalada de Garbanzos',
        'categoria': 'Cena',
        'tiempo': 10,
        'dificultad': 'Principiante',
        'calorias': 230,
        'ingredientes': ['1 taza garbanzos', 'Pepino', 'Tomate', 'Aceite de oliva'],
        'instrucciones': 'Mezclar todos los ingredientes y aderezar.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 26,
        'nombre': 'Calabacines Rellenos',
        'categoria': 'Cena',
        'tiempo': 35,
        'dificultad': 'Intermedio',
        'calorias': 270,
        'ingredientes': ['2 calabacines', 'Carne molida', 'Salsa tomate', 'Queso'],
        'instrucciones': 'Vaciar calabacines, rellenar y hornear 25 min.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
    },
    {
        'id': 27,
        'nombre': 'Sopa Miso',
        'categoria': 'Cena',
        'tiempo': 15,
        'dificultad': 'Principiante',
        'calorias': 150,
        'ingredientes': ['Pasta miso', 'Tofu', 'Algas', 'Cebollín'],
        'instrucciones': 'Disolver miso en agua caliente, agregar ingredientes.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 28,
        'nombre': 'Hamburguesa de Lentejas',
        'categoria': 'Cena',
        'tiempo': 30,
        'dificultad': 'Intermedio',
        'calorias': 290,
        'ingredientes': ['1 taza lentejas', 'Avena', 'Especias', 'Pan integral'],
        'instrucciones': 'Mezclar ingredientes, formar hamburguesas y cocinar.',
        'tipo_dieta': 'Vegano',
        'ingredientes_principales': 4
    },
    {
        'id': 29,
        'nombre': 'Pizza de Coliflor',
        'categoria': 'Cena',
        'tiempo': 40,
        'dificultad': 'Avanzado',
        'calorias': 320,
        'ingredientes': ['1 coliflor', 'Huevo', 'Salsa tomate', 'Queso'],
        'instrucciones': 'Preparar base de coliflor, agregar ingredientes y hornear.',
        'tipo_dieta': 'Vegetariano',
        'ingredientes_principales': 4
    },
    {
        'id': 30,
        'nombre': 'Rollitos de Lechuga',
        'categoria': 'Cena',
        'tiempo': 20,
        'dificultad': 'Principiante',
        'calorias': 180,
        'ingredientes': ['Hojas de lechuga', 'Pollo desmenuzado', 'Verduras', 'Salsa'],
        'instrucciones': 'Rellenar hojas de lechuga con ingredientes y enrollar.',
        'tipo_dieta': 'Standard',
        'ingredientes_principales': 4
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alimentos_registrados (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                alimento VARCHAR(255) NOT NULL,
                cantidad DECIMAL(8,2) NOT NULL,
                unidad VARCHAR(50) NOT NULL,
                calorias DECIMAL(8,2) NOT NULL,
                proteinas DECIMAL(8,2),
                carbohidratos DECIMAL(8,2),
                grasas DECIMAL(8,2),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

def parsear_ingrediente(texto_ingrediente):
    try:
        texto = texto_ingrediente.lower().strip()
        
        cantidad_match = re.match(r'^(\d+(\.\d+)?)\s*', texto)
        cantidad = 1.0
        
        if cantidad_match:
            cantidad = float(cantidad_match.group(1))
            texto = texto[cantidad_match.end():].strip()
        
        unidades = ['taza', 'tazas', 'cucharada', 'cucharadas', 'cda', 'cdas', 
                'cucharadita', 'cucharaditas', 'gramo', 'gramos', 'g', 'kg',
                'libra', 'libras', 'lb', 'onza', 'onzas', 'oz', 'unidad', 'unidades',
                'pizca', 'pizcas', 'diente', 'dientes', 'hoja', 'hojas']
        
        unidad = 'unidad'
        nombre = texto
        
        for u in unidades:
            if texto.startswith(u + ' ') or texto.startswith(u + 's '):
                unidad = u
                if unidad.endswith('s'):
                    unidad = unidad[:-1] 
                texto = texto[len(u):].strip()
                if texto.startswith('de '):
                    texto = texto[3:].strip()
                nombre = texto
                break
        
        return {
            'cantidad': cantidad,
            'unidad': unidad,
            'nombre': nombre.title()
        }
    
    except Exception as e:
        return {
            'cantidad': 1,
            'unidad': 'unidad',
            'nombre': texto_ingrediente.title()
        }

def analizar_receta_api(ingredientes):
    try:
        nutrientes_totales = {
            'calorias': 0,
            'proteinas': 0,
            'grasas': 0,
            'carbohidratos': 0
        }
        
        ingredientes_encontrados = []
        ingredientes_no_encontrados = []
        
        for ingrediente in ingredientes:
            
            resultados = buscar_alimentos_usda_simple(ingrediente['nombre'])
            
            ingrediente_encontrado = False
            
            if resultados and len(resultados) > 0:
                alimento = resultados[0]
                fdc_id = alimento.get('fdc_id')
                
                if fdc_id:
                    detalle_nutrientes = obtener_nutrientes_usda_simple(fdc_id)
                    
                    if detalle_nutrientes and detalle_nutrientes.get('nutrientes'):
                        nutrientes = detalle_nutrientes['nutrientes']
                        
                        cantidad_gramos = convertir_a_gramos(ingrediente['cantidad'], ingrediente['unidad'])
                        factor = cantidad_gramos / 100.0  
                        
                        ingrediente_analizado = {
                            'nombre': ingrediente['nombre'],
                            'cantidad': ingrediente['cantidad'],
                            'unidad': ingrediente['unidad'],
                            'cantidad_gramos': cantidad_gramos,
                            'calorias': nutrientes.get('calorias', 0) * factor,
                            'proteinas': nutrientes.get('proteinas', 0) * factor,
                            'grasas': nutrientes.get('grasas', 0) * factor,
                            'carbohidratos': nutrientes.get('carbohidratos', 0) * factor,
                            'encontrado_en_api': True,
                            'estado': 'encontrado',
                            'fdc_id': fdc_id,
                            'descripcion_usda': detalle_nutrientes.get('nombre', '')
                        }
                                                
                        nutrientes_totales['calorias'] += ingrediente_analizado['calorias']
                        nutrientes_totales['proteinas'] += ingrediente_analizado['proteinas']
                        nutrientes_totales['grasas'] += ingrediente_analizado['grasas']
                        nutrientes_totales['carbohidratos'] += ingrediente_analizado['carbohidratos']
                        
                        ingredientes_encontrados.append(ingrediente_analizado)
                        ingrediente_encontrado = True

            
            if not ingrediente_encontrado:
                ingrediente_no_encontrado = {
                    'nombre': ingrediente['nombre'],
                    'cantidad': ingrediente['cantidad'],
                    'unidad': ingrediente['unidad'],
                    'cantidad_gramos': convertir_a_gramos(ingrediente['cantidad'], ingrediente['unidad']),
                    'calorias': 0,
                    'proteinas': 0,
                    'grasas': 0,
                    'carbohidratos': 0,
                    'encontrado_en_api': False,
                    'estado': 'no_encontrado',
                    'fdc_id': None,
                    'descripcion_usda': None
                }
                ingredientes_no_encontrados.append(ingrediente_no_encontrado)
        
        todos_los_ingredientes = ingredientes_encontrados + ingredientes_no_encontrados
        return {
            'nutrientes_totales': nutrientes_totales,
            'ingredientes_analizados': todos_los_ingredientes,
            'ingredientes_encontrados': ingredientes_encontrados,
            'ingredientes_no_encontrados': ingredientes_no_encontrados,
            'total_encontrados': len(ingredientes_encontrados),
            'total_no_encontrados': len(ingredientes_no_encontrados),
            'total_ingredientes': len(ingredientes)
        }
    
    except Exception as e:
        print(f"Error analizando receta: {e}") 
        return None

def convertir_a_gramos(cantidad, unidad):
    try:
        unidad = unidad.lower().strip()
        conversiones = {
            'taza': 240,           
            'tazas': 240,
            'cucharada': 15,       
            'cucharadas': 15,
            'cda': 15,
            'cdas': 15,
            'cucharadita': 5,     
            'cucharaditas': 5,
            'cucharita': 5,
            'cucharitas': 5,
            
            'gramo': 1,
            'gramos': 1,
            'g': 1,
            'kg': 1000,
            'kilogramo': 1000,
            'kilogramos': 1000,
            'libra': 453.592,      
            'libras': 453.592,
            'lb': 453.592,
            'onza': 28.3495,      
            'onzas': 28.3495,
            'oz': 28.3495,
            
            'unidad': 100,         
            'unidades': 100,
            'pieza': 100,
            'piezas': 100,
            'pizca': 0.5,         
            'pizcas': 0.5,
            'diente': 5,           
            'dientes': 5,
            'hoja': 3,            
            'hojas': 3,
            'rebanada': 30,       
            'rebanadas': 30,
            'filete': 150,         
            'filetes': 150,
            'lata': 400,           
            'latas': 400,
            'rodaja': 20,          
            'rodajas': 20
        }
        
        if unidad in conversiones:
            return cantidad * conversiones[unidad]
        else:
            return cantidad  
    
    except Exception as e:
        print(f"Error en convertir_a_gramos: {e}")
        return cantidad

def buscar_alimentos_usda_simple(query):
    try:
        url = f"{USDA_API_URL}/foods/search"
        params = {
            'api_key': USDA_API_KEY,
            'query': query,
            'pageSize': 10,
            'dataType': ['Foundation', 'SR Legacy']
        }
        
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            alimentos = []
            
            for food in data.get('foods', []):
                nutrientes_basicos = {}
                if 'foodNutrients' in food:
                    for nutrient in food['foodNutrients']:
                        nutrient_name = nutrient.get('nutrientName', '').lower()
                        amount = nutrient.get('value', 0)
                        
                        if 'energy' in nutrient_name or 'calories' in nutrient_name:
                            nutrientes_basicos['calorias'] = amount
                        elif 'protein' in nutrient_name:
                            nutrientes_basicos['proteinas'] = amount
                        elif 'fat' in nutrient_name or 'lipid' in nutrient_name:
                            nutrientes_basicos['grasas'] = amount
                        elif 'carbohydrate' in nutrient_name:
                            nutrientes_basicos['carbohidratos'] = amount
                
                alimento_info = {
                    'fdc_id': food.get('fdcId'),
                    'descripcion': food.get('description', 'Sin descripción'),
                    'marca': food.get('brandOwner', ''),
                    'categoria': food.get('foodCategory', 'General'),
                    'nutrientes_basicos': nutrientes_basicos
                }
                alimentos.append(alimento_info)
            
            return alimentos
        else:
            return []
    
    except Exception as e:
        print(f"Error buscando alimentos USDA: {e}")  
        return []

def obtener_nutrientes_usda_simple(fdc_id):
    try:
        url = f"{USDA_API_URL}/food/{fdc_id}"
        params = {'api_key': USDA_API_KEY}
                
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            nutrientes = {
                'calorias': 0,
                'proteinas': 0,
                'carbohidratos': 0,
                'grasas': 0
            }
            
            nutrient_map = {
                1008: 'calorias', 
                1003: 'proteinas',  
                1005: 'carbohidratos',  
                1004: 'grasas'  
            }
            
            for nutrient in data.get('foodNutrients', []):
                nutrient_id = nutrient.get('nutrient', {}).get('id')
                amount = nutrient.get('amount', 0)
                
                if nutrient_id in nutrient_map:
                    nutrientes[nutrient_map[nutrient_id]] = amount
                        
            return {
                'nombre': data.get('description', 'Alimento'),
                'nutrientes': nutrientes,
                'fdc_id': fdc_id
            }
        else:
            return None
    
    except Exception as e:
        print(f"Error en obtener_nutrientes_usda_simple: {e}")  
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
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    
    cursor.execute('''
        SELECT nombre, apellido, email, fecha_nacimiento, genero, peso, altura, 
            actividad_fisica, dieta_especifica, experiencia_cocina 
        FROM usuarios 
        WHERE id = %s
    ''', (user_id,))
    
    usuario = cursor.fetchone()
    
    cursor.execute('SELECT objetivo FROM usuario_objetivos WHERE usuario_id = %s', (user_id,))
    objetivos = cursor.fetchall()
    
    cursor.execute('SELECT alergia FROM usuario_alergias WHERE usuario_id = %s', (user_id,))
    alergias = cursor.fetchall()
    
    cursor.execute('SELECT intolerancia FROM usuario_intolerancias WHERE usuario_id = %s', (user_id,))
    intolerancias = cursor.fetchall()
    
    edad = None
    if usuario and usuario[3]: 
        from datetime import datetime
        fecha_nacimiento = usuario[3]
        hoy = datetime.now()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    
    datos_usuario = {}
    if usuario:
        datos_usuario = {
            'nombre': f"{usuario[0]} {usuario[1]}" if usuario[0] and usuario[1] else '',
            'nombre_solo': usuario[0] if usuario[0] else '',
            'apellido': usuario[1] if usuario[1] else '',
            'email': usuario[2] if usuario[2] else '',
            'fecha_nacimiento': usuario[3] if usuario[3] else '',
            'edad': edad,
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
        try:
            nombre = request.form.get('nombre')
            edad_form = request.form.get('edad')
            sexo = request.form.get('sexo')
            peso = request.form.get('peso')
            altura = request.form.get('altura')
            objetivo = request.form.get('objetivo')
            
            cursor.execute('''
                UPDATE usuarios 
                SET nombre = %s, genero = %s, peso = %s, altura = %s
                WHERE id = %s
            ''', (nombre, sexo, peso, altura, user_id))
            
            cursor.execute('DELETE FROM usuario_objetivos WHERE usuario_id = %s', (user_id,))
            if objetivo:
                cursor.execute('INSERT INTO usuario_objetivos (usuario_id, objetivo) VALUES (%s, %s)', 
                            (user_id, objetivo))
            
            mysql.connection.commit()
            
            session['user_nombre'] = nombre
            
            datos_usuario.update({
                'nombre': nombre,
                'edad': edad_form,
                'sexo': sexo,
                'peso': peso,
                'altura': altura,
                'objetivo': objetivo
            })
            
            flash('Perfil actualizado correctamente', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el perfil: {str(e)}', 'danger')
    
    return render_template('perfil.html', datos=datos_usuario)

@app.route('/recomendaciones')
def recomendaciones():    
    metas_diarias = {
        'calorias': 2200,
        'proteinas': 75,
        'carbohidratos': 275,
        'grasas': 65,
        'agua': 2.5,
        'vitamina_c': 90,
        'hierro': 18,
        'calcio': 1000,
        'vitamina_d': 600
    }
    
    return render_template('recomendaciones.html',metas_diarias=metas_diarias,)

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

@app.route('/recetas', methods=['GET', 'POST'])
def recetas():    
    categoria = request.args.get('categoria', 'todas')
    tiempo = request.args.get('tiempo', 'todos')
    dificultad = request.args.get('dificultad', 'todas')
    tipo_dieta = request.args.get('tipo_dieta', 'todas')
    calorias = request.args.get('calorias', 'todas')
    
    recetas_filtradas = RECETAS
    
    if categoria != 'todas':
        recetas_filtradas = [r for r in recetas_filtradas if r['categoria'].lower() == categoria.lower()]
    
    if tiempo != 'todos':
        if tiempo == 'rapido':
            recetas_filtradas = [r for r in recetas_filtradas if r['tiempo'] <= 15]
        elif tiempo == 'medio':
            recetas_filtradas = [r for r in recetas_filtradas if 15 < r['tiempo'] <= 30]
        elif tiempo == 'largo':
            recetas_filtradas = [r for r in recetas_filtradas if r['tiempo'] > 30]
    
    if dificultad != 'todas':
        recetas_filtradas = [r for r in recetas_filtradas if r['dificultad'].lower() == dificultad.lower()]
    
    if tipo_dieta != 'todas':
        recetas_filtradas = [r for r in recetas_filtradas if r['tipo_dieta'].lower() == tipo_dieta.lower()]
    
    if calorias != 'todas':
        if calorias == 'bajas':
            recetas_filtradas = [r for r in recetas_filtradas if r['calorias'] <= 200]
        elif calorias == 'medias':
            recetas_filtradas = [r for r in recetas_filtradas if 200 < r['calorias'] <= 400]
        elif calorias == 'altas':
            recetas_filtradas = [r for r in recetas_filtradas if r['calorias'] > 400]
    
    return render_template('recetas.html', 
                        recetas=recetas_filtradas,
                        filtros_actuales={
                            'categoria': categoria,
                            'tiempo': tiempo,
                            'dificultad': dificultad,
                            'tipo_dieta': tipo_dieta,
                            'calorias': calorias
                        })

@app.route('/receta/<int:receta_id>')
def receta_detalle(receta_id):    
    receta = next((r for r in RECETAS if r['id'] == receta_id), None)
    if not receta:
        flash('Receta no encontrada', 'danger')
        return redirect(url_for('recetas'))
    
    return render_template('receta_detalle.html', receta=receta)

@app.route('/analizador_de_recetas', methods=['GET', 'POST'])
def analizador_de_recetas():    
    resultado_analisis = None
    
    if request.method == 'POST':
        try:
            nombre_receta = request.form.get('nombre_receta', 'Receta sin nombre')
            texto_ingredientes = request.form.get('ingredientes', '')
            porciones = int(request.form.get('porciones', 1))
            
            lineas_ingredientes = [line.strip() for line in texto_ingredientes.split('\n') if line.strip()]
            ingredientes = []
            
            for linea in lineas_ingredientes:
                ingrediente_parseado = parsear_ingrediente(linea)
                if ingrediente_parseado:
                    ingredientes.append(ingrediente_parseado)
            
            if ingredientes:
                analisis = analizar_receta_api(ingredientes)
                
                if analisis:
                    factor_porcion = 1 / porciones
                    
                    resultado_analisis = {
                        'nombre_receta': nombre_receta,
                        'porciones': porciones,
                        'nutrientes_totales': {
                            'calorias': analisis['nutrientes_totales']['calorias'],
                            'proteinas': analisis['nutrientes_totales']['proteinas'],
                            'grasas': analisis['nutrientes_totales']['grasas'],
                            'carbohidratos': analisis['nutrientes_totales']['carbohidratos']
                        },
                        'nutrientes_porcion': {
                            'calorias': analisis['nutrientes_totales']['calorias'] / factor_porcion,
                            'proteinas': analisis['nutrientes_totales']['proteinas'] / factor_porcion,
                            'grasas': analisis['nutrientes_totales']['grasas'] / factor_porcion,
                            'carbohidratos': analisis['nutrientes_totales']['carbohidratos'] / factor_porcion
                        },
                        'ingredientes_analizados': analisis['ingredientes_analizados'],
                        'estadisticas': {
                            'total_ingredientes': analisis['total_ingredientes'],
                            'encontrados': analisis['total_encontrados'],
                            'no_encontrados': analisis['total_no_encontrados']
                        }
                    }
                    flash('Receta analizada exitosamente', 'success')                 
        except Exception as e:
            flash(f'Error al procesar la receta: {str(e)}', 'danger')
    
    return render_template('analizador_de_recetas.html', 
                        resultado_analisis=resultado_analisis)
    
@app.route('/habitos')
def habitos():
    return render_template('habitos.html')

@app.route('/buscar_alimentos', methods=['POST'])
def buscar_alimentos():
    query = request.json.get('query', '')
    if not query or len(query) < 2:
        return jsonify({'error': 'La búsqueda debe tener al menos 2 caracteres'}), 400
    
    try:
        resultados = buscar_alimentos_usda_simple(query)
        return jsonify({'alimentos': resultados})
    
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return jsonify({'error': 'Error al buscar alimentos'}), 500

@app.route('/obtener_nutrientes/<int:fdc_id>', methods=['GET'])
def obtener_nutrientes(fdc_id):
    try:
        alimento_data = obtener_nutrientes_usda_simple(fdc_id)
        if not alimento_data:
            return jsonify({'error': 'No se pudo obtener información del alimento'}), 404
        
        return jsonify({
            'nombre': alimento_data['nombre'],
            'nutrientes': alimento_data['nutrientes']
        })
    
    except Exception as e:
        print(f"Error al obtener nutrientes: {e}")
        return jsonify({'error': 'Error al obtener información nutricional'}), 500

@app.route('/alimentos', methods=['GET', 'POST'])
def alimentos():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT id, alimento, cantidad, unidad, calorias, proteinas, carbohidratos, grasas, fecha_registro
        FROM alimentos_registrados 
        WHERE usuario_id = %s AND DATE(fecha_registro) = CURDATE()
        ORDER BY fecha_registro DESC
    ''', (session['user_id'],))
    
    alimentos_registrados = cursor.fetchall()
    
    alimentos = []
    for alimento in alimentos_registrados:
        alimentos.append({
            'id': alimento[0],
            'alimento': alimento[1],
            'cantidad': alimento[2],
            'unidad': alimento[3],
            'calorias': alimento[4],
            'proteinas': alimento[5] or 0,
            'carbohidratos': alimento[6] or 0,
            'grasas': alimento[7] or 0
        })
    
    resultados_busqueda = None
    query_busqueda = None
    alimento_seleccionado = None
    
    if request.method == 'POST':
        if 'buscar_usda' in request.form:
            query = request.form.get('buscar_query', '').strip()
            query_busqueda = query
            
            if len(query) < 2:
                flash('Ingresa al menos 2 caracteres para buscar', 'warning')
            else:
                resultados_busqueda = buscar_alimentos_usda_simple(query)
                if not resultados_busqueda:
                    flash('No se encontraron alimentos con esa búsqueda', 'warning')
        
        elif 'seleccionar_alimento' in request.form:
            fdc_id = request.form.get('fdc_id')
            alimento_seleccionado = obtener_nutrientes_usda_simple(fdc_id)
            if alimento_seleccionado:
                flash('Información nutricional cargada exitosamente', 'success')
            else:
                flash('Error al cargar información nutricional', 'danger')
        
        elif 'registrar_alimento' in request.form:
            try:
                alimento_nombre = request.form.get('alimento')
                cantidad = float(request.form.get('cantidad'))
                unidad = request.form.get('unidad')
                calorias = float(request.form.get('calorias'))
                proteinas = float(request.form.get('proteinas') or 0)
                carbohidratos = float(request.form.get('carbohidratos') or 0)
                grasas = float(request.form.get('grasas') or 0)
                
                cursor.execute('''
                    INSERT INTO alimentos_registrados 
                    (usuario_id, alimento, cantidad, unidad, calorias, proteinas, carbohidratos, grasas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (session['user_id'], alimento_nombre, cantidad, unidad, calorias, proteinas, carbohidratos, grasas))
                
                mysql.connection.commit()
                flash('Alimento registrado exitosamente', 'success')
                return redirect(url_for('alimentos'))
                
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al registrar alimento: {str(e)}', 'danger')
    
    return render_template('alimentos.html', 
                        alimentos=alimentos,
                        resultados_busqueda=resultados_busqueda,
                        query_busqueda=query_busqueda,
                        alimento_seleccionado=alimento_seleccionado)

@app.route('/eliminar_alimento/<int:alimento_id>', methods=['POST'])
def eliminar_alimento(alimento_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM alimentos_registrados WHERE id = %s AND usuario_id = %s', 
                    (alimento_id, session['user_id']))
        mysql.connection.commit()
        flash('Alimento eliminado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar alimento: {str(e)}', 'danger')
    
    return redirect(url_for('alimentos'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email_login')
        password = request.form.get('password_login')
        
        if not email or not password:
            return render_template('login.html', error='Por favor completa todos los campos')
        
        usuario = verificar_usuario(email, password)
        
        if usuario:
            session['user_id'] = usuario['id']
            session['user_email'] = usuario['email']
            session['user_nombre'] = usuario['nombre']
            flash(f'¡Bienvenido/a de nuevo, {usuario["nombre"]}!', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales incorrectas. Intenta nuevamente.')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            email = request.form.get('contacto')
            password = request.form.get('contrasena')
            confirm_password = request.form.get('confirmaContraseña')
            
            if not all([nombre, apellido, email, password, confirm_password]):
                return render_template('registro.html', error='Por favor completa todos los campos obligatorios')
            
            if password != confirm_password:
                return render_template('registro.html', error='Las contraseñas no coinciden')
            
            if len(password) < 6:
                return render_template('registro.html', error='La contraseña debe tener al menos 6 caracteres')
            
            if email_existe(email):
                return render_template('registro.html', error='Este correo electrónico ya está registrado')
            
            dia = request.form.get('dia')
            mes = request.form.get('mes')
            anio = request.form.get('anio')
            fecha_nacimiento = None
            
            if dia and mes and anio:
                try:
                    fecha_nacimiento = f"{anio}-{mes}-{dia}"
                except ValueError:
                    fecha_nacimiento = None
            
            genero = request.form.get('genero')
            peso = request.form.get('peso')
            altura = request.form.get('altura')
            actividad_fisica = request.form.get('actividad_fisica')
            dieta_especifica = request.form.get('dieta_especifica')
            experiencia_cocina = request.form.get('experiencia_cocina')
            
            objetivos = request.form.getlist('objetivos')
            alergias = request.form.getlist('alergias')
            intolerancias = request.form.getlist('intolerancias')
            
            objetivos = [obj for obj in objetivos if obj]
            alergias = [alg for alg in alergias if alg]
            intolerancias = [intol for intol in intolerancias if intol]
            
            try:
                peso = float(peso) if peso else None
                altura = float(altura) if altura else None
            except (ValueError, TypeError):
                peso = None
                altura = None
            
            exito, mensaje = registrar_usuario_db(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password,
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
            
            if exito:
                usuario = verificar_usuario(email, password)
                if usuario:
                    session['user_id'] = usuario['id']
                    session['user_email'] = usuario['email']
                    session['user_nombre'] = usuario['nombre']
                    flash(f'¡Cuenta creada exitosamente! Bienvenido/a, {usuario["nombre"]}', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Cuenta creada exitosamente. Por favor inicia sesión.', 'success')
                    return redirect(url_for('login'))
            else:
                return render_template('registro.html', error=mensaje)
                
        except Exception as e:
            print(f"Error en registro: {e}")
            return render_template('registro.html', error='Ocurrió un error durante el registro. Intenta nuevamente.')
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_nombre', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))

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
    factores_actividad = {
        'sedentario': {'factor': 1.2, 'descripcion': 'Sedentario'},
        'ligero': {'factor': 1.375, 'descripcion': 'Ligero'},
        'moderado': {'factor': 1.55, 'descripcion': 'Moderado'},
        'intenso': {'factor': 1.725, 'descripcion': 'Intenso'},
        'muy_intenso': {'factor': 1.9, 'descripcion': 'Muy intenso'}
    }
    
    if request.method == 'POST':
        try:
            tmb = float(request.form.get('tmb'))
            actividad = request.form.get('actividad')
            
            if actividad in factores_actividad:
                factor = factores_actividad[actividad]['factor']
                descripcion = factores_actividad[actividad]['descripcion']
                gct = tmb * factor
            else:
                factor = 1.2
                descripcion = 'Sedentario'
                gct = tmb * factor
                actividad = 'sedentario'
            
            if gct < 1500:
                recomendacion = "Tu gasto calórico es bajo. Considera aumentar tu actividad física gradualmente."
            elif 1500 <= gct < 2500:
                recomendacion = "Gasto calórico moderado. Ideal para mantener un estilo de vida equilibrado."
            else:
                recomendacion = "Gasto calórico alto. Asegúrate de consumir suficientes nutrientes para tu nivel de actividad."
            
            niveles_comparacion = {}
            for key, valores in factores_actividad.items():
                niveles_comparacion[key] = {
                    'descripcion': valores['descripcion'],
                    'factor': valores['factor'],
                    'gct': tmb * valores['factor']
                }
            
            return render_template('gct.html', 
                                gct_resultado=f"{gct:.0f}",
                                tmb=tmb,
                                factor_actividad=factor,
                                descripcion_actividad=descripcion,
                                actividad_seleccionada=actividad,
                                recomendacion=recomendacion,
                                niveles_comparacion=niveles_comparacion)
            
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
                recomendacion = f"Tu peso ideal  ({peso_ideal_formula:.1f} kg) está por debajo del rango saludable mínimo ({peso_minimo_imc:.1f} kg). Considera consultar con un nutricionista."
            elif peso_ideal_formula > peso_maximo_imc:
                recomendacion = f"Tu peso ideal  ({peso_ideal_formula:.1f} kg) está por encima del rango saludable máximo ({peso_maximo_imc:.1f} kg). Un profesional puede ayudarte a establecer metas realistas."
            else:
                recomendacion = f"¡Excelente! Tu peso ideal  ({peso_ideal_formula:.1f} kg) está dentro del rango saludable recomendado ({peso_minimo_imc:.1f} - {peso_maximo_imc:.1f} kg)."
            
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