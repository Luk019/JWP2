from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Witaj w mojej aplikacji Flask!</h1>
    <a href="/about"><button>O mnie</button></a>
    <a href="/contact"><button>Kontakt</button></a>
    '''

@app.route('/about')
def about():
    return "Zaprogramowano przez [Twoje Imię]."

@app.route('/contact')
def contact():
    return "Email: kontakt@example.com."

if __name__ == '__main__':
    app.run(debug=True)
