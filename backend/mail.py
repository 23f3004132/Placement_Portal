import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_email, subject, message):
    from flask import current_app

    app = current_app
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    sender   = app.config.get('MAIL_FROM')

    if not username or not password:
        app.logger.warning('MAIL_USERNAME/MAIL_PASSWORD not configured; skipping email.')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = sender
    msg['To']      = to_email
    msg.attach(MIMEText(message, 'html'))

    try:
        server = smtplib.SMTP(app.config.get('MAIL_HOST'), app.config.get('MAIL_PORT'))
        if app.config.get('MAIL_USE_TLS', True):
            server.starttls()
        server.login(username, password)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as error:
        app.logger.error(f'Failed to send email: {error}')
        return False
