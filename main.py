#!/bin/env python3
#-*-coding:utf-8-*-

import os
import json
import random
import argparse
from datetime import datetime, timedelta

AUTHOR = 'STARRY-S'
VERSION = '1.0'
APP_NAME = 'Sau Daily Attendence'
DEBUG = False

# Args
parser = argparse.ArgumentParser(description="Sau Daily Attendence.")
parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
parser.add_argument("-c", "--config", help="Config file")
parser.add_argument("-m", "--mail", help="Send mail test message.", action="store_true")
parser.add_argument("-v", "--version", help="Show version", action="store_true")
args = parser.parse_args()

if args.debug:
  DEBUG = True

config_file = 'config.json'
if args.config:
  print("Set config file to: ", args.config)
  config_file = args.config

files = [
  "mail.py",
  "utils.py",
  "config.json"
]

# import files
for filename in files:
  if not os.path.exists(filename):
    print("File %s not found, please reinstall %s."%(filename, APP_NAME))
    send_mail(config_file, "File {} not found".format(filename))
    exit(1)

from mail import send_mail
from utils import open_config, write_config
import utils

try:
  import requests
except ImportError:
  print("Failed to import requests.")
  print("Install requirements via 'pip3 install requests'")
  send_mail(config_file, "failed to import requests")
  exit(1)

if args.mail:
  send_mail(config_file, "这是一条测试消息, 用来证明邮件功能可用.")
  exit(0)

# if args.clean:
#   ## TODO clean data in config file.
#   exit(0)

# if args.log:
#   # TODO log system.
#   exit(0)

if args.version:
  print("{n} by {a} \nVersion {v}".format(n=APP_NAME, a=AUTHOR, v=VERSION))
  exit(0)

now = datetime.now()

def main():
  c = open_config(config_file)

  last_post_date = getDate(c['data']['last_post'])
  if now - last_post_date < timedelta(days=1):
    debug("[Info]", "Already post.")
    exit(0)
  
  last_login_date = getDate(c['data']['last_login'])
  # if config don't have cookie 
  # or last success login over 30 days.
  if (c['data']['cookie'] == '') or (now - timedelta(days=30) > last_login_date):
    c = login(c)
    write_config(config_file, c)
    # if login failed and cookie is empty, can't post data.
    # if login failed but has previous cookie, try post data.
    if c['data']['cookie'] == '':
      print("Failed to login.")
      send_mail(config_file, "Login Failed.")
      exit(-1)
  
  print("Start posting data at {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))
  a = post(c)
  # server response 302 if cookie error
  # relogin to update cookie
  if a.status_code == 302:
    c = login(c)
    a = post(c)
  
  if a.status_code != 200:
    print("[ERROR] Code \"{}\", \
      post failed while post data.".format(a.status_code))
    send_mail(config_file, "Server response {}".format(a.status_code))
    
  post_info = json.loads(a.text)
  if post_info['e'] != 0:
    print("[ERROR] \"{}\"".format(post_info['d']['message']))
    send_mail(config_file, post_info['d']['message'])
    exit(-1)
  c['data']['last_post'] = now.strftime("%Y-%m-%d")
  write_config(config_file, c)

  print("Success!")

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
    print("Failed: Timeout.")
    send_mail(config_file, "Post Data Time out.")
    return a
  except requests.ConnectionError as e1:
    print("Failed: network failed or the server refused the connection.")
    print("        Please check your network connection or DNS setting.")
    print("        hint:   try 'ping app.sau.edu.cn' check DNS setting.")
    debug("Post Connection Error", e1)
    send_mail(config_file, "Network error")
    return a
  except requests.exceptions.RequestException as e2:
    print("Post failed.")
    send_mail(config_file, e2)
    return a
  debug("Post Response", a.text)
  return a

def login(c):
  print("Try login...")
  session = requests.session()
  # c = open_config(config_file)
  if c['username'] == '' or c['password'] == '' or c['username'] == '学号':
    print("[ERROR] No username or password found in config file.")
    print("        Please check config file.")
    exit(-1)
  
  login_data = {
    "username": c["username"],
    "password": c["password"]
  }
  try:
    a = session.post(utils.login_url, headers = utils.login_headers, 
      data = login_data, timeout = 10)
  # Through failed to login, but still return config data, use cookie to post data.
  except requests.exceptions.Timeout:
    print("Failed: Login Timeout.")
    return c
  except requests.ConnectionError as e1:
    print("Failed: network failed or the server refused the connection.")
    print("        Please check your network connection or DNS setting.")
    print("        hint: try 'ping ucapp.sau.edu.cn' check DNS setting.")
    debug("Login Connection Error", e1)
    return c
  except requests.exceptions.RequestException as e2:
    print("Login failed.")
    debug(e2)
    return c
  
  debug("Login Response", a.text)
  if a.status_code != 200:
    print("Login failed: server respond {}".format(a.status_code))
    return c
  
  login_info = json.loads(a.text)
  if login_info['e'] != 0:
    print("Failed: {}.".format(login_info['m']))
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
  print("Login success.")
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

def debug(info, msg):
  if (DEBUG): 
    print(info, msg)

if __name__ == '__main__':
  main()