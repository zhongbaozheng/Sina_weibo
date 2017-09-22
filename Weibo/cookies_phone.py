# coding:utf-8

import requests
import json
import logging
from accounts import MyAccounts

headers = {
    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=',
    'Origin': 'https://passport.weibo.cn',
    'Host': 'passport.weibo.cn'
}


logger = logging.getLogger(__name__)


login_url = 'https://passport.weibo.cn/sso/login'

def get_cookie(account, password):
    formdata = {
        'username': account,
        'password': password,
        'savestate': '1',
        'r': 'http://weibo.cn/',
        'ec': '0',
        'pagerefer': '',
        'entry': 'mweibo',
        'wentry': '',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'qq': '',
        'mainpageflag': '1',
        'hff': '',
        'hfp': '',
    }

    session = requests.Session()
    r = session.post(login_url, data=formdata, headers=headers)
    if r.status_code == 200:
        logger.warning('Succeed to get cookie of account(%s).' % account)
        return json.dumps(r.cookies.get_dict())
    else:
        logger.warning('Failed to get cookie of account(%s).Status_code:%d.' % (account, r.status_code))
        return None


def get_Cookies(Accounts):
    cookies = []
    for account in Accounts:
        cookie = get_cookie(account, Accounts[account])
        if cookie:
            cookies.append(cookie)
    return cookies


cookies = get_Cookies(MyAccounts)
logger.warning('Finished to get cookies. Num:%d.' % len(cookies))
    

    
    
    
    

    