import os
from datetime import datetime
from mysqlclient import curs,cnx
from flask import Flask, request, flash, url_for, redirect, \
    render_template, abort, send_from_directory

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

@app.route('/')
def index():
    return render_template('schedule.html',schedule_active=True)
@app.route('/subjects/')
def subjects_page():
    return render_template('subjects.html',subjects_active=True)
@app.route('/project/')
def about_project():
    return render_template('project.html',project_active=True)

#

@app.route('/admins')
def get_admins():
    res="";
    curs.execute("SELECT * FROM admins")

    for (id,username,password) in curs:
        res+="%s\n"%username.decode("utf8")
    return res

@app.route('/<path:resource>')
def serve_static_resource(resource):
    return send_from_directory('static/', resource)

if __name__ == '__main__':
    app.run()

