import os
import mysql

from mysql.connector import (connection)


class Grade:
    def __init__(self, id, title):
        self.title = title
        self.id = id


class Homework:
    def __init__(self, id, grade_id, subject_id, data):
        self.subject_id = subject_id
        self.grade_id = grade_id
        self.data = data
        self.id = id


class Subject:
    def __init__(self, id, title):
        self.title = title
        self.id = id


MYSQL_HOST = os.environ.get('OPENSHIFT_MYSQL_DB_HOST', '127.0.0.1')
MYSQL_USER = os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME', 'root')
MYSQL_PASSWORD = os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD', '')
MYSQL_PORT = os.environ.get('OPENSHIFT_MYSQL_DB_PORT', 3306)
MYSQL_DB = 'ptl'

cnx = connection.MySQLConnection(user=MYSQL_USER, password=MYSQL_PASSWORD,
                                 host=MYSQL_HOST,
                                 database=MYSQL_DB, charset='utf8')

curs = cnx.cursor(buffered=True)


def get_grades():
    curs.execute('SELECT * FROM grade')
    res = curs.fetchall()

    grades_array = []
    for (id, title) in res:
        grades_array.append(Grade(int(id), str(title.decode("utf8"))))
    return grades_array


def get_homeworks(grade_id2, subject_id2):
    id_ = 'SELECT * FROM homework WHERE grade_id=%s AND subject_id=%s ORDER BY id DESC' % (grade_id2, subject_id2)

    curs.execute(id_)

    res = curs.fetchall()

    homeworks_array = []
    for (id, grade_id, subject_id, data) in res:
        homeworks_array.append(Homework(int(id), grade_id, subject_id, str(data.decode("utf8"))))
    return homeworks_array


def is_valid_admin(username, password_md5):
    id_ = 'SELECT * FROM admins WHERE username=\'%s\' AND password=\'%s\'' % (username, password_md5)
    print(id_)
    curs.execute(id_)
    if not curs.fetchone()[0]:
        return False
    return True


def add_homework_db(grade_id, subject_id, data):
    insert_command = 'INSERT INTO homework (grade_id, subject_id, data) VALUES (%s,%s,\'%s\')' % (
    grade_id, subject_id, data)
    curs.execute(insert_command)
    cnx.commit()


def get_subjects():
    curs.execute('SELECT * FROM subject')
    res = curs.fetchall()

    subjects_array = []
    for (id, title) in res:
        subjects_array.append(Subject(int(id), str(title.decode("utf8"))))
    return subjects_array


def close_connection():
    cnx.close()
