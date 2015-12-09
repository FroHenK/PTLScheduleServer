import os
import mysql
from datetime import datetime
from mysql.connector import (connection)


class Grade:
    def __init__(self, id, title):
        self.title = title
        self.id = id


class DayElement:
    def __init__(self,id, grade_id, date, subject_id,subject_name):
        self.subject_name = subject_name
        self.subject_id = subject_id
        self.date = date
        self.grade_id = grade_id
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

def get_all_homeworks():
    id_ = 'SELECT * FROM homework'

    curs.execute(id_)

    res = curs.fetchall()

    homeworks_array = []
    for (id, grade_id, subject_id, data) in res:
        homeworks_array.append(Homework(int(id), grade_id, subject_id, str(data.decode("utf8"))))
    return homeworks_array

def create_day_element_db(grade_id, datetime, subject_id):
    insert_command = 'INSERT INTO day_element (grade_id, date, subject_id)  VALUES (%s,\'%s\',%s)' % (
        grade_id, datetime.strftime('%Y-%m-%d %H:%M:00'), subject_id)
    curs.execute(insert_command)
    cnx.commit()


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

def get_day_db(grade_id,date):
    elements_array=[]
    command='SELECT * FROM day_element WHERE grade_id = %s AND date BETWEEN \'%s 00:00:00\' AND \'%s 23:59:59\' ORDER BY date'%(grade_id,date.strftime('%Y-%m-%d'),date.strftime('%Y-%m-%d'))
    curs.execute(command)
    res = curs.fetchall()
    for (id, grade_id, date, subject_id) in res:
            curs.execute('SELECT title FROM subject WHERE id=%s'%subject_id)
            title=curs.fetchone()[0]
            elements_array.append( DayElement(id,grade_id,date,subject_id,str(title.decode('utf8'))) )

    return elements_array

def get_all_day_db():
    elements_array=[]
    command='SELECT * FROM day_element'
    curs.execute(command)
    res = curs.fetchall()
    for (id, grade_id, date, subject_id) in res:
            curs.execute('SELECT title FROM subject WHERE id=%s'%subject_id)
            title=curs.fetchone()[0]
            elements_array.append( DayElement(id,grade_id,date,subject_id,str(title.decode('utf8'))) )

    return elements_array

def get_homework_id(id):
    id_ = 'SELECT * FROM homework WHERE id=%s' % (id)

    curs.execute(id_)

    res = curs.fetchall()

    homeworks_array = []
    for (id, grade_id, subject_id, data) in res:
        homeworks_array.append(Homework(int(id), grade_id, subject_id, str(data.decode("utf8"))))
    return homeworks_array[0]

def delete_day_db_id(id):

    command='DELETE  FROM day_element WHERE id=%s'%id

    curs.execute(command)
    cnx.commit()

def delete_homework_id(id):

    command='DELETE  FROM homework WHERE id=%s'%id

    curs.execute(command)
    cnx.commit()

def get_day_db_id(id):
    elements_array=[]
    command='SELECT * FROM day_element WHERE id=%s'%id
    curs.execute(command)
    res = curs.fetchall()
    for (id, grade_id, date, subject_id) in res:
            curs.execute('SELECT title FROM subject WHERE id=%s'%subject_id)
            title=curs.fetchone()[0]
            elements_array.append( DayElement(id,grade_id,date,subject_id,str(title.decode('utf8'))) )

    return elements_array[0]


def get_subjects():
    curs.execute('SELECT * FROM subject')
    res = curs.fetchall()

    subjects_array = []
    for (id, title) in res:
        subjects_array.append(Subject(int(id), str(title.decode("utf8"))))
    return subjects_array



def close_connection():
    cnx.close()
