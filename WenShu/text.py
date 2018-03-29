# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlencode

from scrapy import FormRequest

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
start_urls = ['http://wenshu.court.gov.cn/Index/GetAllCountRefresh?refresh=Refresh']
AA = FormRequest(url=start_urls[0], headers=header)
AA.copy()
print(AA.__dict__)