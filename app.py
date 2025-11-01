from flask import Flask, render_template, redirect, url_for,session,request

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
