import os
import hashlib
from datetime import datetime
from mysqlclient import curs, cnx, get_grades, get_subjects, get_homeworks, is_valid_admin, add_homework_db
from flask import Flask, request, session, flash, url_for, redirect, \
    render_template, abort, send_from_directory

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')


def template_imports():
    res = {}
    res["grades_array"] = get_grades()
    res["subjects_array"] = get_subjects()
    return res


@app.route('/set_grade/', methods=['POST'])
def set_grade():
    session['grade_selected_id'] = int(request.form['grade_id'])
    return redirect('/')


@app.route('/login/', methods=['POST'])
def admin_login():
    s = str(hashlib.md5(str(request.form['password']).encode('utf8')).hexdigest())
    if is_valid_admin(str(request.form['username']), s):
        session['is_admin'] = True
    return redirect('/')


@app.route('/')
def index():
    return render_template('schedule.html', schedule_active=True, **template_imports())


@app.route('/subjects/')
def subjects_page():
    return render_template('subjects.html', subjects_active=True, **template_imports())


@app.route('/add_homework/<int:grade_id>/<int:subject_id>/', methods=["POST"])
def on_add_homework(grade_id, subject_id):
    add_homework_db(grade_id,subject_id,str(request.form['data']))

    return redirect('/subjects/%s' % subject_id)


@app.route('/subjects/<int:subject_id>/')
def draw_subject(subject_id):
    return render_template('homeworks.html', subjects_active=True, subject_id=subject_id,
                           homeworks_array=get_homeworks(session['grade_selected_id'], subject_id),
                           **template_imports())


@app.route('/project/')
def about_project():
    return render_template('project.html', project_active=True, **template_imports())


@app.route('/admins')
def get_admins():
    res = ""
    curs.execute("SELECT * FROM admins")

    for (id, username, password) in curs:
        res += "%s\n" % username.decode("utf8")
    return res


@app.route('/<path:resource>')
def serve_static_resource(resource):
    return send_from_directory('static/', resource)


if __name__ == '__main__':
    app.run()
