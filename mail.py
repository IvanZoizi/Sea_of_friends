from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import logging


def send_mail(email=None):
    try:
        msg = MIMEMultipart()
        password = "ANf-amW-9kc-5H4"
        msg['From'] = "seaoffriendsforyou@gmail.com"
        msg['To'] = email
        msg['Subject'] = f"Подтверждение адреса электронной почты"
        msg.attach(MIMEText(f'<h1>Проверка адреса электронной почты</h1> <h1>Чтобы завершить настройку учетной записи, нам нужно убедиться в том, что этот адрес электронной почты принадлежит вам</h1><a href=http://127.0.0.1:5000/login/{email}">Перейти</a>', 'html', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        logging.warning(e)
        return "Что-то пошло не так"