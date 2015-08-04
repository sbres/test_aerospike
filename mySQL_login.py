from uuid import uuid4
from flask import Flask, request, g
import hashlib, uuid
import json
import time
import logging
import socket

#############   GEVENT IMPORTS   ############

from gevent.wsgi import WSGIServer
############# END GEVENT IMPORTS ############


#############   Mysql imports    ############

import MySQLdb


#############################################

application = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formatter
logging.basicConfig(filename='flask.log', level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@application.before_request
def db_connect():
    g.conn = MySQLdb.connect(host='128.199.251.11',
                          user='dev',
                          passwd='dev',
                          db='dev')
    g.cursor = g.conn.cursor()

@application.after_request
def db_disconnect(response):
    g.cursor.close()
    g.conn.close()
    return response

def query_db(query):
    g.cursor.execute(query)
    rv = [dict((g.cursor.description[idx][0], value)
    for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
    return rv

namespace = 'test'



@application.route('/')
def hello_world():
    return 'Sup ?'

@application.route('/loaderio-ad9ef568269be193b06e0ea51e6c53c4.txt')
def loader_io():
    return 'loaderio-ad9ef568269be193b06e0ea51e6c53c4'


@application.route('/login', methods=['POST'])
def login():
    to_check = ['username', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    password = request.form.get('password')
    data = query_db("SELECT * from user where username='{0}'".format(username, password))
    print data
    if data is None:
        return 'User {0} don\'t exists.'.format(username), 422
    h_password = hashlib.sha512(password).hexdigest()
    db_pass = data[3]
    if db_pass != h_password:
        return 'Wrong password', 401
    _return = {'mail': data[2]}
    return json.dumps(_return)


@application.route('/singin', methods=['POST'])
def inscription():
    to_check = ['username', 'mail', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    mail = request.form.get('mail')
    password = request.form.get('password')
    data = query_db("SELECT * from user where username='{0}' and password='{1}'".format(username, password))
    if data is not None:
        return 'User {0} already exists.'.format(username), 422
    uid = str(uuid4())
    h_password = hashlib.sha512(password).hexdigest()
    bin = {'id': uid,
           'password': h_password,
           'mail': mail
           }
    try:
        data = query_db("INSERT into user (username, mail, password) VALUES ('{0}', '{1}', '{2}')".format(username, mail, h_password))
    except Exception as e:
        logging.error('failed to put data on db // {0}'.format(e.message))
        return 'KO', 500
    return 'OK', 200


if __name__ == '__main__':
    hostname = socket.gethostname()
    if hostname == 'Stephanes-MacBook-Pro.local':
        print 'DEV ' * 10
        application.debug = True
        application.run(host='0.0.0.0', port=80)

    else:
        print 'PROD ' * 10
        http_server = WSGIServer(('', 80), application)
        http_server.serve_forever()

