# -*- coding: utf-8 -*-

import random
from cookies_phone import cookies
from user_agents import agents
import json

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
    	print '-----------------------'
        request.headers['User-Agent'] = random.choice(agents)


class CookiesMiddleware(object):
    def process_request(self, request, spider):
    	print '-----------------------'
    	cookie = json.loads(random.choice(cookies))
        request.cookies = cookie
        print cookie
