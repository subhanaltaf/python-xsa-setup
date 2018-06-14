import os
from flask import Flask

#create instance of Flask
app = Flask(__name__)

#assign port for Flask application to run on
port = int(os.environ.get('PORT', 3000))

#execute hello function when page URL is requested
@app.route('/')
def hello():
    return "Hello Python World"

if __name__ == '__main__':
    app.run(port=port)
