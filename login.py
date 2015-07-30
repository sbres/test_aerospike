from uuid import uuid4
from flask import Flask, request
import hashlib, uuid
import aerospike
import json
import time
import logging
import socket

#############   TORNADO IMPORTS   ############
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
############# END TORNADO IMPORTS ############

application = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formatter
logging.basicConfig(filename='flask.log', level=logging.INFO)
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
    try:
        client = aerospike.client(config).connect()
    except:
        logging.error("failed to connect to the cluster with // {0}".format(config['hosts']))
        return 'KO', 500
    to_check = ['username', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    password = request.form.get('password')

    (key, meta, bin) = client.get((namespace, 'user', username))
    if meta is None:
        return 'User {0} don\'t exists.'.format(username), 422
    h_password = hashlib.sha512(password).hexdigest()
    db_pass = bin['password']
    if db_pass != h_password:
        return 'Wrong password', 401
    _return = {'mail': bin['mail']}
    return json.dumps(_return)


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
    uid = str(uuid4())
    h_password = hashlib.sha512(password).hexdigest()
    bin = {'id': uid,
           'password': h_password,
           'mail': mail
           }
    try:
        client.put(key, bin)
    except Exception as e:
        logging.error('failed to put data on db // {0}'.format(e.message)), 500
    return 'OK', 200


if __name__ == '__main__':
    hostname = socket.gethostname()
    if hostname == 'Stephanes-MacBook-Pro.local':
        application.debug = True
        application.run(host='0.0.0.0', port=80)
    else:
        http_server = HTTPServer(WSGIContainer(application))
        http_server.listen(80)
        IOLoop.instance().start()

