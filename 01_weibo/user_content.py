# coding=utf-8
# Author:wangzy
# Date:2020-06-29
# Email:wangzycloud@163.com
# 转自https://blog.csdn.net/Asher117/article/details/82793091

import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver

def log_on(user,passwd):
    browser = None
    try:
        print(u'登陆新浪微博手机端...')
        browser = webdriver.Firefox()
        url = 'https://passport.weibo.cn/signin/login'
        browser.get(url)
        time.sleep(3)
        # 找到输入用户名的地方，并将用户名里面的内容清空
        username = browser.find_element_by_css_selector('#loginName')
        time.sleep(2)
        username.clear()
        # 输入自己的账号
        username.send_keys(user)
        # 找到输入密码的地方
        password = browser.find_element_by_css_selector('#loginPassword')
        time.sleep(2)
        # 输入自己的密码
        password.send_keys(passwd)
        # 点击登录
        browser.find_element_by_css_selector('#loginAction').click()
        ##这里给个15秒非常重要，因为在点击登录之后，新浪微博会有个九宫格验证码，如果有，通过程序执行的话会有点麻烦（可以参考崔庆才的Python书里面有解决方法），这里手动解决
        time.sleep(15)
    except:
        print('---------Error---------')
    finally:
        print('完成登陆!')
    return browser
def get_info(browser,id):
    # 获取用户信息
    # 用户的url结构为 url = 'http://weibo.cn/' + id
    # 不同用户的id结构不一样，普通用户的id形式一般为'/u/xx'(xx表示一串数字)，开v账号如人民日报是rmrb
    url = 'http://weibo.cn/' + id
    browser.get(url)
    time.sleep(3)
    # 使用BeautifulSoup解析网页的HTML
    soup = BeautifulSoup(browser.page_source, 'lxml')
    # 爬取最大页码数目
    pageSize = soup.find('div', attrs={'id': 'pagelist'})
    pageSize = pageSize.find('div').getText()
    pageSize = (pageSize.split('/')[1]).split('页')[0]
    # 爬取微博数量
    divMessage = soup.find('div', attrs={'class': 'tip2'})
    weiBoCount = divMessage.find('span').getText()
    weiBoCount = (weiBoCount.split('[')[1]).replace(']', '')
    # 爬取关注数量和粉丝数量
    a = divMessage.find_all('a')[:2]
    guanZhuCount = (a[0].getText().split('[')[1]).replace(']', '')
    fenSiCount = (a[1].getText().split('[')[1]).replace(']', '')

    print('-------------------')
    print('博文数量:', weiBoCount)
    print('关注:', guanZhuCount)
    print('粉丝:', fenSiCount)
    # 返回页码数目，爬取所有数据时需要用到这个参数
    return pageSize
def get_content(browser,pageSize):
    # 获取博文内容
    cont = []
    for i in range(1, int(pageSize)):
        # 每一页数据的url结构为
        # url = 'http://weibo.cn/' + id + ‘?page=’ + i
        url = 'https://weibo.cn/'+id+'?page=' + str(i)
        browser.get(url)
        time.sleep(1)
        # 使用BeautifulSoup解析网页的HTML
        soup = BeautifulSoup(browser.page_source, 'lxml')
        body = soup.find('body')
        divSs = body.find_all('div', attrs={'class': 'c'})[1:-2]
        # 遍历每页上捕捉到的数据，将每条数据保存在字典中
        for divs in divSs:
            div = divs.find_all('div')
            # 建立字典结构，格式化存储数据
            dic = {}
            content = None
            faBuTime = None
            laiYuan = None
            dianZan = 0
            zhuanFa = 0
            pinLun = 0
            flag = None

            # flag表示是否原创，这里有三种情况，两种为原创，一种为转发
            if (len(div) == 2):  # 原创，有图
                flag = '原创'
                # 爬取微博内容
                content = div[0].find('span', attrs={'class': 'ctt'}).getText()
                aa = div[1].find_all('a')
                for a in aa:
                    text = a.getText()
                    if (('赞' in text) or ('转发' in text) or ('评论' in text)):
                        # 爬取点赞数
                        if ('赞' in text):
                            dianZan = (text.split('[')[1]).replace(']', '')
                        # 爬取转发数
                        elif ('转发' in text):
                            zhuanFa = (text.split('[')[1]).replace(']', '')
                        # 爬取评论数目
                        elif ('评论' in text):
                            pinLun = (text.split('[')[1]).replace(']', '')
                            # 爬取微博来源和时间
                span = divs.find('span', attrs={'class': 'ct'}).getText()
                faBuTime = str(span.split('来自')[0])
                if len(span.split('来自')) == 1:
                    laiYuan = ' '
                else:
                    laiYuan = span.split('来自')[1]
            elif (len(div) == 1):  # 原创，无图
                flag = '原创 无图'
                content = div[0].find('span', attrs={'class': 'ctt'}).getText()
                aa = div[0].find_all('a')
                for a in aa:
                    text = a.getText()
                    if (('赞' in text) or ('转发' in text) or ('评论' in text)):
                        if ('赞' in text):
                            if len(text.split('[')) <= 1:
                                break
                            dianZan = (text.split('[')[1]).replace(']', '')
                        elif ('转发' in text):
                            zhuanFa = (text.split('[')[1]).replace(']', '')
                        elif ('评论' in text):
                            pinLun = (text.split('[')[1]).replace(']', '')
                span = divs.find('span', attrs={'class': 'ct'}).getText()
                faBuTime = str(span.split('来自')[0])
                if len(span.split('来自')) == 1:
                    laiYuan = ' '
                else:
                    laiYuan = span.split('来自')[1]
            elif (len(div) == 3):  # 转发的微博
                flag = '转发'
                content = div[0].find('span', attrs={'class': 'ctt'}).getText()
                aa = div[2].find_all('a')
                for a in aa:
                    text = a.getText()
                    if (('赞' in text) or ('转发' in text) or ('评论' in text)):
                        if ('赞' in text):
                            if len(text.split('[')) <= 1:
                                break
                            dianZan = (text.split('[')[1]).replace(']', '')
                        elif ('转发' in text):
                            zhuanFa = (text.split('[')[1]).replace(']', '')
                        elif ('评论' in text):
                            pinLun = (text.split('[')[1]).replace(']', '')
                span = divs.find('span', attrs={'class': 'ct'}).getText()
                faBuTime = str(span.split('来自')[0])
                if len(span.split('来自')) == 1:
                    laiYuan = ' '
                else:
                    laiYuan = span.split('来自')[1]

            # 将获取到的数据进行保存
            dic['标题'] = content
            dic['时间'] = faBuTime
            dic['来源'] = laiYuan
            dic['转发'] = zhuanFa
            dic['评论'] = pinLun
            dic['赞'] = dianZan
            dic['flag'] = flag
            cont.append(dic)
        time.sleep(2)
    return cont
def save(content,out_path):
    # 显示一下获取到的内容
    for item in content:
        print(item)
    # 保存内容至csv
    names={'标题':'标题', '时间':'时间', '来源':'来源','转发':'转发', '评论':'评论', '赞':'赞', 'flag':'flag'}
    save_file = open(out_path,'w',encoding='utf_8_sig',newline='')
    writer = csv.DictWriter(save_file,fieldnames=names,dialect='excel')
    writer.writeheader()
    for row in content:
        writer.writerow(row)
    save_file.close()

if __name__ == '__main__':
    # 登录账户，用自己的账号进行登录
    user = 'xxx'
    password = 'xxx'

    # 要爬取的用户id
    # 用户id不是用户昵称，在用户主页的链接上看
    # 如：岳云鹏，id=‘u/6260348034’
    # https://weibo.cn/u/1751675285
    id = 'u/1751675285'

    browser = log_on(user,password)
    pageSize = get_info(browser,id)
    content = get_content(browser,5)

    save_file = './yueYue.csv'
    save(content,save_file)