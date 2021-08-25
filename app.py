from flask import Flask
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy

import flask_admin as admin
from flask_admin.contrib.sqla import ModelView


# Create application
app = Flask(__name__, template_folder='templates')
app.debug = True

# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Models
class Catalog_unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(64))
    weight = db.Column(db.Integer)
    price = db.Column(db.Numeric(10,2))


class Delivery_address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64))
    reigion = db.Column(db.String(64))
    district = db.Column(db.String(64))
    settelment = db.Column(db.String(64))
    street = db.Column(db.String(64))
    address = db.Column(db.String(64))


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

# Create admin interface
class CatalogAdmin(ModelView):

    def __init__(self):
        super(CatalogAdmin, self).__init__(Catalog_unit, db.session, name="Catalog")

class DeliveryAdmin(ModelView):

    def __init__(self):
        super(DeliveryAdmin, self).__init__(Delivery_address, db.session, name="Delivery")


admin = admin.Admin(name="PulsuPro Admin", template_mode='bootstrap4')
admin.init_app(app)
admin.add_view(CatalogAdmin())
admin.add_view(DeliveryAdmin())

if __name__ == '__main__':

    # Create DB
    db.create_all()

    # Start app
    app.run()
