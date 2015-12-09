import os
import hashlib
import json
from datetime import datetime, timedelta

from mysqlclient import curs, cnx, get_grades, get_subjects, get_homeworks, is_valid_admin, add_homework_db, \
    create_day_element_db, get_day_db, get_day_db_id, get_homework_id, delete_day_db_id, delete_homework_id,get_all_day_db,get_all_homeworks
from flask import Flask, request, session, flash, url_for, redirect, \
    render_template, abort, send_from_directory

app = Flask(__name__)

app.config.from_pyfile('flaskapp.cfg')


def template_imports():
    res = {}

    res["grades_array"] = get_grades()

    res["subjects_array"] = get_subjects()
    res["timedelta"] = timedelta
    return res


@app.route('/set_grade/', methods=['POST'])
def set_grade():
    session['grade_selected_id'] = int(request.form['grade_id'])
    return redirect('/')


@app.route("/create_day_element/<string:usr_date>/", methods=['POST'])
def create_day_element(usr_date):
    time_str = request.form['usr_time']
    subject_id = int(request.form['subject_id'])
    if len(time_str) == 0:
        time_str = '00:00'
    current_datetime = datetime.strptime(usr_date + ' ' + time_str, '%Y-%m-%d %H:%M')
    create_day_element_db(session['grade_selected_id'], current_datetime, subject_id)
    return redirect('/get_day/' + usr_date + "/")


@app.before_first_request
def b_request():
    session['grade_selected_id'] = 105  # FIXME  bad code


@app.route("/get_day/<string:usr_date>/", methods=['GET'])
def get_homework(usr_date):
    current_datetime = datetime.strptime(usr_date, '%Y-%m-%d')

    day_db = get_day_db(session['grade_selected_id'], current_datetime)
    return render_template('schedule.html', day_elements_array=day_db, schedule_active=True,
                           current_datetime=current_datetime,
                           **template_imports())


@app.route("/delete_day_element/<int:id>")
def delete_day_elem(id):
    day_element = get_day_db_id(id)
    delete_day_db_id(id)
    return redirect('/get_day/' + day_element.date.strftime('%Y-%m-%d'))


@app.route("/delete_homework/<int:id>")
def delete_homework(id):
    day_element = get_homework_id(id)
    delete_homework_id(id)
    return redirect('/subjects/' + str(day_element.subject_id))


@app.route('/login/', methods=['POST'])
def admin_login():
    s = str(hashlib.md5(str(request.form['password']).encode('utf8')).hexdigest())
    if is_valid_admin(str(request.form['username']), s):
        session['is_admin'] = True
    return redirect('/')


@app.route('/')
def index():
    # TODO make it
    current_datetime = datetime.now()

    return get_homework(current_datetime.strftime("%Y-%m-%d"))


@app.route('/subjects/')
def subjects_page():
    return render_template('subjects.html', subjects_active=True, **template_imports())


@app.route('/add_homework/<int:grade_id>/<int:subject_id>/', methods=["POST"])
def on_add_homework(grade_id, subject_id):
    add_homework_db(grade_id, subject_id, str(request.form['data']))

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


def encode_b(obj):
    if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
    return obj.__dict__


@app.route("/get_json/")
def json_api():
    json_data = {}
    json_data['grades'] = get_grades()
    json_data['subjects'] = get_subjects()
    json_data['homeworks'] = get_all_homeworks()
    json_data['day_elements'] = get_all_day_db()


    return json.dumps(json_data, default=encode_b)


if __name__ == '__main__':
    app.run()
