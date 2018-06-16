import os
from flask import Flask
from cfenv import AppEnv
from hdbcli import dbapi

import logging
from cf_logging import flask_logging

app = Flask(__name__)    #create instance of Flask
env = AppEnv()        #used to obtain environment variables

flask_logging.init(app, logging.INFO)
logger = logging.getLogger('route.logger')

#assign port for Flask application to run on
port = int(os.environ.get('PORT', 3000))
hana = env.get_service(name='hdi-db')    #connect to hdi-db service

#execute hello function when page URL is requested
@app.route('/')
def hello():
    #connect to DB using credentials from hdi-db service
    conn = dbapi.connect(address=hana.credentials['host'],
                         port=int(hana.credentials['port'],
                         user=hana.credentials['user'],
                         password=hana.credentials['password'],
                         CURRENTSCHEMA=hana.credentials['schema'])

    #check if DB connection has been established successfully and
    #output to application logs
    if conn.isconnected():
        logger.info('Connection to databse successful')
    else:
        logger.info('Unable to connect to database')
        
    cursor = conn.cursor()

    #execute SQL query
    cursor.execute('SELECT CURRENT_UTCTIMESTAMP FROM DUMMY', {})
    ro = cursor.fetchone()    #get the first result
    cursor.close()
    conn.close()        #close DB connection

    #return query results
    return "Current time is: " + str(ro["CURRENT_UTCTIMESTAMP"])

if __name__ == '__main__':
    app.run(port=port)
