import requests
import time
import re
from PIL import Image
from qr import *

class LoginLib:
    imgUrl  = "https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4" #二维码图片地址
    qrsig   = '' # 二维码检查token
    brower  = requests.session()
    imgPath = ''

    def __init__(self):
        self.imgPath = "%d.png" %(time.time())
        imgData = self.getLoginImg()
        self.putQRCode(imgData)
        self.qrlogin_submit()

    # URL参数名:ptqrtoken
    # 通过解密cookie中的qrsig得到值
    def hash33(self, t):
        e, i = 0, 0
        n = len(t)
        for i in range(0,n):
            e += (e << 5) + ord(t[i])
        return 2147483647 & e

    # 获取登录二维码,并取出检测token
    def getLoginImg(self):
        # >>1 将图片内容保存到变量中
        tmpS = self.brower.get(self.imgUrl)
        imgData = tmpS.content

        # >>2 获取cookie中的qrsig,用作二维码存活检查
        self.qrsig = self.hash33(tmpS.cookies['qrsig'])

        return imgData

    # 输出文本二维码
    def putQRCode(self, imgData):
        imgFile = open(self.imgPath,'wb')
        imgFile.write(imgData)
        imgFile.close()
        QRImg(self.imgPath)

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
        response = self.brower.get(url, params = payload)
        if response.text.find('二维码已失效') != -1:
            print('二维码已失效,正在重新获取二维码...')
        elif response.text.find('二维码认证中') != -1:
            print('二维码认证中...')
        elif response.text.find('登录成功') != -1:
            successData = re.findall("'(.*?)'",response.text)
            print('正在登录...')
            self.loginWeb(successData[2])
            return
        else:
            print('请扫描二维码.')

        time.sleep(2)
        self.qrlogin_submit()

    def loginWeb(self, url):
        response = self.brower.get(url)
        response = self.brower.get('http://s.web2.qq.com/api/get_self_info2?t=1488914269316')
        print(response.text)

LoginLib = LoginLib()