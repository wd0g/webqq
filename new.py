from lib.api import Api
import  time


class Run:
    # 全局配置
    config = {
        'qrcode_image_url':'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4',
        'qrcode_image_path':'QRCode.png',
        'aid':501004106,
        'clientid':53999199,
        'headers':{
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) "
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',}
             }

    user_some_info      = {}            # 协议需要的一些用户信息
    login_status        = {}            # 登录状态
    self_info           = {}            # 当前用户的信息

    def login(self):
        # >>1 获取二维码,并输出
        self.Api = Api(self.config)
        self.Api.show_qrcode_image()

        # >>2 检测登录情况,登录成功则返回url
        vfwebqq_url = self.check_login_status()

        # >>3 获取一些协议需要的信息
        self.user_some_info['vfwebqq'] = self.Api.get_vfwebqq(vfwebqq_url)
        self.user_some_info['uin'], self.user_some_info['vfwebqq'], self.user_some_info['psessionid'] = self.Api.get_some_info()

        # >>4 获取用户信息
        self.self_info = self.Api.get_self_info()

    #检查登录是否登录状态
    #>>>二维码失效:      执行login方法
    #>>>登录成功:        返回跳转URL

    def check_login_status(self):
        login_info = self.Api.check_qrcode_is_online()
        is_login = False

        if login_info != self.login_status:
            self.login_status = login_info
            print(login_info['tips'])

        if login_info['code'] == 3:
            is_login = True
            self.login_status = login_info
            return login_info['url']

        if is_login == False:
            time.sleep(1.5)
            return self.check_login_status()

test = Run()
test.login()