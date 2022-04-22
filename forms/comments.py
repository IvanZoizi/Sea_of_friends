from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    name = StringField("Комментарий", validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')