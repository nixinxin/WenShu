# -*- coding: utf-8 -*-
__author__ = "nixinxin"
import execjs


def getkey(cookie):
    key = execjs.compile(open("F:\WenShu\WenShu\js\secure.js", encoding='utf-8').read()).call('getKey', cookie)
    return key


def getguid():
    guid = execjs.compile(open("F:\WenShu\WenShu\js\secure.js", encoding='utf-8').read()).call('ref', '')
    url = "http://wenshu.court.gov.cn/ValiCode/GetCode"

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"guid\"\r\n\r\n68cfdea8-a4f1-e7d6800d-0698db910b71\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)
    return guid

