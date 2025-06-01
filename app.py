from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # return ("helloWorld")
    return render_template("index.html")

@app.route('/base')
def base():
    # return ("helloWorld")
    return render_template("base.html")

@app.route('/auction')
def auction():
    return render_template("auction.html")

if __name__ == '__main__':
    app.run(debug=True)
