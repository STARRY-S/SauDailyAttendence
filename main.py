#!/bin/env python3
#-*-coding:utf-8-*-

import os
import json
import random
import argparse
from datetime import datetime, timedelta

AUTHOR = 'STARRY-S'
VERSION = '1.2.0'
APP_NAME = 'Sau Daily Attendence'
DEBUG = False

# Args
parser = argparse.ArgumentParser(description="Sau Daily Attendence.")
parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
parser.add_argument("-c", "--config", help="Config file")
parser.add_argument("-l", "--log", help="Log file")
parser.add_argument("-m", "--mail", help="Send mail test message.", action="store_true")
parser.add_argument("--clean", help="Clean data", action="store_true")
parser.add_argument("-v", "--version", help="Show version", action="store_true")
args = parser.parse_args()

# import files
files = [
  "mail.py",
  "utils.py",
  "config.json"
]

for filename in files:
  if not os.path.exists(filename):
    print("File {} not found, please reinstall {}.".format(filename, APP_NAME))
    send_mail("File {} not found".format(filename))
    exit(1)

from mail import send_mail
from utils import open_config, write_config
from utils import LOG_DEBUG, LOG_INFO, LOG_ERROR, LOG_WARN
import utils

# check args
if args.version:
  print("{n} by {a} \nVersion {v}".format(n=APP_NAME, a=AUTHOR, v=VERSION))
  exit(0)

if args.clean:
  c = open_config()
  c['data']['cookie'] = ''
  c['data']['last_login'] = ''
  c['data']['last_post'] = ''
  write_config(c)
  print("Data cleaned.")
  exit(0)

if args.config:
  utils.CONFIG_NAME = args.config
  LOG_INFO("Set config file to: ", args.config)

if args.log:
  utils.LOG_NAME = args.log
  LOG_INFO("Set log file to: ", args.log)

if args.mail:
  send_mail("这是一条测试消息, 用来证明邮件功能可用.")
  exit(0)

if args.debug:
  utils.DEBUG = True

try:
  import requests
except ImportError:
  LOG_ERROR("Failed to import requests.")
  LOG_ERROR("Install requirements via 'pip3 install requests'")
  send_mail("failed to import requests")
  exit(1)

now = datetime.now()

def main():
  c = open_config()

  last_post_date = getDate(c['data']['last_post'])
  if now - last_post_date < timedelta(days=1):
    LOG_INFO("Data is already post at", c['data']['last_post'])
    exit(0)

  last_login_date = getDate(c['data']['last_login'])
  # if config don't have cookie
  # or last success login over 30 days.
  if (c['data']['cookie'] == '') or (now - timedelta(days=30) > last_login_date):
    c = login(c)
    write_config(c)
    # if login failed and cookie is empty, can't post data.
    # if login failed but has previous cookie, try post data.
    if c['data']['cookie'] == '':
      # LOG_ERROR("Failed to login.")
      send_mail("Login Failed.")
      exit(-1)

  LOG_INFO("Starting post data at {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))
  a = post(c)
  # server response 302 if cookie error
  # relogin to update cookie
  if a.status_code == 302:
    LOG_WARN("login failed due to cookie out date.")
    c = login(c)
    a = post(c)

  if a.status_code != 200:
    LOG_ERROR("Code \"{}\", post failed while post data.".format(a.status_code))
    send_mail("Server response {}".format(a.status_code))

  post_info = json.loads(a.text)
  if post_info['e'] != 0:
    LOG_ERROR("\"{}\"".format(post_info['d']['message']))
    send_mail(post_info['d']['message'])
    exit(-1)
  c['data']['last_post'] = now.strftime("%Y-%m-%d")
  write_config(c)

  LOG_INFO("Success!\n")

def post(c):
  session = requests.session()
  post_data = c['post']
  utils.post_headers['Cookie'] = c['data']['cookie']
  # temperature from 36.1 to 36.7
  post_data['tiwen']  = "36.{}".format(str(random.randrange(1, 8, 1)))
  post_data['tiwen1'] = "36.{}".format(str(random.randrange(1, 6, 1)))
  post_data['tiwen2'] = "36.{}".format(str(random.randrange(1, 6, 1)))
  # Date: YYYY-MM-DD
  post_data['riqi'] = now.strftime("%Y-%m-%d")

  a = None
  try:
    a = session.post(utils.post_url, headers = utils.post_headers,
      data = post_data, params = {"formid": "10"}, timeout = 10)
  except requests.exceptions.Timeout:
    LOG_ERROR("Failed: Timeout.")
    send_mail("Post Data Time out.")
    return a
  except requests.ConnectionError as e1:
    LOG_ERROR("Failed: network failed or the server refused the connection.")
    LOG_ERROR("        Please check your network connection or DNS setting.")
    LOG_ERROR("        hint:   try 'ping app.sau.edu.cn' check DNS setting.")
    LOG_DEBUG("Post Connection Error", e1)
    send_mail("Network error")
    return a
  except requests.exceptions.RequestException as e2:
    LOG_ERROR("Post failed.")
    send_mail(e2)
    return a
  LOG_DEBUG("Post Response", a.text)
  return a

def login(c):
  LOG_INFO("Try login...")
  session = requests.session()
  # c = open_config()
  if c['username'] == '' or c['password'] == '' or c['username'] == '学号':
    LOG_ERROR("No username or password found in config file.")
    send_mail("Login failed -- no username or password.")
    exit(-1)

  login_data = {
    "username": c["username"],
    "password": c["password"]
  }
  try:
    a = session.post(utils.login_url, headers = utils.login_headers,
      data = login_data, timeout = 30)
  # Through failed to login, but still return config data, use cookie to post data.
  except requests.exceptions.Timeout:
    LOG_ERROR("Failed: Login Timeout.")
    return c
  except requests.ConnectionError as e1:
    LOG_ERROR("Failed: network failed or the server refused the connection.")
    LOG_ERROR("        Please check your network connection or DNS setting.")
    LOG_ERROR("        hint: try 'ping ucapp.sau.edu.cn' check DNS setting.")
    LOG_DEBUG("Login Connection Error", e1)
    return c
  except requests.exceptions.RequestException as e2:
    LOG_ERROR("Login failed.")
    LOG_DEBUG(e2)
    return c

  LOG_DEBUG("Login Response", a.text)
  if a.status_code != 200:
    LOG_ERROR("Login failed: server respond {}".format(a.status_code))
    return c

  login_info = json.loads(a.text)
  if login_info['e'] != 0:
    LOG_ERROR("Failed: {}.".format(login_info['m']))
    return c

  login_cookie = a.cookies.get_dict()
  # convert dict to string
  cookie_str = ""
  for x in login_cookie:
    cookie_str += "{}={};".format(x, login_cookie[x])
  # remove last ";"
  cookie_str = cookie_str[:-1]
  # debug("Login cookie", cookie_str)
  # Write new login cookie and login date to config file.
  c['data']['cookie'] = cookie_str
  c['data']['last_login'] = now.strftime("%Y-%m-%d")
  LOG_INFO("Login success.")
  return c

def getDate(s):
  if s == "":
    # return a very early date, for update cookie.
    return datetime(2000, 1, 1)
  s = s.split('-')
  d = datetime(
    int(s[0]),
    int(s[1]),
    int(s[2])
  )
  return d

if __name__ == '__main__':
  main()
