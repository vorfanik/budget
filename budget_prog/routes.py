import os
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
from datetime import datetime
import secrets
from PIL import Image
from flask_mail import Message
from . import db, app, bcrypt, Account, Entries, mail
from .form import RegistrationForm, SingInForma, SendEmailForm, PasswordUpdateForm, EntriesForm, AccountUpdateForm


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('signin'))
    form = RegistrationForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        account = Account(form.name.data, form.email.data, encrypted_password)
        db.session.add(account)
        db.session.commit()
        flash('You have successfully registered! You can log in!', 'success')
        return redirect(url_for('signin'))
    return render_template('registration.html', form=form)


@app.route("/", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('entries'))
    form = SingInForma()
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('entries'))
        else:
            flash('Login failed. Check your email and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    form = SendEmailForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with instructions on how to reset your password.', 'info')
        return redirect(url_for('signin'))
    return render_template('reset_request.html', form=form)



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request',
                  sender='The Lord of The Python',
                  recipients=[user.email])
    msg.body = f'''Click the link to reset your password:

    {url_for('reset_token', token=token, _external=True)}

    If you did not make this request, do nothing and the password will not be changed.
    '''
    mail.send(msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = Account.verify_reset_token(token)
    if user is None:
        flash('The request is invalid or has expired', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordUpdateForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! Can log in', 'success')
        return redirect(url_for('signin'))
    return render_template('reset_token.html', form=form)


@app.route("/entries")
@login_required
def entries():
    page = request.args.get('page', 1, type=int)
    all_entries_page = Entries.query.filter_by(account_id=current_user.id).order_by(Entries.date.desc()).paginate(
        page=page, per_page=5)
    try:
        all_entries = Entries.query.filter_by(account_id=current_user.id)[::-1]
    except:
        all_entries = []
    balance = 0
    for entries in all_entries:
        if entries.income:
            balance += entries.sum
        if entries.costs:
            balance -= entries.sum
    return render_template("entries.html", all_entries=all_entries, all_entries_page=all_entries_page, balance=balance,
                           datetime=datetime)


@app.route("/new_entries", methods=["GET", "POST"])
@login_required
def new_entries():
    form = EntriesForm()
    if form.validate_on_submit():
        new_entries = Entries(form.income.data, form.costs.data, form.sum.data, current_user.id)
        db.session.add(new_entries)
        db.session.commit()
        flash(f"Entries created", 'success')
        return redirect(url_for('entries'))
    return render_template("new_entries.html", form=form)


@app.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update(id):
    form = EntriesForm()
    entries = Entries.query.get(id)
    if form.validate_on_submit():
        entries.income = form.income.data
        entries.costs = form.costs.data
        entries.suma = form.sum.data
        db.session.commit()
        return redirect(url_for('entries'))
    return render_template("update.html", form=form, entries=entries)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    entries = Entries.query.get(id)
    db.session.delete(entries)
    db.session.commit()
    return redirect(url_for('entries'))


@app.route("/account")
@login_required
def account():
    image = url_for('static', filename=current_user.image)
    return render_template('account.html', image=image)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', picture_fn)

    output_size = (200, 350)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account_update", methods=['GET', 'POST'])
@login_required
def account_update():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.image.data:
            image = save_picture(form.image.data)
            current_user.image = image
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image = url_for('static', filename=current_user.image)
    return render_template('account_update.html', form=form, image=image)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('signin'))


# Klaidos
@app.errorhandler(404)
def error_404(error):
    error = 404
    return render_template("errors.html", error=error), 404


@app.errorhandler(500)
def error_500(error):
    error = 500
    return render_template("errors.html", error=error), 500
