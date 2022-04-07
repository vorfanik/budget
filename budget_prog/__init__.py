import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from flask_mail import Mail
from .password import password

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'balance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message_category = 'info'

from .models import Account, Entries


@login_manager.user_loader
def load_user(account_id):
    return Account.query.get(int(account_id))


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == "python.vornik@gmail.com"


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'python.vornik@gmail.com'
app.config['MAIL_PASSWORD'] = password
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

from . import routes

# Prisijungus su python.vornik@gmail.com loginu galima redaguot Entries ir Account (Admin ijungti per http://127.0.0.1:5000/admin/)
admin = Admin(app)
admin.add_view(MyModelView(Entries, db.session))
admin.add_view(MyModelView(Account, db.session))



