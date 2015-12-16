GUEST_LOCAL = 'Гость'
__author__ = 'Alexey Maksimov (FroHenK)'
import os
import hashlib
import json
from datetime import datetime, timedelta

from mysqlclient import curs, cnx, get_all_grades, get_all_subjects, get_homeworks, is_valid_admin, add_homework_db, \
    create_day_element_db, get_day_db, get_day_db_id, get_homework_id, delete_day_db_id, delete_homework_id, \
    get_all_day_db, get_all_homeworks, add_subject_db, delete_subject_id, add_grade_db

from flask import Flask, request, session, flash, url_for, redirect, \
    render_template, abort, send_from_directory

app = Flask(__name__)

app.config.from_pyfile('flaskapp.cfg')


# TODO refactor 'class' to 'grade'

@app.context_processor
def template_imports():  # put things into table for template rendering
    res = {}

    res["grades_array"] = get_all_grades()
    res["subjects_array"] = get_all_subjects()
    res["timedelta"] = timedelta
    return res


@app.route('/set_grade/', methods=['POST'])  # set user's grade
def set_grade():
    session['grade_selected_id'] = int(request.form['grade_id'])
    return redirect('/')


@app.route('/logout/')
def logout():
    if not session['is_admin']:
        return not_enough_permissions()
    session['is_admin'] = False
    session['username'] = GUEST_LOCAL
    return redirect(url_for('index'))


@app.route('/classes/')
def classes_admin():
    return render_template('classes_admin.html', classes_admin_active=True)


@app.route('/add_grade/', methods=['POST'])
def add_grade():
    add_grade_db(request.form['title'])
    return redirect(url_for('classes_admin'))


@app.route('/admin/')
def admin_panel():
    return render_template('admin_panel.html', admin_panel_active=True)


@app.route("/create_day_element/<string:usr_date>/", methods=['POST'])
def create_day_element(usr_date):
    if not session['is_admin']:
        return not_enough_permissions()
    time_str = request.form['usr_time']
    subject_id = int(request.form['subject_id'])
    if len(time_str) == 0:
        time_str = '00:00'
    current_datetime = datetime.strptime(usr_date + ' ' + time_str, '%Y-%m-%d %H:%M')
    create_day_element_db(session['grade_selected_id'], current_datetime, subject_id)
    return redirect('/get_day/' + usr_date + "/")


@app.before_request
def b_request():
    # lazy initializations
    if session.get('grade_selected_id') is None:  # if none grade is selected
        session['grade_selected_id'] = 105  # FIXME bad code
    if session.get('is_admin') is None:
        session['is_admin'] = False
    if session.get('username') is None:
        session['username'] = GUEST_LOCAL


@app.route("/get_day/<string:usr_date>/", methods=['GET'])
def get_homework(usr_date):
    current_datetime = datetime.strptime(usr_date, '%Y-%m-%d')

    day_db = get_day_db(session['grade_selected_id'], current_datetime)
    return render_template('schedule.html', day_elements_array=day_db, schedule_active=True,
                           current_datetime=current_datetime)


@app.route("/delete_day_element/<int:id>")
def delete_day_elem(id):
    if not session['is_admin']:
        return not_enough_permissions()
    day_element = get_day_db_id(id)
    delete_day_db_id(id)
    return redirect('/get_day/' + day_element.date.strftime('%Y-%m-%d'))


@app.route("/delete_homework/<int:id>")
def delete_homework(id):
    if not session['is_admin']:
        return not_enough_permissions()
    day_element = get_homework_id(id)
    delete_homework_id(id)
    return redirect('/subjects/' + str(day_element.subject_id))


@app.route('/login/', methods=['POST'])
def admin_login():
    s = str(hashlib.md5(str(request.form['password']).encode('utf8')).hexdigest())
    if not is_valid_admin(str(request.form['username']), s):
        return not_enough_permissions()  # TODO make special login error page
    session['is_admin'] = True
    session['username'] = str(request.form['username'])
    return redirect('/')


@app.route('/')
def index():
    current_datetime = datetime.now()
    return get_homework(current_datetime.strftime("%Y-%m-%d"))


@app.route('/subjects/')
def subjects_page():
    return render_template('subjects.html', subjects_active=True)


@app.route('/add_homework/<int:grade_id>/<int:subject_id>/', methods=["POST"])
def on_add_homework(grade_id, subject_id):
    if not session['is_admin']:
        return not_enough_permissions()

    add_homework_db(grade_id, subject_id, str(request.form['data']))

    return redirect('/subjects/%s' % subject_id)


@app.route('/add_subject/', methods=["POST"])
def add_subject():
    if not session['is_admin']:
        return not_enough_permissions()

    add_subject_db(str(request.form['title']))

    return redirect('/subjects/')


# displays not enough permissions error page
def not_enough_permissions():
    return render_template('not_enough_permissions.html')


@app.route('/delete_subject/<int:subject_id>/')
def remove_subject(subject_id):
    if not session['is_admin']:
        return not_enough_permissions()

    delete_subject_id(subject_id)
    return redirect(url_for('subjects_page'))


@app.route('/subjects/<int:subject_id>/')
def draw_subject(subject_id):
    return render_template('homeworks.html', subjects_active=True, subject_id=subject_id,
                           homeworks_array=get_homeworks(session['grade_selected_id'], subject_id))


@app.route('/project/')
def about_project():
    return render_template('project.html', project_active=True)


@app.route('/<path:resource>')
def serve_static_resource(resource):
    return send_from_directory('static/', resource)


class JCalendar:  # how java's calendar looks in JSON
    def __init__(self, year, month, dayOfMonth, hourOfDay, minute, second):
        self.year = year
        self.month = month - 1
        self.dayOfMonth = dayOfMonth
        self.hourOfDay = hourOfDay
        self.minute = minute
        self.second = second


def encode_b(obj):  # JSON encode function
    if isinstance(obj, datetime):
        serial = JCalendar(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)  # we need Java like calendar

        return serial.__dict__
    return obj.__dict__


@app.route("/get_json/")  # API for Java JSON
def json_api():
    json_data = {}
    json_data['grades'] = get_all_grades()
    json_data['subjects'] = get_all_subjects()
    json_data['homeworks'] = get_all_homeworks()
    json_data['day_elements'] = get_all_day_db()

    return json.dumps(json_data, default=encode_b)


if __name__ == '__main__':
    app.run()
