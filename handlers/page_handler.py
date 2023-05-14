from flask import render_template
from services import db_services


def render_initialisation_page():
    return render_template('initialise.htm')


def render_result_page(data):
    T = data.get('audit_result').get('T')
    avg_95 = data.get('audit_result').get('avg_95')
    avg_99 = data.get('audit_result').get('avg_99')
    signal_key = 'buy_results' if T == 'Buy' else 'sell_results'
    for result in data[signal_key]:
        result.extend([avg_95, avg_99])
        result.insert(0, T)
    return render_template('results.htm', data=data[signal_key])


def render_audit_page():
    query = "SELECT * FROM AUDIT LIMIT 50"
    result = db_services.execute_query_and_get_data(query)
    print(result[0])
    return render_template('audit.htm', data=result)
