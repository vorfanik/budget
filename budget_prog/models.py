from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from . import app, db


class Account(db.Model, UserMixin):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String(20), nullable=False)
    email = db.Column("Email", db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False)
    password = db.Column("Password", db.String(60), unique=True, nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.image = 'default.jpg'
        self.password = password

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Account.query.get(user_id)


class Entries(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column("Date", db.DateTime)
    income = db.Column("Income", db.Boolean)
    costs = db.Column("Costs", db.Boolean)
    sum = db.Column("Sum", db.Integer)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    account = db.relationship("Account", lazy=True)

    def __init__(self, income, costs, sum, account_id):
        self.income = income
        self.costs = costs
        self.sum = sum
        self.account_id = account_id
        self.date = datetime.now()


db.create_all()
