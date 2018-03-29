# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WenshuItem(scrapy.Item):
    # define the fields for your item here like:
    case_id = scrapy.Field()
    zh_id = scrapy.Field()
    title = scrapy.Field()
    court = scrapy.Field()
    case_type = scrapy.Field()
    trialround = scrapy.Field()
    trialdate = scrapy.Field()
    public_organ = scrapy.Field()
    party = scrapy.Field()
    legal_basis = scrapy.Field()
    resource_type = scrapy.Field()
    resource = scrapy.Field()
    relatefile = scrapy.Field()
    grade = scrapy.Field()
    zero_court = scrapy.Field()
    trialyear = scrapy.Field()
    wenshu_type = scrapy.Field()
    keywords = scrapy.Field()
    pubdate = scrapy.Field()
    content = scrapy.Field()
    judge_result = scrapy.Field()
    file_path = scrapy.Field()
    click_num = scrapy.Field()
    label = scrapy.Field()
    case_reason = scrapy.Field()
    relateinfo = scrapy.Field()
    legalbase = scrapy.Field()
    legalitems = scrapy.Field()
    legalcontent = scrapy.Field()
    case_html = scrapy.Field()

    def get_insert_sql(self):

        if self['court']:
            insert_sql = """
                INSERT INTO `judgements`.`wenshu`(`court`, `resource`, `title`, `case_type`, `trialdate`, `case_id`
               , `trialround`, `trialyear`, `zh_id`)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `case_id`=VALUES (`case_id`)
            """
            params = (self['court'], self['resource'], self['title'], self['case_type'], self['trialdate'], self['case_id'],
                      self['trialround'], self['trialyear'], self['zh_id'])

            return insert_sql, params


class RelatedItem(scrapy.Item):
    case_id = scrapy.Field()
    related_id = scrapy.Field()
    over_way = scrapy.Field()












