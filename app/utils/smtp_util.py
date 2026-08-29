"""邮件发送工具。

封装 SMTP 发送逻辑，简化验证码、通知类消息的发送流程。
"""

import smtplib
from email.mime.text import MIMEText

from app.core.config import settings


def send_message(body: str, to: str, subject: str):
    """发送文本邮件。

    body 是邮件正文内容，to 是收件人地址，subject 是邮件主题。
    """
    # 将正文构造成 MIME 文本，指定 UTF-8 编码以支持中文内容。
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject

    # 通过 SSL 连接 SMTP 服务器，并执行登录和邮件发送操作。
    server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.login(settings.SMTP_USER, settings.SMTP_PASS)

    server.sendmail(settings.SMTP_USER, to, msg.as_string())
    server.quit()