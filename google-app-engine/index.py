from flask import Flask
from handlers import service_handler
from flask import Flask, request
import logging
import os
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './cred'


app = Flask(__name__)


@app.get('/health_check')
def health_check():
    return {"status": "healthy"}


@app.post('/warmup')
def warm_up_lambda():
    data = request.get_json()
    return service_handler.warm_up(data)


@app.get('/resources_ready')
def check_resources_ready():
    return service_handler.check_resources_ready()


@app.get('/get_warmup_cost')
def get_warmup_cost():
    return service_handler.get_warmup_cost()


@app.get('/get_endpoints')
def get_endpoints():
    return service_handler.get_endpoints()


@app.post('/analyse')
def analyse():
    args = request.get_json()
    return service_handler.analyse(args)


@app.get('/get_sig_vars9599')
def get_sig_vars9599():
    return service_handler.get_sig_vars9599()


@app.get('/get_avg_vars9599')
def get_avg_vars9599():
    return service_handler.get_avg_vars9599()


@app.get('/get_sig_profit_loss')
def get_sig_profit_loss():
    return service_handler.get_sig_profit_loss()


@app.get('/get_tot_profit_loss')
def get_tot_profit_loss():
    return service_handler.get_tot_profit_loss()


@app.get('/get_chart_url')
def get_chart_url():
    return service_handler.get_chart_url()


@app.get('/get_time_cost')
def get_time_cost():
    return service_handler.get_time_cost()


@app.get('/get_audit')
def get_audit():
    return service_handler.get_audit()


@app.get('/reset')
def reset():
    return service_handler.reset()


@app.get('/terminate')
def terminate():
    return service_handler.terminate()


@app.get('/resources_terminated')
def check_resources_terminated():
    return service_handler.check_resources_terminated()


@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
    logging.exception('ERROR!')
    return """ 
    An  error occurred: <pre>{}</pre> 
    """.format(e), 500


# @app.teardown_appcontext
# def exit(exception):
#     db_services.close_connection(exception)


if __name__ == '__main__':
    # Entry point for running on the local machine
    # On GAE, endpoints (e.g. /) would be called.
    # Called as: gunicorn -b :$PORT index:app,
    # host is localhost; port is 8080; this file is index (.py)
    app.run(host='0.0.0.0', port=3000, debug=True)
