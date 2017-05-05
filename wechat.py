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
import logging

urls = (
    "/wechat", "Wechat",
)

logging.basicConfig(
    filename="./wechat.log",
    level=logging.DEBUG,
    formatter=logging.Formatter(
        "[%(levelname)s][%(funcName)s][%(asctime)s]%(message)s"
    )
)

class Wechat:

    def __init__(self):
        #init webpy template render
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root,"templates")
        self.render = web.template.render(self.templates_root)
        self.help_reply = (
                "当你关注的APP信息有优惠时，我会通知你。\n"
                "回复包含appid的任意文字，可以获取APP的价格信息，"
                "同时把该APP添加进关注列表。\n"
                "你可以尝试复制该信息并回复。\n"
                "com.mojang.minecraftpe"
        )

    def GET(self):
        #verify msg from wechat server
        #see https://mp.wexin.qq.com/wiki
        data = web.input()
        echostr = data.echostr
        if self._is_from_wechat(data):
            return echostr

    def POST(self):
        str_xml = web.data()
        self._trans_msg(str_xml)
        return self._get_reply()


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
        self.msg_type = xml.findtext("MsgType")
        self.from_user_name = xml.findtext("FromUserName")
        self.to_user_name = xml.findtext("ToUserName")
        self.content = xml.findtext("Content")
        self.msg_id = xml.findtext("MsgId")
        self.event = xml.findtext("Event")
        self.event_key = xml.findtext("EventKey")

    def _get_reply(self):
        logging.debug(self.msg_type)
        reply_content = "I don't know what you are talking about :("
        if self.msg_type == "event":
            if self.event == "subscribe":
                #funs follow
                reply_content = self.help_reply
            elif self.event == "CLICK":
                if self.event_key == "HELP":
                    reply_content = self.help_reply
                elif self.event_key == "SHOW_LIST":
                    apps = playstoredata.get_all_uniqname()
                    reply_content = (
                        "Here are all apps in the list.\n"
                        "I will let you know when they are on sale.\n"
                        "--------\n" 
                        +
                        ("\n-------\n".join(apps))
                    )
                elif self.event_key == "TEST":
                    reply_content = (
                        "你可以尝试复制该信息并回复。\n"
                        "com.mojang.minecraftpe"
                    )
        elif self.msg_type == "text":
            p = re.compile(r"\w+\.\w+\.\w+\.?\w*")
            match = p.search(self.content)
            if match:
                app_uniq_name = match.group(0)
                app_detail = playstoredata.get_app_detail(app_uniq_name)
                if (app_detail is None) or (app_detail["uniq_name"] is None):
                    reply_content = "No such app"
                else:
                    reply_content = (
                        "{0} \n{1} \n${2}\n"
                        "This app is already in watch list."
                        "I will notice you when it is on sale."
                    ).format(
                        app_uniq_name,
                        app_detail["name"],
                        str(app_detail["price"])
                    )
            else:
                reply_content = "No such app"
        logging.debug(reply_content)
        return self.render.reply_text(
            self.from_user_name,
            self.to_user_name,
            int(time.time()),
            reply_content
        )

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
