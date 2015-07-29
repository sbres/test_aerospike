from uuid import uuid4
from flask import Flask, request
import hashlib, uuid
import aerospike
import json
import time
import logging


#############   TORNADO IMPORTS   ############
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
############# END TORNADO IMPORTS ############

application = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


config = {
  'hosts': [ ('127.0.0.1', 3000) ]
}
namespace = 'test'

@application.route('/')
def hello_world():
    return 'Sup ?'

@application.route('/login', methods=['POST'])
def login():
    pass


@application.route('/singin', methods=['POST'])
def inscription():
    try:
        client = aerospike.client(config).connect()
    except:
        logging.error("failed to connect to the cluster with // {0}".format(config['hosts']))
        return 'KO', 500
    to_check = ['username', 'mail', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    mail = request.form.get('mail')
    password = request.form.get('password')

    (key, meta) = client.exists((namespace, 'user', username))
    if meta is not None:
        return 'User {0} already exists.'.format(username), 422
    uid = uuid4()
    h_password = hashlib.sha512(password).hexdigest()
    bin = {'id': uid,
           'password': h_password,
           'mail': mail
           }
    try:
        client.put(key, bin)
    except Exception as e:
        logging.error('failed to put data on db // {0}'.format(e.message)), 500



if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=80)


