# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    user_id = scrapy.Field()
    nickname = scrapy.Field()
    area = scrapy.Field()
    gender = scrapy.Field()
    birthday = scrapy.Field()
    num_weibo = scrapy.Field()
    num_follow = scrapy.Field()
    num_fans = scrapy.Field()
    synopsis = scrapy.Field()			#简介
    authentication = scrapy.Field()		#认证
    url = scrapy.Field()


class WeiboItem(scrapy.Item):
	user_id = scrapy.Field()
	content = scrapy.Field()
	num_attitude = scrapy.Field()
	num_repost = scrapy.Field()
	num_comment = scrapy.Field()
	pub_time = scrapy.Field()
	pub_tool = scrapy.Field()
	#pub_place = scrapy.Field()


class FollowItem(scrapy.Item):
	user_id = scrapy.Field()
	fList = scrapy.Field()


class FansItem(scrapy.Item):
	user_id = scrapy.Field()
	fList = scrapy.Field()
