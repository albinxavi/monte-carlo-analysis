from flask import render_template
from services import db_services


def render_initialisation_page():
    return render_template('initialise.htm')


def render_result_page(data):
    T = data.get('audit_result').get('T')
    avg_95 = data.get('audit_result').get('avg_95')
    avg_99 = data.get('audit_result').get('avg_99')
    signal_key = 'buy_results' if T == 'Buy' else 'sell_results'

    chart = [[T] + result[:-1] + [avg_95, avg_99] for result in data[signal_key]]
    print(chart)
    return render_template('results.htm', table=data[signal_key], chart=chart)


def render_audit_page():
    query = "SELECT * FROM AUDIT LIMIT 50"
    result = db_services.execute_query_and_get_data(query)
    print(result[0])
    return render_template('audit.htm', data=result)
