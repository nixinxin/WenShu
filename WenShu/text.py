# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlencode

import execjs
import requests
import scrapy
from scrapy import FormRequest
from WenShu.settings import JS_CODE

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
start_urls = ['http://wenshu.court.gov.cn/List/List']

ip_port = "http://116.226.131.129:8060"

scrapy.FormRequest(url=start_urls[0], headers=header)
print(aa.e)