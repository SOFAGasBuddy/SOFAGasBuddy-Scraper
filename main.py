import os
from flask import Flask, jsonify
from tabulate import tabulate
import waitress
from flask_apscheduler import APScheduler

from helper_stuff import print_and_log, update_data

app = Flask("ESSOScaper")

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

SSN = os.environ['SSN'].strip("\"").strip("-")
VRN = os.environ['VRN'].strip("\"")

try:
    REFRESH_INTERVAL = int(os.environ['REFRESH_INTERVAL'].strip("\""))
except KeyError:
    REFRESH_INTERVAL = 3600

bal, vehicle_list, health = update_data(SSN, VRN)


@scheduler.task('refresh', id='refresh_data', seconds=REFRESH_INTERVAL, misfire_grace_time=900)
def refresh_data():
    with scheduler.app.app_context():
        bal, vehicle_list, health = update_data(SSN, VRN)
        print_and_log(f"Refreshed data, health is: {health}")

@app.route('/', methods=['GET'])
def active_only():
    """returns only the active ESSO cards, in JSON"""
    result = {"balance": bal}
    for i in range(0, len(vehicle_list)):
        if vehicle_list[i].status != "Active":
            continue
        result[str(i)] = {'vrn': vehicle_list[i].vrn,
                          'type': vehicle_list[i].veh_type,
                          'status': vehicle_list[i].status,
                          'limit': vehicle_list[i].limit,
                          'available': vehicle_list[i].available,
                          'exp_date': vehicle_list[i].exp_date}
    return jsonify(result)

@app.route('/all', methods=['GET'])
def all_vehicles():
    """Returns all vehicles, is JSON"""
    result = {"balance": bal}
    for i in range(0, len(vehicle_list)):
        result[str(i)] = {'vrn': vehicle_list[i].vrn,
                          'type': vehicle_list[i].veh_type,
                          'status': vehicle_list[i].status,
                          'limit': vehicle_list[i].limit,
                          'available': vehicle_list[i].available,
                          'exp_date': vehicle_list[i].exp_date}
    return jsonify(result)

@app.route('/html', methods=["GET"])
def simple_table():
    """Very simple HTML table with only the active cards"""
    table = [['VRN', 'Type', 'Status', 'Limit', 'Available', 'Exp Date']]
    for i in vehicle_list:
        if i.status != "Active":
            continue
        tmp_tbl = [i.vrn, i.veh_type, i.status, (i.limit + "L"), i.available + "L", i.exp_date]
        table.append(tmp_tbl)
    result = f"Balance: {bal}<br><br>"
    result += tabulate(table, tablefmt='html', headers="firstrow")
    return result

@app.route('/html/all', methods=["GET"])
def simple_table_all():
    """Same as /html, but with all cards ever"""
    table = [['VRN', 'Type', 'Status', 'Limit', 'Available', 'Exp Date']]
    for i in vehicle_list:
        tmp_tbl = [i.vrn, i.veh_type, i.status, (i.limit + "L"), i.available + "L", i.exp_date]
        table.append(tmp_tbl)
    result = f"Balance: {bal}<br><br>"
    result += tabulate(table, tablefmt='html', headers="firstrow")
    return result

@app.route('/balance', methods=["GET"])
def balance_only():
    """Just the balance"""
    return {"balance": bal}

@app.route('/health')
def health_status():
    """Returns a string of either 1 or 0, to be used in docker healthcheck"""
    return str(health)

waitress.serve(app, host="0.0.0.0", port=9999)
