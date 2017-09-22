# coding:utf-8

import base64
from urllib import quote, unquote
import rsa
import binascii
import requests
import json
import re
import logging
from accounts import MyAccounts


logger = logging.getLogger(__name__)


login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'

def get_cookie(account, password):
    en_user = base64.b64encode(quote(account))
    prelogin_url = '''https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=
    sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.19)''' % en_user
    r = requests.get(prelogin_url)
    pre_data = re.search(ur'\{.+\}', r.content).group()
    pre_data = json.loads(pre_data)
    servertime = pre_data['servertime']
    nonce = pre_data['nonce']
    rsakv = pre_data['rsakv']
    pubkey = pre_data['pubkey']
    pubkey = int(pubkey, 16)
    e = int('10001', 16)
    pub = rsa.PublicKey(pubkey, e)

    en_pwd = rsa.encrypt(str(servertime) + '\t' + str(nonce) + '\n' + password, pub)
    en_pwd = binascii.b2a_hex(en_pwd)

    formdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '30',
        #'qrcode_flag': 'false',
        'useticket': '0',
        'ssosimplelogin': '1',
        'pagerefer': '',
        'vsnf': '1',
        #'vsnval': '',
        'su': en_user,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': en_pwd,
        'sr': '1440*900',
        'encoding': 'UTF-8',
        'cdult': '3',
        'domain': 'weibo.com',
        'prelt': '0',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }

    session = requests.Session()
    r1 = session.post(login_url, data=formdata)
    # print(unquote(r1.content))
    url2 = re.search('location.replace\(\"(.*?)\"\)', r1.content).group(1)
    retcode = re.search('retcode=(\d+)', unquote(url2)).group(1)
    if retcode == '0':
        logger.warning('Succeed to get cookie of account(%s).' % account)
        r2 = session.get(url2)
        # print(r2.content)
        url3 = re.search('location.replace\(\'(.*?)\'\)', r2.content).group(1)
        r3 = session.get(url3)
        # print(r3.content)
        # print(session.cookies.get_dict())
        # print(r3.cookies.get_dict())
        return json.dumps(r3.cookies.get_dict())
    else:
        reason = re.search('reason=(.+)$', unquote(url2)).group(1)
        #print(reason)
        logger.warning('Failed to get cookie of account(%s).Reason:%s.' % (account, reason))
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
    

    
    
    
    

    