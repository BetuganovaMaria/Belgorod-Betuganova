import sqlalchemy
from forms.user import RegisterForm
from flask import Flask, render_template, redirect, abort, request
from flask_login import login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask_login import LoginManager
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.tasks import TasksForm
from forms.calculator import CalculatorForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def first():
    return render_template('first.html',
                           title='Добро пожаловать!')


@app.route('/tasks')
def tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks)
    return render_template('tasks.html',
                           title='Мои заметки',
                           tasks=tasks, db_sess=db_sess)


@app.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/tasks')
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html',
                           title='Авторизация',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html',
                           title='Регистрация',
                           form=form)


@app.route('/add_tasks', methods=['GET', 'POST'])
@login_required
def add_news():
    form = TasksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.content = form.content.data
        current_user.tasks.append(tasks)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/tasks')
    return render_template('add_tasks.html', title='Добавление новости',
                           form=form)


@app.route('/add_tasks/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = TasksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            form.title.data = tasks.title
            form.content.data = tasks.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            tasks.title = form.title.data
            tasks.content = form.content.data
            db_sess.commit()
            return redirect('/tasks')
        else:
            abort(404)
    return render_template('add_tasks.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                        Tasks.user == current_user
                                        ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/tasks')


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    form = CalculatorForm()
    result = ''
    if form.validate_on_submit():
        sign = form.sign.data.split()[1]
        if sign == '+':
            result = form.first.data + form.second.data
        elif sign == '-':
            result = form.first.data - form.second.data
        elif sign == '*':
            result = form.first.data * form.second.data
        elif sign == '/':
            result = form.first.data / form.second.data
        elif sign == '^':
            result = form.first.data ** form.second.data
    return render_template('calculator.html',
                           title='Калькулятор',
                           form=form,
                           result=str(result))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.run(port=8080, host='127.0.0.1')
