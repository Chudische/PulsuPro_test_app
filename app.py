import os

from flask import Flask, redirect, url_for, abort, request
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import helpers as admin_helpers
from flask_security import Security, current_user, SQLAlchemyUserDatastore
from flask_security.models import fsqla_v2 as fsqla
from flask_security.utils import encrypt_password

# Create application
app = Flask(__name__, template_folder='templates')
app.debug = True
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# Define models
fsqla.FsModels.set_db_info(db)
db.metadata.clear()

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, fsqla.FsRoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, fsqla.FsUserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Custom models
class Catalog_unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
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

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )
    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class DeliveryAdmin(ModelView):
    column_filters = ('country', 'settelment', 'street')

    def __init__(self):
        super(DeliveryAdmin, self).__init__(Delivery_address, db.session, name="Delivery")
        
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )
    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

admin = admin.Admin(name="PulsuPro Admin", base_template='base.html', template_mode='bootstrap4')
admin.init_app(app)
admin.add_view(CatalogAdmin())
admin.add_view(DeliveryAdmin())

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(            
            email='admin@admin.com',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )
        
        countries = ('Ukraine', 'Poland', 'England', 'Russia', 'USA', 'Canada', 'Australia')
        reigions = ('North', 'West', 'East', 'South')
        districts = ('Small', 'Big', "High", 'Low')
        settelments = ('Sity', 'Settelment', 'Village', 'Town')
        streets = ('United', "Popova", 'Shevchenko', 'Briton', 'Derebasovskaya', 'Zavodova')
        addresses = ('12', '123', '55', '46/2', '111', '78/1')
        for i in range(100):
            address = Delivery_address(
                country = random.choice(countries),
                reigion = random.choice(reigions),
                district = random.choice(districts),
                settelment = random.choice(settelments),
                street = random.choice(streets),
                address = random.choice(addresses),            )
            db.session.add(address)
        db.session.commit() 
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.run()
