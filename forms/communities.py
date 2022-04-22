from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length


class CommunitiesForm(FlaskForm):
    name = StringField("Название группы", validators=[DataRequired()])
    interes = StringField("Описание", validators=[DataRequired(), Length(max=80)])
    location = StringField("Город, в котором вы находитесь", validators=[DataRequired()])
    movie = BooleanField("Фильмы, сериалы")
    sport = BooleanField('Спорт')
    turizm = BooleanField("Туризм")
    book = BooleanField("Книги")
    music = BooleanField('Музыка')
    kitchen = BooleanField("Еда")
    picture = BooleanField("Рисование")
    submit = SubmitField('Создать')