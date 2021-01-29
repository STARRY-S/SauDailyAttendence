#!/usr/bin/env python3
#-*-coding:utf-8-*-

### File name: mail.py
## Created by STARRY-S

import smtplib
from email.message import EmailMessage
from utils import open_config, write_config

def send_mail(cf, msg):
  # get config
  c = open_config(cf)
  host_server = c['mail']['host_server']
  sender = c['mail']['sender']
  pwd = c['mail']['password']
  receiver = c['mail']['receiver']
  content = ("======== 自动打卡失败 ======\n" +
            "\n错误信息:\n{}".format(msg))

  if host_server == "smtp服务器" or sender == "":
    print("Failed to send mail, please check the config file.")
    return -1

  smtp = smtplib.SMTP_SSL(host_server)
  # Hello!
  smtp.ehlo(host_server)
  smtp.login(sender, pwd)

  message = EmailMessage()
  message.set_content(content)

  message['Subject'] = "自动打卡失败提醒"
  message['From'] = sender
  message['To'] = receiver

  smtp.send_message(message)
  print("Mail sent.")


if __name__ == "__main__":
  send_mail("config.json", "It works!")