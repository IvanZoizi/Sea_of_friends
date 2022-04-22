from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class CommunitiesForm(FlaskForm):
    name = StringField("Почта", validators=[DataRequired()])
    interes = StringField("Интересы", validators=[DataRequired()])
    location = StringField("Город", validators=[DataRequired()])
    submit = SubmitField('Войти')