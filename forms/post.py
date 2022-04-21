from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    content = StringField("Содержание сообщения", validators=[DataRequired()])
    private = BooleanField('Приватное')
    submit = SubmitField('Войти')