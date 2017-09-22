#coding:utf-8


import scrapy
from scrapy.http import Request
from Weibo.items import InfoItem, WeiboItem, FollowItem, FansItem
from bs4 import BeautifulSoup
import re
import mysql.connector
import time

import random
from Weibo.cookies_phone import cookies
import json


def get_rnd_cookie():
	return json.loads(random.choice(cookies))



class Spider(scrapy.Spider):
	name = 'weibo_spider'
	allowed_domain = 'weibo.cn'
	url_main = 'https://weibo.cn/'
	start_users = [1266321801, 1790596553, 1197161814, 1196235387, 1266286555, 1239246050, 3099016097,
	1299532580, 1914100420, 6027167937, 1608574203, 1746274673, 1496852380, 3125046087, 1188552450,
	1254745922, 1793285524, 1497983190, 1740856600, 1730336902, 2134671703, 1905077071, 2144684673,
	1854627907, 1764222885, 1263498570, 1568006292, 1191220232, 1195230310, 2865101843, 1191262305]

	def __init__(self, name=None, **kwargs):
		if name is not None:
			self.name = name
		elif not getattr(self, 'name', None):
			raise ValueError("%s must have a name" % type(self).__name__)
		self.__dict__.update(kwargs)
		if not hasattr(self, 'start_urls'):
			self.start_urls = []
		self.cnx = mysql.connector.connect(user='root', password='xxx', database='sina_weibo', host='localhost')
		self.cur =self.cnx.cursor()

	def start_requests(self):
		for _id in self.start_users:
			_id = str(_id)
			if not self.select_id(_id):	#判断是否爬过
				for request in self.process_id(_id):
					yield request

	def process_id(self, _id):
		url_home = self.url_main + _id
		url_weibo = url_home + '?filter=1&page=1'
		url_follow = self.url_main + _id + '/follow'
		url_fans = self.url_main + _id + '/fans'

		followItem = FollowItem()
		followItem['user_id'] = _id
		followItem['fList'] = []
		fansItem = FansItem()
		fansItem['user_id'] = _id
		fansItem['fList'] = []

		Requests = []
		Requests.append(Request(url_home, callback=self.get_info1, meta={'user_id': _id}, cookies=get_rnd_cookie()))
		Requests.append(Request(url_weibo, callback=self.get_weibo, meta={'user_id': _id}, cookies=get_rnd_cookie()))
		Requests.append(Request(url_follow, callback=self.get_follow_fans, meta={'item': followItem}, cookies=get_rnd_cookie()))
		Requests.append(Request(url_fans, callback=self.get_follow_fans, meta={'item': fansItem}, cookies=get_rnd_cookie()))
		self.insert_id(_id)

		return Requests


	def get_info1(self, response):
		item = InfoItem()
		item['url'] = response.url
		item['user_id'] = response.meta['user_id']

		re_weibo = re.compile(u'微博\[(\d+)\]')
		re_follow = re.compile(u'关注\[(\d+)\]')
		re_fans = re.compile(u'粉丝\[(\d+)\]')

		soup = BeautifulSoup(response.text, 'lxml')
		tag_weibo = soup.find('span', text=re_weibo)
		if tag_weibo:
			item['num_weibo'] = re.match(re_weibo, unicode(tag_weibo.get_text())).group(1)
		tag_follow = soup.find('a', text=re_follow)
		if tag_follow:
			item['num_follow'] = re.match(re_follow, unicode(tag_follow.get_text())).group(1)
		tag_fans = soup.find('a', text=re_fans)
		if tag_fans:
			item['num_fans'] = re.match(re_fans, unicode(tag_fans.get_text())).group(1)

		url_info = self.url_main + item['user_id'] + '/info'
		yield Request(url_info, callback=self.get_info2, meta={'item': item}, cookies=get_rnd_cookie())


	def get_info2(self, response):
		item = response.meta['item']
		soup = BeautifulSoup(response.text, 'lxml')
		tag_info = soup.find('div', text=u'基本信息').next_sibling
		text_info = tag_info.get_text(';')

		nickname = re.search(u'昵称[:：](.*?);', text_info)
		area = re.search(u'地区[:：](.*?);', text_info)
		gender = re.search(u'性别[:：](.*?);', text_info)
		birthday = re.search(u'生日[:：](.*?);', text_info)
		synopsis = re.search(u'简介[:：](.*?);', text_info)
		authentication = re.search(u'认证[:：](.*?);', text_info)

		item['nickname'] = nickname.group(1) if nickname else ''
		item['area'] = area.group(1) if area else ''
		item['gender'] = gender.group(1) if gender else ''
		item['birthday'] = birthday.group(1) if birthday else ''
		item['synopsis'] = synopsis.group(1) if synopsis else ''
		item['authentication'] = authentication.group(1) if authentication else ''
		yield item


	def get_weibo(self, response):
		soup = BeautifulSoup(response.text, 'lxml')
		tags = soup.find_all('div', id=re.compile('M_\w+'))
		for tag in tags:
			item = WeiboItem()
			item['user_id'] = response.meta['user_id']
			text_weibo = re.sub('\xa0+', '|', tag.get_text().replace(u'\u200B', ''))
			item['content'] = text_weibo.split('|')[0]
			item['num_attitude'] = re.search(u'赞\[(\d+)\]', text_weibo).group(1)
			item['num_repost'] = re.search(u'转发\[(\d+)\]', text_weibo).group(1)
			item['num_comment'] = re.search(u'评论\[(\d+)\]', text_weibo).group(1)

			if text_weibo.split('|')[-1].startswith(u'来自'):
				item['pub_tool'] = text_weibo.split('|')[-1].replace(u'来自', '')
				item['pub_time'] = text_weibo.split('|')[-2]
			else:
				item['pub_tool'] = ''
				item['pub_time'] = text_weibo.split('|')[-1]

			if item['pub_time'].endswith(u'分钟前'):
				minute = int(item['pub_time'].replace(u'分钟前', ''))
				item['pub_time'] = time.strftime('%m月%d日 %H:%M', time.localtime(
					time.time() - minute * 60)).decode('utf-8')
			elif item['pub_time'].startswith(u'今天'):
				item['pub_time'] = item['pub_time'].replace(u'今天', 
					time.strftime('%m月%d日', time.localtime()).decode('utf-8'))

			yield item

		tag_next = soup.find('a', text=u'下页')
		if tag_next:
			url_next = 'http://weibo.cn' + tag_next['href']
			yield Request(url_next, callback=self.get_weibo, meta={'user_id': response.meta['user_id']}, cookies=get_rnd_cookie())


	def get_follow_fans(self, response):
		item = response.meta['item']
		soup = BeautifulSoup(response.text, 'lxml')
		IDs = soup.find('input', attrs={'name': 'uidList'})['value'].strip().split(',')
		item['fList'] += IDs
		for ID in IDs:
			if not self.select_id(ID):
				for request in self.process_id(ID):
					yield request

		tag_next = soup.find('a', text=u'下页')
		if tag_next:
			url_next = 'http://weibo.cn' + tag_next['href']
			yield Request(url_next, callback=self.get_follow_fans, meta={'item': item}, cookies=get_rnd_cookie())
		else:
			yield item



	def select_id(self, _id):
		self.cur.execute("select 1 from finished_id where finished_id=%s" % _id)
		if self.cur.fetchone():
			return True
		else:
			return False

	def insert_id(self, _id):
		sql = "insert into finished_id values(%s)" % _id
		try:
			self.cur.execute(sql)
			self.cnx.commit()
		except:
			self.cnx.rollback()

