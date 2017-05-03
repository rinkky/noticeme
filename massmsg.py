#! python2
# coding=utf-8

import requests
import wechatcfg
import sys
import os
sys.path.append(os.path.join(sys.path[0],os.pardir))
from playstoredata import playstoredata
import time
import json

url_token = (
	"https://api.weixin.qq.com/cgi-bin/token"
	"?grant_type=client_credential&appid={0}&secret={1}"
).format(
		wechatcfg.appid, 
		wechatcfg.secret
)

r = requests.get(url_token)

if r.status_code != 200:
	sys.exit(0)

print(r.status_code)

data = r.json()
access_token = data.get("access_token")

url_sendmsg = (
	"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={0}"
).format(access_token)
print(url_sendmsg)

apps = playstoredata.get_notice_apps()
if apps is None:
	text_to_send = time.asctime() + "\nNo apps on sale"
else:
	text_to_send = time.asctime() + "\nhere are the apps on sale:\n"
	apps_detail = []
	for app in apps:
		apps_detail.append(
			"{0}\n{1}\n{2}\n----\n".format(
				app.uniq_name,
				app.name,
				app.price
			)
		)
	text_to_send = text_to_send + "".join(apps_detail)
print(text_to_send)

data_to_send = {
	"filter": {
		"is_to_all": False,
		"tag_id": 0
	},
	"msgtype": "text",
	"text": {"content": text_to_send,}
}
data_to_send = json.dumps(data_to_send)
headers = {"content-type": "application/json"}

#time.sleep(60)
r = requests.post(url_sendmsg, data=data_to_send, headers=headers)
print(r.status_code)
#print(r.text)
errmsg = r.json()
if errmsg.get("errcode") == 0:
	playstoredata.clean_notice_apps()