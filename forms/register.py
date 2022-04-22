from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    movie = BooleanField("Фильмы, сериалы")
    sport = BooleanField('Спорт')
    turizm = BooleanField("Туризм")
    book = BooleanField("Книги")
    music = BooleanField('Музыка')
    kitchen = BooleanField("Еда")
    picture = BooleanField("Рисование")
    location = StringField("Локация")
    location_submit = SubmitField("Подтвердить локацию")
    submit = SubmitField('Зарегистрировать')