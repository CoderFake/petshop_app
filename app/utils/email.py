import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template


def send_email(to, subject, template, **kwargs):
    try:
        app = current_app._get_current_object()
        smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('MAIL_PORT', 587))
        smtp_username = os.environ.get('MAIL_USERNAME')
        smtp_password = os.environ.get('MAIL_PASSWORD')
        default_sender = os.environ.get('MAIL_DEFAULT_SENDER', smtp_username)

        if not smtp_username or not smtp_password:
            app.logger.error("SMTP credentials not configured. Cannot send email.")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = default_sender
        msg['To'] = to

        html = render_template(f'emails/{template}.html', **kwargs)
        text = render_template(f'emails/{template}.txt', **kwargs)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(default_sender, to, msg.as_string())

        app.logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False


def send_verification_email(user, verification_url):
    return send_email(
        to=user.email,
        subject="Pet Shop - Xác thực tài khoản của bạn",
        template="verification",
        user=user,
        verification_url=verification_url
    )


def send_password_reset_email(user, reset_url):
    return send_email(
        to=user.email,
        subject="Pet Shop - Đặt lại mật khẩu của bạn",
        template="password_reset",
        user=user,
        reset_url=reset_url
    )


def send_order_confirmation_email(user, order):
    return send_email(
        to=user.email,
        subject=f"Pet Shop - Xác nhận đơn hàng #{order.id}",
        template="order_confirmation",
        user=user,
        order=order
    )