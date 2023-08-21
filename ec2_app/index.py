import logging
from flask import Flask, request

from analyse import analyse

app = Flask(__name__)


@app.route('/')
def health_check():
    return {"status": True}


@app.post('/analyse')
def run_simulation():
    data = request.get_json()
    D = int(data.get('d'))
    H = int(data.get('h'))
    P = int(data.get('p'))
    T = data.get('t')
    return analyse(D, H, T, P)


@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
    logging.exception('ERROR!')
    return """ 
    An  error occurred: <pre>{}</pre> 
    """.format(e), 500


if __name__ == '__main__':
    # Entry point for running on the local machine
    # On GAE, endpoints (e.g. /) would be called.
    # Called as: gunicorn -b :$PORT index:app,
    # host is localhost; port is 8080; this file is index (.py)
    app.run(host='0.0.0.0', port=8080, debug=True)
