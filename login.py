import requests
import time
import re
import json
from PIL import Image
from qr import *

class LoginLib:
    imgUrl  = "https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4" #二维码图片地址
    _headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',
    }
    qrsig   = '' # 二维码检查token
    brower  = requests.session()
    imgPath = ''

    """需要的参数"""
    ptwebqq = ''
    clientid = 53999199
    vfwebqq = ''
    psessionid = ''
    uin = ''

    def __init__(self):
        self.brower.get('http://w.qq.com/', headers = self._headers)
        self.imgPath = "QRCode.png"
        imgData = self.getLoginImg()
        self.putQRCode(imgData)
        self.qrlogin_submit()

    # URL参数名:ptqrtoken
    # 通过解密cookie中的qrsig得到值
    @staticmethod
    def hash33(t):
        e, i = 0, 0
        n = len(t)
        for i in range(0,n):
            e += (e << 5) + ord(t[i])
        return 2147483647 & e

    @staticmethod
    def hash2(uin, ptwebqq):
        """
        计算hash，貌似TX的这个算法会经常变化，暂时不使用
        get_group_list_with_group_code 会依赖此数据
        提取自http://pub.idqqimg.com/smartqq/js/mq.js
        :param uin:
        :param ptwebqq:
        :return:
        """
        N = [0, 0, 0, 0]
        # print(N[0])
        for t in range(len(ptwebqq)):
            N[t % 4] ^= ord(ptwebqq[t])
        U = ["EC", "OK"]
        V = [0, 0, 0, 0]
        V[0] = int(uin) >> 24 & 255 ^ ord(U[0][0])
        V[1] = int(uin) >> 16 & 255 ^ ord(U[0][1])
        V[2] = int(uin) >> 8 & 255 ^ ord(U[1][0])
        V[3] = int(uin) & 255 ^ ord(U[1][1])
        U = [0, 0, 0, 0, 0, 0, 0, 0]
        for T in range(8):
            if T % 2 == 0:
                U[T] = N[T >> 1]
            else:
                U[T] = V[T >> 1]
        N = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
        V = ""
        for T in range(len(U)):
            V += N[U[T] >> 4 & 15]
            V += N[U[T] & 15]
        return V

    # 获取登录二维码,并取出检测token
    def getLoginImg(self):
        # >>1 将图片内容保存到变量中
        tmpS = self.brower.get(self.imgUrl, headers = self._headers)
        imgData = tmpS.content

        # >>2 获取cookie中的qrsig,用作二维码存活检查
        self.qrsig = self.hash33(tmpS.cookies['qrsig'])

        return imgData

    # 输出文本二维码
    def putQRCode(self, imgData):
        imgFile = open(self.imgPath,'wb')
        imgFile.write(imgData)
        imgFile.close()
        QRImage(self.imgPath)

    # 检查二维码是否失效
    def qrlogin_submit(self):
        url = "https://ssl.ptlogin2.qq.com/ptqrlogin?"
        payload = {
            'ptqrtoken': self.qrsig,
            'webqq_type':10,
            'remember_uin':1,
            'login2qq':1,
            'aid':501004106,
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
        response = self.brower.get(url, params = payload, headers = self._headers)
        if response.text.find('二维码已失效') != -1:
            print('二维码已失效,正在重新获取二维码...')
        elif response.text.find('二维码认证中') != -1:
            print('二维码认证中...')
        elif response.text.find('登录成功') != -1:
            successData = re.findall("'(.*?)'",response.text)
            print('正在登录...')
            self.login(successData[2])
            return
        else:
            print('请扫描二维码.')

        time.sleep(2)
        self.qrlogin_submit()

    def login2(self):
        url = "http://d1.web2.qq.com/channel/login2"
        payload = {'r':'{"ptwebqq":"%s","clientid":%s,"":"","status":"online"}' %(self.ptwebqq, self.clientid)}
        response = self.brower.post(url, data = payload)
        result = json.loads(response)

        self.uin = result['uin']
        self.vfwebqq = result['vfwebqq']
        self.psessionid = result['psessionid']

    # 完整登录
    def login(self, pUrl):
        #>>1 获取ptwebqq
        self.brower.get(pUrl, headers = self._headers)
        self.ptwebqq = self.brower.cookies['ptwebqq']

        #>>2 获取vfwebqq
        vUrl = "http://s.web2.qq.com/api/getvfwebqq?ptwebqq=%s&clientid=%s" %(self.ptwebqq, self.clientid)
        response = self.brower.get(vUrl, headers = self._headers)
        result = json.loads(response.text)
        self.vfwebqq = result['result']['vfwebqq']

        #>>3 获取个人信息
        self.get_self_info()

    # 获取个人信息
    def get_self_info(self):
        url = 'http://s.web2.qq.com/api/get_self_info2'
        response = self.brower.get(url, headers = self._headers)
        result = json.loads(response.text)['result']
        self.self_info = result

    # 获取讨论组信息
    def get_discus_list(self):
        url = 'http://s.web2.qq.com/api/get_discus_list'
        payload = {'clientid':self.clientid,'psessionid':self.psessionid,'vfwebqq':self.vfwebqq}
        response = self.brower.get(url, params = payload, headers = self._headers)
        result = json.loads(response.text)['result']
        self.discus_list = result

    # 获取好友信息[分组,好友,备注,会员...]
    def get_user_friends(self):
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        payload = {'r':'{"vfwebqq":"%s","hash":"%s"}' %(self.vfwebqq,self.hash2(self.self_info['uin'],self.ptwebqq))}
        response = self.brower.get(url, params = payload, headers = self._headers)
        result = json.loads(response.text)['result']
        self.user_friends_info = result

    # 获取我的群信息(群成员信息除外)
    def get_group_name_list(self):
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        payload = {'r':'{"vfwebqq":"%s","hash":"%s"}' %(self.vfwebqq,self.hash2(self.self_info['uin'],self.ptwebqq))}
        response = self.brower.post(url, params = payload, headers=self._headers)
        result = json.loads(response.text)['result']['gnamelist']
        self.group_name_list = result
        print(result)

    # 获取最近联系人
    def get_recent_list2(self):
        url = 'http://d1.web2.qq.com/channel/get_recent_list2'
        payload = {'r':'{"vfwebqq":"%s","clientid":%d,"psessionid":"%s"}' %(self.vfwebqq, self.clientid, self.psessionid)}
        response = self.brower.get(url, headers = self._headers)
        result = json.loads(response.text)['result']

    # 获取好友在线状态
    def get_online_buddies2(self):
        url = 'http://d1.web2.qq.com/channel/get_online_buddies2'
        payload = {'r':'{"vfwebqq":"%s","clientid":%d,"psessionid":"%s"}' %(self.vfwebqq, self.clientid, self.psessionid)}
        response = self.brower.get(url, headers = self._headers)
        result = json.loads(response.text)['result']

    # 获取某个好友签名
    def get_single_long_nick2(self, uin):
        url = 'http://s.web2.qq.com/api/get_single_long_nick2'
        payload = {'r':'{"vfwebqq":"%s","tuin":%d}' %(self.vfwebqq, uin)}
        response = self.brower.get(url, headers = self._headers)
        result = json.loads(response.text)['result']

    # 获取好友详细信息
    def get_friend_info2(self, uin):
        url = 'http://s.web2.qq.com/api/get_friend_info2'
        payload = {'r':'{"vfwebqq":"%s","clientid":%d,"psessionid":"%s","tuin":%d}' %(self.vfwebqq, self.clientid, self.psessionid, uin)}
        response = self.brower.get(url, headers = self._headers)
        result = json.loads(response.text)['result']



LoginLib = LoginLib()
LoginLib.get_group_name_list()