#! python2
# coding=utf-8

"""
reply msg from wechat server

"""

import web
import wechatcfg
import hashlib

urls = (
	"/wechat", "Wechat"
)


class Wechat:

	def GET(self):
		#verify msg from wechat server
		#see https://mp.wexin.qq.com/wiki
		data = web.input()
		echostr = data.echostr
		if self._is_from_wechat(data):
			return echostr

	def POST(self):



	def _is_from_wechat(self,data):
		token = wechatcfg.wechat_token
		timestamp = data.timestamp
		nonce = data.nonce
		signature = data.signature		

		lst = [token,timestamp,nonce]
		lst.sort()
		sha1 = hashlib.sha1()
		sha1.update("",join(lst))
		return signature == sha1.hexdigest()


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()