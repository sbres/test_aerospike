from uuid import uuid4
from flask import Flask, request
import hashlib, uuid
import aerospike
import json
import time
import logging
import socket

#############   GEVENT IMPORTS   ############

from gevent.wsgi import WSGIServer
############# END GEVENT IMPORTS ############

application = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formatter
logging.basicConfig(filename='flask.log', level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


config = {
  'hosts': [('128.199.87.171', 3000)]
}
namespace = 'test'

@application.route('/')
def hello_world():
    return 'Sup ?'

@application.route('/login', methods=['POST'])
def login():
    try:
        client = aerospike.client(config).connect()
    except Exception, e:
        logging.error("failed to connect to the cluster with // {0} ".format(e.message)
        return 'KO', 500
    to_check = ['username', 'password']
    for element in to_check:
        if request.form.get(element) is None:
            client.close()
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    password = request.form.get('password')

    (key, meta, bin) = client.get((namespace, 'user', username))
    if meta is None:
        client.close()
        return 'User {0} don\'t exists.'.format(username), 422
    h_password = hashlib.sha512(password).hexdigest()
    db_pass = bin['password']
    if db_pass != h_password:
        return 'Wrong password', 401
    _return = {'mail': bin['mail']}
    client.close()
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
            client.close()
            return '{0} not in request.'.format(element)
    username = request.form.get('username')
    mail = request.form.get('mail')
    password = request.form.get('password')

    (key, meta) = client.exists((namespace, 'user', username))
    if meta is not None:
        client.close()
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
        client.close()
        logging.error('failed to put data on db // {0}'.format(e.message)), 500
    client.close()
    return 'OK', 200


if __name__ == '__main__':
    hostname = socket.gethostname()
    if hostname == 'Stephanes-MacBook-Pro.local':
        application.debug = True
        application.run(host='0.0.0.0', port=80)
    else:
        http_server = WSGIServer(('', 80), application)
        http_server.serve_forever()

