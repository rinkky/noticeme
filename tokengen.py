
#!python2
# coding=utf-8
import requests
import wechatcfg
import time

WECHATKEY_EXPIRES_IN = "expires_in"
WECHATKEY_ACCESS_TOKEN = "access_token"
timeout = 7199
lastgettime = 0
token = ""

url_token = (
	"https://api.weixin.qq.com/cgi-bin/token"
	"?grant_type=client_credential&appid={0}&secret={1}"
).format(
		wechatcfg.appid, 
		wechatcfg.secret
)

def get_token():
	global token
	global timeout
	global lastgettime
	if timeout + lastgettime < time.time():
		lastgettime = time.time()
		r = requests.get(url_token)
		if r.status_code != 200:
			return None
		data = r.json()
		timeout = data.get(WECHATKEY_EXPIRES_IN) - 100
		token = data.get(WECHATKEY_ACCESS_TOKEN)
	return token

if __name__ == '__main__':
	print(get_token())