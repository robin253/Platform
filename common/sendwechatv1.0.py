#!/usr/bin/python
#coding=utf-8

import urllib,urllib2
import json
import sys
import chardet
#import redis 可以将token放在redis缓存里 避免每次都去微信请求

#WeChat类 注意类的写法 三个输入参数
class WeChat():
    def __init__(self):
        # corpid = "wxe65349952d43c58f"
        # secret = "ltvEnOhBaC7ODXs_Kc2mqmZB0anTG_uMygD-DglptDP7TwxRkpl4GA6cBNLb7ZLv"
        self.agentid = "1000002"
        corpid = "wxf237ac7f3faacce7"
        secret = "FmN6HGl-QzFbOudtnm_MfotmXQxsNXMm8eJWTKC_iFw"


        self.gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid='+corpid+'&corpsecret='+secret

    def send_messages(self,content):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        try:
            tokenresponse = urllib2.urlopen(self.gettoken_url)
        except  urllib2.HTTPError,e:
            print "获取token错误",e
            pass#打印日
        token_json = tokenresponse.read().decode('utf-8')   #this is json type
        token_dict = json.loads(token_json)     #change to python dict
        token = token_dict['access_token']
        message = {
                "touser":"@all", #所有用户
                #"totag":"1",       #标签ID  1
                "msgtype":"text",
                "agentid":self.agentid,  #持久化数据订正平台3      账务4  网关1
                "text":{"content":content},
                "safe":"0"
                }


        post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token+"&agentid="+self.agentid

        message_json = json.dumps(message, ensure_ascii=False,encoding='utf-8') #change to json type
        request = urllib2.Request(post_url, message_json)
        try:
            wechatresponse = urllib2.urlopen(request)
        except urllib2.HTTPError,e:
            print "发送信息失败"
            print e
            pass#打印日志
        msg_json = wechatresponse.read().decode('utf-8')  #this is json type
        msg_dict = json.loads(msg_json)     #change to python dict
        print msg_json
        return msg_dict

if __name__ == '__main__':
    wechat_sender = WeChat()#初始化对象
    content="muamua+++++++++++++++++++++++++++"
    #print type(content) #<type 'str'>
    #print chardet.detect(content)['encoding']#utf-8
    msg_dict=wechat_sender.send_messages(content)#调用方法发送信息 并返回信息
    #print msg_dict
    if msg_dict['errcode']!=0:
        print 'error'
        pass#打印日志



