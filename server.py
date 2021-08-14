from flask_app import app
from flask_app.controllers import users, stores, checkout #insert name of controller files/file here#

if __name__ == '__main__':
    app.run(debug = True)
