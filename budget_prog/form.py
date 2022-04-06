from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from flask_wtf.file import FileField, FileAllowed
from . import Account, current_user


class RegistrationForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [Email(message=('Invalid address')), DataRequired()],
                        render_kw={"placeholder": "email@address.com"})
    password = PasswordField('Password', [DataRequired()])
    confirm_password = PasswordField("Confirm Password", [EqualTo('password', "Password must match.")])
    submit = SubmitField('Sign Up')

    def check_name(self, name):
        user = Account.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('This name has been used. Choose another.')

    def check_email(self, email):
        user_email = Account.query.filter_by(email=email.data).first()
        if user_email:
            raise ValidationError('This email has been used. Choose another.')


class AccountUpdateForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [Email(message=('Invalid address')), DataRequired()],
                        render_kw={"placeholder": "email@address.com"})
    image = FileField('Update profile photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def check_update_name(self, name):
        if name.data != current_user.name:
            user = Account.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('This name has been used. Choose another.')

    def check_update_email(self, email):
        if email.data != current_user.email:
            user_email = Account.query.filter_by(email=email.data).first()
            if user_email:
                raise ValidationError('This email has been used. Choose another.')


class SingInForma(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Log In')


class SendEmailForm(FlaskForm):
    email = StringField('Email', [Email(message=('Invalid address')), DataRequired()],
                        render_kw={"placeholder": "email@address.com"})
    submit = SubmitField('Send')

    def validate_email(self, email):
        user = Account.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account registered with this email address. Sign up.')


class PasswordUpdateForm(FlaskForm):
    password = PasswordField('Password', [DataRequired()])
    confirm_password = PasswordField("Confirm Password", [EqualTo('password', "Password must match.")])
    submit = SubmitField('Update Password')


class EntriesForm(FlaskForm):
    income = BooleanField('Income')
    costs = BooleanField('Costs')
    sum = FloatField('Sum', [DataRequired()])
    submit = SubmitField('Submit')
