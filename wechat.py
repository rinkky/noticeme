#! python2
# coding=utf-8

"""
reply msg from wechat server

"""

import web
import wechatcfg
import hashlib
import re
from lxml import etree
import sys
import os
import time
sys.path.append(os.path.join(sys.path[0],os.pardir))
from playstoredata import playstoredata
from test import Test
import logging

urls = (
	"/wechat", "Wechat",
	"/test","Test"
)
logging.basicConfig(
	filename="./wechat.log",
	level=logging.DEBUG,
#	formatter=logging.Formatter(
#		"[%(levelname)s][%(funcName)s][%(asctime)s]%(message)s"
#	)
)

class Wechat:
	def __init__(self):
		#init webpy template render
		self.app_root = os.path.dirname(__file__)
		self.templates_root = os.path.join(self.app_root,"templates")
		self.render = web.template.render(self.templates_root)

	def GET(self):
		#verify msg from wechat server
		#see https://mp.wexin.qq.com/wiki
		data = web.input()
		echostr = data.echostr
		if self._is_from_wechat(data):
			return echostr

	def POST(self):
		str_xml = web.data()
		wechat_msg = self._trans_msg(str_xml)
		if (wechat_msg["MsgType"] == "event" and 
			wechat_msg["Event"] == "MASSSENDJOBFINISH"):
			logging.debug(str_xml)
			print(str_xml)
		return self._get_reply(wechat_msg)


	def _is_from_wechat(self,data):
		token = wechatcfg.wechat_token
		timestamp = data.timestamp
		nonce = data.nonce
		signature = data.signature

		lst = [token,timestamp,nonce]
		lst.sort()
		sha1 = hashlib.sha1()
		sha1.update("".join(lst))
		return signature == sha1.hexdigest()

	def _trans_msg(self,xml_msg):
		xml = etree.fromstring(xml_msg)
		msg_type = xml.find("MsgType").text
		from_user = xml.find("FromUserName").text
		to_user = xml.find("ToUserName").text
		msg_id = xml.find("MsgId")
		content = ""
		event = ""
		if msg_type == "text":
			content = xml.find("Content").text
 		elif msg_type == "event":
			event = xml.find("Event").text
		return {
			"MsgType": msg_type,
			"FromUserName": from_user,
			"ToUserName": to_user,
			"Content": content,
			"MsgId": msg_id,
			"Event":event
		}

	def _get_reply(self,wechat_msg):
		msg_type = wechat_msg["MsgType"]
		if msg_type == "event":
			event = wechat_msg["Event"]
			if event == "subscribe":
				reply_content = (
					"Thank you for following, "
					"try this reply:\ncom.mojang.minecraftpe"
				)
				return self.render.reply_text(
					wechat_msg["FromUserName"],
					wechat_msg["ToUserName"],
					int(time.time()),
					reply_content
				)
			elif event == "CLICK":
				eventkey = wechat_msg["EventKey"]
				if eventkey == "HELP":
					reply_content = "HELP CONTENT"
				elif eventkey == "SHOW_LIST":
					reply_content = "LIST CONTENT"
				elif eventkey == "TEST":
					reply_content = "TEST"
#			if event == "MASSSENDJOBFINISH":
#				logging.debug("")
#				return None
		elif msg_type == "text":
			msg_content = wechat_msg["Content"]
			p = re.compile(r"\w+\.\w+\.\w+")
			match = p.match(msg_content)
			reply_content = ""
			if match:
				app_uniq_name = match.group(0)
				app_detail = playstoredata.get_app_detail(app_uniq_name)
				if (app_detail is None) or (app_detail["uniq_name"] is None):
					reply_content = "No such app"
				else:
					reply_content = "{0} \n{1} \n${2}".format(
						app_uniq_name,
						app_detail["name"],
						str(app_detail["price"])
					)
			else:
				reply_content = "No such app"

			return self.render.reply_text(
				wechat_msg["FromUserName"],
				wechat_msg["ToUserName"],
				int(time.time()),
				reply_content
			)


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
