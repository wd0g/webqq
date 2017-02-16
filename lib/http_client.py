import requests
import json

class Brower:
    session = requests.session()

    def get(self,*args):
        url, params, headers = '','',''

        argsLen = len(args)
        if argsLen == 1:
            url = args[0]
        elif argsLen == 2:
            url = args[0]
            params = args[1]
        elif argsLen == 3:
            url = args[0]
            params = args[1]
            headers = args[2]

        result = self.request(url, params, headers, 0)

        try:
            jsonList = json.loads(result.text)
        except:
            jsonList = False

        return jsonList

    def post(self,*args):
        url, params, headers = '','',''
        argsLen = len(args)
        if argsLen == 1:
            url = args[0]
        elif argsLen == 2:
            url = args[0]
            params = args[1]
        elif argsLen == 3:
            url = args[0]
            params = args[1]
            headers = args[2]

        result = self.request(url, params, headers, 1)

        try:
            jsonList = json.loads(result.text)
        except:
            jsonList = False

        return jsonList

    def request(self, url, params, headers, type):
        if type == 0:
            result = self.session.get(url, params=params, headers=headers)
        elif type == 1:
            result = self.session.post(url, data=params, headers=headers)

        return result


