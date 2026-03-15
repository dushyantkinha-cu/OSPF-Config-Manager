#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect
import getconfig
import ospfconfig
import database
import diffconfig
import migration

app = Flask(__name__)

database.init_db()

@app.route('/')
def index():
    return render_template('index.html', tittle="Home")

@app.route('/get_config')
def get_config():
    files = getconfig.configs()
    return render_template('get_config.html', filenames=files)

@app.route('/ospf_config')
def ospf_config():
    return render_template('ospf_home.html')

@app.route('/ospf_input/<hostname>')
def ospf_input(hostname):
    return render_template('ospf_form.html', hostname=hostname)

@app.route('/ospf_save', methods=['POST'])
def ospf_save():
    data = {
        'hostname': request.form['hostname'],
        'username': request.form['username'],
        'password': request.form['password'],
        'ospf_process': request.form['ospf_process'],
        'ospf_area': request.form['ospf_area'],
        'ospf_area_2': request.form.get('ospf_area_2', ''), 
        'loopback_ip': request.form['loopback_ip']
    }
    database.save_router_data(data)
    return redirect('/ospf_config')

@app.route('/ospf_deploy', methods=['POST'])
def ospf_deploy():
    results = ospfconfig.configure_network()
    return render_template('ospf_results.html', results=results)

@app.route('/diff_config')
def diff_config():
    diffs = diffconfig.get_diffs()
    return render_template('diff_results.html', diffs=diffs)

@app.route('/migration')
def migration_route():
    results = migration.run_migration()
    return render_template('migration_results.html', logs=results)

def main():
    app.debug = True
    app.run(host='0.0.0.0', port=80)

if __name__ == "__main__":
    main()