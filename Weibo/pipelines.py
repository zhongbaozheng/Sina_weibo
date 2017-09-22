# -*- coding: utf-8 -*-

from items import InfoItem, WeiboItem, FollowItem, FansItem
import mysql.connector

cnx = mysql.connector.connect(user='root', password='xxx', database='sina_weibo', 
	host='localhost')
cur = cnx.cursor()


class WeiboPipeline(object):
    def process_item(self, item, spider):
    	sql = None
    	value = None
        if isinstance(item, InfoItem):
        	sql = "insert into t_user_info values(0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        	value = (
        		item['user_id'],
        		item['nickname'],
        		item['area'],
        		item['gender'],
        		item['birthday'],
        		item['num_weibo'],
        		item['num_follow'],
        		item['num_fans'],
        		item['synopsis'],
        		item['authentication'],
        		item['url'])
        elif isinstance(item, WeiboItem):
        	sql = "insert into t_weibo values(0,%s,%s,%s,%s,%s,%s,%s)"
        	value = (
        		item['user_id'],
        		item['content'],
        		item['num_attitude'],
        		item['num_repost'],
        		item['num_comment'],
        		item['pub_time'],
        		item['pub_tool'])
        elif isinstance(item, FollowItem):
        	sql = "insert into t_user_follow values(0,%s,%s)"
        	value = (item['user_id'], str(item['fList']))
        else:
        	sql = "insert into t_user_fans values(0,%s,%s)"
        	value = (item['user_id'], str(item['fList']))

        try:
    		cur.execute(sql, value)
    		cnx.commit()
    	except Exception as why:
    		print(why)
    		cnx.rollback()

