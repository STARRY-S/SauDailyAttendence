#!/usr/bin/env python3
#-*- coding: utf-8 -*-

### File name: mail.py
## Created by STARRY-S

import json
import sys

DEBUG = false
LOG_NAME = "main.log"

login_headers = {
  "Accept": "application/json, text/javascript, */*; q=0.01",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
  "Connection": "keep-alive",
  "Content-Length": "46",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "Host": "ucapp.sau.edu.cn",
  "Origin": "https://ucapp.sau.edu.cn",
  "Referer": "https://ucapp.sau.edu.cn/campus/wap/login/index",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-origin",
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

post_headers = {
  "Host": "app.sau.edu.cn",
  "Connection": "keep-alive",
  "Content-Length": "840",
  "Accept": "application/json, text/javascript, */*; q=0.01",
  "X-Requested-With": "XMLHttpRequest",
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "Origin": "https://app.sau.edu.cn",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Dest": "empty",
  "Referer": "https://app.sau.edu.cn/form/wap/default/index?formid=10&nn=6872.794873703194",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
  "Cookie": ""
}

login_url = "https://ucapp.sau.edu.cn/wap/login/invalid"
post_url = "https://app.sau.edu.cn/form/wap/default/save"

# open config file
def open_config(config_file):
  with open(config_file) as config_open:
    configs = json.loads(config_open.read())
    # debug("Configs", configs)
    return configs

# write json data to config file
def write_config(config_file, data):
  with open(config_file, 'w') as config_write:
    json.dump(data, config_write, indent=2, ensure_ascii=False)

def LOG_DEBUG(*msg, info="[DEBUG]")
  with open(LOG_NAME, 'w') as log_file
    print(info, *msg, file = sys.stdout)
    print(info, *msg, file = log_file)

def LOG_INFO(*msg, info="[INFO] ")
  with open(LOG_NAME, 'w') as log_file
    print(info, *msg, file = sys.stdout)
    print(info, *msg, file = log_file)

def LOG_ERROR(*msg, info="[ERROR]")
  with open(LOG_NAME, 'w') as log_file
    print(info, *msg, file=sys.stderr)
    print(info, *msg, file=log_file)
