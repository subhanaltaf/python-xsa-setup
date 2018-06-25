import os
from flask import Flask
from cfenv import AppEnv
from hdbcli import dbapi

import logging
from cf_logging import flask_logging

#imports for user authorization
from sap import xssec
from flask import request
from flask import abort

app = Flask(__name__)
env = AppEnv()

flask_logging.init(app, logging.INFO)
logger = logging.getLogger('route.logger')

#assign port for Flask application to run on
port = int(os.environ.get('PORT', 3000))
hana = env.get_service(name='hdi-db')

#access credentials of uaa service
uaa_service = env.get_service(name=’myuaa’).credentials

@app.route('/')
def hello():
    #check if authorization information is provided
    if ‘authorization’ not in request.headers:
        abort(403)
    
    #check if user is authorized
    access_token = request.headers.get(‘authorization’)[7:]
    security_context = xssec.create_sercurity_context(access_token, uaa_service)
    isAuthorized = security_context.check_scope(‘openid’)
    
    if not isAuthorized:
	abort(403)

    conn = dbapi.connect(address=hana.credentials['host'],
                         port=int(hana.credentials['port']),
                         user=hana.credentials['user'],
                         password=hana.credentials['password'],
                         CURRENTSCHEMA=hana.credentials['schema'])

    if conn.isconnected():
        logger.info('Connection to databse successful')
    else:
        logger.info('Unable to connect to database')

    cursor = conn.cursor()
    cursor.execute("select CURRENT_UTCTIMESTAMP from DUMMY", {})
    ro = cursor.fetchone()
    cursor.close()
    conn.close()

    return "Current time is: " + str(ro["CURRENT_UTCTIMESTAMP"])

if __name__ == '__main__':
    app.run(port=port)
