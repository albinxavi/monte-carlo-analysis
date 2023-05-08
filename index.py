import os
import logging
from flask import Flask, request, redirect
from handlers import page_handler
from handlers import service_handler
# from services import lambda
# from services import *

from flask import Flask

app = Flask(__name__)


@app.route('/health_check')
def health_check():
    return {"status": "healthy"}


@app.route('/initialise')
def get_initialisation_page():

    return page_handler.render_initialisation_page()


@app.route('/warm_up')
def warm_up_lambda():

    return service_handler.warm_up_lambda()


@app.route('/provision_ec2')
def provision_ec2():
    args = request.args.to_dict()
    return service_handler.provision_ec2(args.get('R'))


@app.route('/input')
def get_input_page():
    args = request.args.to_dict()

    return page_handler.render_input_page(args)


@app.post('/simulate')
def simulate():
    args = request.get_json()
    print(args)

    return service_handler.simulate(args)


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
    app.run(host='127.0.0.1', port=8080, debug=True)
