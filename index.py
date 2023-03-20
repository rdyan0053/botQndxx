import requests
import json
import time
import hmac
import base64
import urllib
import hashlib


def get_latest_lesson(s, laravel_session):
    url = "https://service.jiangsugqt.org/api/cjdList"  # 江苏省青年大学习成绩单接口
    # 参数
    params = {
        "page": "1",
        "limit": "20"
    }
    # 构造请求头
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; 22127RK46C Build/TKQ1.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5015 MMWEBSDK/20230202 MMWEBID/3840 MicroMessenger/8.0.33.2320(0x2800213D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        'Cookie': "laravel_session=" + laravel_session
    }
    res = s.post(url=url, headers=headers, params=params)  # 发送请求
    res = res.json()  # 返回结果转json
    if res["status"] == 1 and res["message"] == "操作成功":
        return res["data"][0]
    else:
        return None


def learn_lesson(s, laravel_session, lesson_id):
    url = "https://service.jiangsugqt.org/api/doLesson"  # 江苏省青年大学习接口
    # 参数
    params = {
        "lesson_id": lesson_id
    }
    # 构造请求头
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; 22127RK46C Build/TKQ1.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5015 MMWEBSDK/20230202 MMWEBID/3840 MicroMessenger/8.0.33.2320(0x2800213D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        'Cookie': "laravel_session=" + laravel_session
    }
    res = s.post(url=url, headers=headers, params=params, verify=False)  # 发送请求
    res = res.json()  # 返回结果转json
    print("%s: %s" % (lesson_id, res))
    if res["status"] == 1 and res["message"] == "操作成功":
        pass
    else:
        print("学习失败")
        dingding("学习失败")


# 钉钉提醒
def dingding(msg):
    timestamp = str(round(time.time() * 1000))
    secret = 'xxx'  # 加签
    # https://oapi.dingtalk.com/robot/send?access_token=xxx
    token = 'xxx'  # 链接里等号后面的值
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    # print(timestamp)
    # print(sign)
    # 请求的URL，WebHook地址
    webhook = f"https://oapi.dingtalk.com/robot/send?access_token={token}&timestamp={timestamp}&sign={sign}"

    # 构建请求头部
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}

    # 生成dingding消息
    message = {
        "msgtype": "text",
        "text": {"content": msg},
        "at": {
            # @ 所有人
            "isAtAll": True
        }
    }
    message_json = json.dumps(message)
    info = requests.post(url=webhook, data=message_json, headers=header, verify=False)  # 打印返回的结果
    print(info.text)


def main(laravel_session):
    s = requests.session()  # 创建会话
    latest_lesson = get_latest_lesson(s, laravel_session)
    if laravel_session == None:
        print("无法查询成绩单，请检查 Cookie 是否正确")
        dingding("无法查询成绩单，请检查 Cookie 是否正确")
        return
    if latest_lesson["has_learn"] == '1':
        print("本周的 %s 已经学过了" % latest_lesson["title"])
        dingding("本周的 %s 已经学过了" % latest_lesson["title"])
        return

    learn_lesson(s, laravel_session, latest_lesson["id"])


def handler(event=None, context=None):
    laravel_session = "xxx"  # 自行抓包获取40位的laravel_session
    main(laravel_session)


# 本地调试，如果上传到云函数，则注释掉下面的代码
# if __name__ == '__main__':
#     handler()
