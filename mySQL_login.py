from uuid import uuid4
from flask import Flask, request
import hashlib, uuid
import json
import time
import logging
import socket

#############   GEVENT IMPORTS   ############

from gevent.wsgi import WSGIServer
############# END GEVENT IMPORTS ############


#############   Mysql imports    ############

from flask.ext.mysql import MySQL


#############################################

application = Flask(__name__)
application.config['MYSQL_DATABASE_USER'] = 'dev'
application.config['MYSQL_DATABASE_PASSWORD'] = 'dev'
application.config['MYSQL_DATABASE_DB'] = 'dev'
application.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql = MySQL()
mysql.init_app(application)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formatter
logging.basicConfig(filename='flask.log', level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

namespace = 'test'

@application.route('/')
def hello_world():
    return 'Sup ?'

@application.route('/login', methods=['POST'])
def login():
    to_check = ['username', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    password = request.form.get('password')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from user where username='{0}' and password='{1}'".format(username, password))
    data = cursor.fetchone()
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
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from user where username='{0}' and password='{1}'".format(username, password))
    data = cursor.fetchone()
    if data is not None:
        return 'User {0} already exists.'.format(username), 422
    uid = str(uuid4())
    h_password = hashlib.sha512(password).hexdigest()
    bin = {'id': uid,
           'password': h_password,
           'mail': mail
           }
    try:
        cursor.execute("INSERT into user (username, mail, password) VALUES ('{0}', '{1}', '{2}')".format(username, mail, h_password))
        cursor.close()
    except Exception as e:
        logging.error('failed to put data on db // {0}'.format(e.message))
        return 'KO', 500
    return 'OK', 200


if __name__ == '__main__':
    hostname = socket.gethostname()
    if hostname == 'Stephanes-MacBook-Pro.local':
        application.debug = True
        application.run(host='0.0.0.0', port=80)
    else:
        http_server = WSGIServer(('', 80), application)
        http_server.serve_forever()

