# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class WenshuPipeline(object):
    def process_item(self, item, spider):
        if 'over_way' in item:
            print("related", item)
        if 'court' in item:
            print("info", item)
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DB'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        if 'over_way' in item:
            print("related", item)
        if 'court' in item:
            # 使用twisted将mysql插入变成异步执行
            query = self.dbpool.runInteraction(self.do_insert, item)
            query.addErrback(self.hand_error)
            return item

    def hand_error(self, failure):
        print("error", failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        result = cursor.execute(insert_sql, params)
        print(result, item['title'])
