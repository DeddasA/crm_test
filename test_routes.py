from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # This is the home page template

@app.route('/route_1')
def route_1():
    return render_template('route_1.html')  # This is the another route template

if __name__ == '__main__':
    app.run(debug=True)
