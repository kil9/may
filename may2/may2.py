from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    return 'main here'


@app.route('/pick')
def pick():
    print(result)
    return 'ok'


if __name__ == '__main__':
    app.run(port=21000, debug=True)
