
import re
from lib.qr import *
from lib.http_client import Brower
from lib.func import Func
class Api:
    brower = Brower()
    config = []         #全局配置
    func = Func()

    def __init__(self, config):
        self.config = config

    # 获取Brower中的cookie
    def get_cookie(self, name):
        try:
            cookie = self.brower.session.cookies[name]
        except:
            cookie = ''
        return cookie

    # 获取并显示二维码图片
    def show_qrcode_image(self):
        imgData = self.brower.request(self.config['qrcode_image_url'],'','',0).content
        imgFile = open(self.config['qrcode_image_path'],'wb')
        imgFile.write(imgData)
        imgFile.close()

        QRImage(self.config['qrcode_image_path'])

    # 检查二维码状态
    def check_qrcode_is_online(self):
        url = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
        params = {
            'ptqrtoken': self.func.hash33(self.get_cookie('qrsig')),
            'webqq_type':10,
            'remember_uin':1,
            'login2qq':1,
            'aid':self.config['aid'],
            'u1':'http://w.qq.com/proxy.html?login2qq=1&webqq_type=10',
            'ptredirect':0,
            'ptlang':2052,
            'daid':164,
            'from_ui':1,
            'pttype':1,
            'dumy':'',
            'fp':'loginerroralert',
            'action':'0-0-130457',
            'mibao_css':'m_webqq',
            't':1,
            'g':1,
            'js_type':0,
            'js_ver':10194,
            'login_sig':'',
            'pt_randsalt':2,
        }
        response = self.brower.request(url, params, self.config['headers'], 0)
        result = False
        if response.text.find('二维码未失效') != -1:
            result = {'code':0,'tips':'等待扫描'}
        if response.text.find('二维码已失效') != -1:
            result = {'code':1,'tips':'二维码已失效'}
        if response.text.find('二维码认证中') != -1:
            result = {'code':2,'tips':'二维码认证中'}
        if response.text.find('登录成功') != -1:
            result = {'code':3,'tips':'登录成功','url':re.findall("'(.*?)'",response.text)[2]}
        return result

    # 获取vfwebqq
    def get_vfwebqq(self, url):
        #>>1 访问ptwebqq页面
        self.brower.request(url, '', self.config['headers'], 0)

        #>>2 访问vfwebqq页面
        params = {'ptwebqq':self.get_cookie('ptwebqq'),'clientid':self.config['clientid']}
        vfwebqq = self.brower.get('http://s.web2.qq.com/api/getvfwebqq',params,self.config['headers'])['result']['vfwebqq']
        return vfwebqq

    # 获取uin,vfwebqq,psessionid
    def get_some_info(self):
        url = "http://d1.web2.qq.com/channel/login2"
        payload = {'r':'{"ptwebqq":"%s","clientid":%s,"":"","status":"online"}' %(self.get_cookie('ptwebqq'), self.config['clientid'])}
        result = self.brower.post(url, payload, self.config['headers'])['result']

        return result['uin'], result['vfwebqq'], result['psessionid']

    # 获取个人信息
    def get_self_info(self):
        url = 'http://s.web2.qq.com/api/get_self_info2'
        result = self.brower.get(url,'',self.config['headers'])['result']
        return result



