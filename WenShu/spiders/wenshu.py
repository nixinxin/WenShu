# -*- coding: utf-8 -*-
import json
import re
import time

import execjs
import os
import requests
import scrapy
from datetime import datetime

from fake_useragent import UserAgent
from scrapy import Spider

from WenShu.scrapy_redis.spiders import RedisSpider

from WenShu.items import WenshuItem, RelatedItem
from WenShu.settings import JS_CODE, BASE_DIR
from utils.crawl_xici_ip import GetIP


class WenshuSpider(RedisSpider):
    name = 'wenshu'
    redis_key = "wenshu:start_urls"

    allowed_domains = ['wenshu.court.gov.cn']
    index = ['http://wenshu.court.gov.cn/index']
    start_urls = ['http://wenshu.court.gov.cn/List/List']
    pages_url = 'http://wenshu.court.gov.cn/Index/GetAllCountRefresh?refresh=Refresh'
    list_content = "http://wenshu.court.gov.cn/List/ListContent"
    type_url = "http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++案件类型: {0}"
    getcode = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
    doc_url = "http://wenshu.court.gov.cn/CreateContentJS/CreateListDocZip.aspx?action=1"
    relate_files_url = "http://wenshu.court.gov.cn/Content/GetRelateFiles"
    getsummary_url = "http://wenshu.court.gov.cn/Content/GetSummary"
    get_html_url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}"

    types = {1: '刑事案件', 2: '民事案件', 3: '行政案件', 4: '赔偿案件', 5: '执行案件'}
    case_counts = {'刑事案件': 6178447, '民事案件': 27658556, '行政案件': 1411938, '赔偿案件': 36568, '执行案件': 8424200}
    header = {"User-Agent": getattr(UserAgent(), 'random'),
              "Accept": "*/*",
              "Accept-Encoding": "gzip, deflate",
              "Accept-Language": "zh-CN, zh;q = 0.9",
              "Connection": "keep-alive",
              "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8",
              "Host": "wenshu.court.gov.cn",
              "Origin": "http://wenshu.court.gov.cn",
              "Referer": "http://wenshu.court.gov.cn/Index",
              "X-Requested-With": "XMLHttpRequest",
              }
    pages = 0

    # custom_settings = {
    #     'JOBDIR': 'status/001',
    # }

    def start_requests(self):
        # url = "http://wenshu.court.gov.cn/Index/GetAllCountRefresh"
        # querystring = {"refresh": "Refresh"}
        # response = requests.request("POST", url, params=querystring, headers=self.header).text
        # result = json.loads(json.loads(response))[1]['CaseTypeCount']
        # for i in result:
        #     case = i['name']
        #     count = int(i['count'][0]['Count'])
        #     self.case_counts[case] = int(count / 20) + 1
        #     file_base = os.path.join(BASE_DIR, 'files', case)
        #     if not os.path.exists(file_base):
        #         os.makedirs(file_base)
        yield scrapy.FormRequest(url=self.start_urls[0], headers=self.header, callback=self.getguid_num)

    def getguid_num(self, response):
        guid = execjs.compile(open(JS_CODE, encoding='utf-8').read()).call('ref', '')
        payload = {"guid": guid}
        yield scrapy.FormRequest(url=self.getcode, formdata=payload, headers=self.header, callback=self.get_cookie,
                                 meta={"guid": guid})

    def get_cookie(self, response):
        guid = response.meta.get('guid', '')
        number = response.text
        # response = requests.request("POST", self.start_urls[0], headers=self.header, proxies=proxies).cookies
        # cookie = dict(response)['vjkl5']
        yield scrapy.FormRequest(url=self.start_urls[0], headers=self.header, callback=self.parse, dont_filter=True,
                                 meta={"guid": guid, 'number': number})

    def parse(self, response):
        for case, pages in self.case_counts.items():
            for page in range(1, int(pages / 20) + 1):
                guid = response.meta.get('guid', '')
                number = response.meta.get('number', '')
                cookies_re = re.compile('vjkl5=(.*?);')
                cookies = cookies_re.findall(str(response.headers))[0]
                cookies = self.getkey(cookies)
                content_parse = {
                    "Param": "案件类型:{0}".format(case),
                    "Index": str(page),
                    "Page": "20",
                    "Order": "法院层级",
                    "Direction": "asc",
                    "vl5x": cookies,
                    "number": number,
                    "guid": guid,
                }
                self.header['Cookies'] = "vjkl5=" + cookies
                yield scrapy.FormRequest(url=self.list_content, formdata=content_parse,
                                         headers=self.header, callback=self.detail)

    def detail(self, response):
        list_content = json.loads(json.loads(response.text))
        for info in list_content[1:]:
            items = WenshuItem()
            items['court'] = info['法院名称']
            try:
                items['resource'] = info['裁判要旨段原文']
            except:
                items['resource'] = None
            items['title'] = info['案件名称']
            items['case_type'] = self.types[int(info['案件类型'])]
            try:
                items['trialdate'] = datetime.strptime(info['裁判日期'], '%Y-%m-%d').date()
                items['trialyear'] = items['trialdate'].year
            except:
                items['trialdate'] = None
                items['trialyear'] = None

            items['case_id'] = info['文书ID']
            try:
                items['trialround'] = info['审判程序']
            except:
                items['trialround'] = None
            items['zh_id'] = info['案号'] if info['案号'] != "无" else None
            yield items

            # 其他信息
            # related_parse = {"docId": items['case_id'], "court": items['court'], "caseNumber": items['zh_id']}
            # scrapy.FormRequest(url=self.relate_files_url, formdata=related_parse,
            #                    headers=self.header, callback=self.get_relate_files,
            #                    meta={'item': items}, dont_filter=True)
            #
            # summary_parse = {"docId": items['case_id']}
            # scrapy.FormRequest(url=self.getsummary_url, formdata=summary_parse,
            #                    headers=self.header, callback=self.getsummary,
            #                    meta={'item': items}, dont_filter=True)
            #
            # scrapy.Request(url=self.get_html_url.format(items['case_id']), callback=self.get_html, dont_filter=True)

            # file_path = os.path.join(BASE_DIR, 'files', items['case_type'], "{0}.doc".format(items['title']))
            # if not os.path.exists(file_path):
            #     doc_parse = {
            #         "conditions": "searchWord 1 AJLX  案件类型:{0}".format(case),
            #         "docIds": "{0}|{1}|{2}".format(items['case_id'], items['case_id'], items['trialdate']),
            #     }
            #     yield scrapy.FormRequest(url=self.doc_url, formdata=doc_parse,
            #                              headers=self.header, callback=self.doc_down,
            #                              meta={'item': items, 'file_path': file_path}, dont_filter=True)

    def doc_down(self, response):
        file_path = response.meta.get("file_path", "")
        with open(file_path, 'wb') as f:
            f.write(response.body)

    def get_relate_files(self, response):
        relatefile = json.load(response.body)
        items = response.meta.get("items", "")
        items['relatefile'] = relatefile

        related_file_info = RelatedItem()

        related_id_re = re.compile('ID":".*?"')
        related_id_result = related_id_re.findall(response.body)[0][4:-1]
        related_file_info['related_id'] = related_id_result
        related_file_info['case_id'] = relatefile["case_id"]

        over_way_re = re.compile('结案方式":".*"')
        over_way_result = over_way_re.findall(response.body)[0].split('"')[-2]
        related_file_info['over_way'] = over_way_result

        yield related_file_info

    def getsummary(self, response):
        items = response.meta.get("items", "")
        items['relateinfo'] = response.body
        try:
            trialRound_re = re.compile("{ name:.*?}")
            trialRound_result = trialRound_re.findall(response.body)[3]
            items['trialround'] = trialRound_result.split('value: "')[1][:-3]
        except:
            pass
        try:
            legalbase_re = re.compile("《.*?》")
            legalbase_result = legalbase_re.findall(response.body)[0]
            items['legalbase'] = legalbase_result
        except:
            pass
        try:
            legalitems_re = re.compile("法条名称:'.*',")
            legalitems_result = legalitems_re.findall(response.body)[0].split("'")[1]
            items['legalitems'] = legalitems_result
        except:
            pass
        try:
            legalcontent_re = re.compile("法条内容:'.*?'}]}]}")
            legalcontent_result = legalcontent_re.findall(response.body)[0].split("'")[1]
            items['legalcontent'] = legalcontent_result
        except:
            pass

    def get_html(self, response):
        items = response.meta.get("items", "")
        case_html_re = re.compile('Html\":\".*</div>')
        case_html_result = case_html_re.findall(response.body)[0].replace('Html":"', '')
        items['case_html'] = case_html_result

        pubdate_re = re.compile('PubDate\":\".*?\"')
        pubdate_result = pubdate_re.findall(response.body)[0].split('"')[2]
        items['pubdate'] = pubdate_result

        click_num_re = re.compile('：.*?次')
        click_num_result = click_num_re.findall(response.body)[0][1:-1]
        items['click_num'] = click_num_result
        print(dict(items))
        yield items

    def getkey(self, cookie):
        key = execjs.compile(open("F:\WenShu\WenShu\js\secure.js", encoding='utf-8').read()).call('getKey', cookie)
        return key

    # def get_cookie(self, ip_port):
    #     proxies = {
    #         'http': ip_port
    #     }
    #     response = requests.request("POST", self.start_urls[0], headers=self.header, proxies=proxies).cookies
    #     cookie = dict(response)['vjkl5']
    #     return cookie

# selenium驱动浏览器
# self.brower.get(self.type_url.format(case))
# self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#resultList .dataItem")))
# html = self.brower.page_source
# print(self.brower.get_cookies())
# html = Selector(text=html)
# records = int(html.css("#span_datacount::text").extract_first(1))
# for page in range(1, int(records/5) + 1):
#     self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#resultList .dataItem")))
#     html = self.brower.page_source
#     html = Selector(text=html)
#     results = html.css("#resultList .dataItem")
#     self.brower.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     try:
#         for i in results:
#             item = WenshuItem()
#             label = i.css(".label div::text").extract()
#             label = "".join(label)
#             case_id, title, court, zh_id, trialdate = i.css("[name='ckList']::attr(value)").extract_first().split("^")
#             resource_type = i.css(".mzjg::text").extract_first("")
#             if resource_type:
#                 items['resource_type'] = resource_type.replace("【", '').replace("】", '')
#                 resource_des = i.css(".wszy::text").extract_first()
#                 items['resource_des'] = resource_des
#             else:
#                 items['resource_type'] = None
#                 items['resource_des'] = None
#             items['label'] = label
#             items['case_id'] = case_id
#             items['title'] = title
#             items['court'] = court
#             items['zh_id'] = zh_id
#             if zh_id == '无':
#                 items['zh_id'] = None
#             # items['trialdate'] = datetime.strptime(trialdate, '%Y-%m-%d').date()
#             items['trialdate'] = None
#             items['case_type'] = case
#             # items['trialyear'] = int(trialdate.split("-")[0])
#             items['trialyear'] = None
#             yield item
#
#             # related_parse = {"docId": case_id, "court": court, "caseNumber": zh_id}
#             # yield scrapy.FormRequest(url=self.relate_files_url, formdata=related_parse,
#             #                          headers=self.header, callback=self.get_relate_files,
#             #                          meta={'item': item}, dont_filter=True)
#             #
#             # summary_parse = {"docId":  "8252121f-8260-4241-b707-018d52d151ca"}
#             # yield scrapy.FormRequest(url=self.getsummary_url, formdata=summary_parse,
#             #                          headers=self.header, callback=self.getsummary,
#             #                          meta={'item': item}, dont_filter=True)
#             #
#             # yield scrapy.Request(url=self.get_html_url.format(case_id), callback=self.get_html, dont_filter=True)
#             #
#             # doc_parse = {
#             #     "conditions": "searchWord 1 AJLX  案件类型:{0}".format(case),
#             #     "docIds": "{0}|{1}|{2}".format(case_id, title, trialdate),
#             # }
#             # file_path = os.path.join(BASE_DIR, 'files', items['case_type'], "{0}.doc".format(items['title']))
#             # if not os.path.exists(file_path):
#             #     yield scrapy.FormRequest(url=self.doc_url, formdata=doc_parse,
#             #                              headers=self.header, callback=self.doc_down,
#             #                              meta={'item': item, 'file_path': file_path}, dont_filter=True)
#     except:
#         pass
#     time.sleep(1)
#     self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#resultList .dataItem")))
#     self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#pageNumber > a.next"))).click()

# 自编码模拟请求
