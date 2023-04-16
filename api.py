# ==== Para ejecutar el servidor: python api.py y está en localhost:5000 ====

from flask import Flask

app = Flask(__name__)


@app.route('/hola')
def hola():
    return '¡Hola, mundo!'

if __name__ == '__main__':
    app.run(debug=True)


