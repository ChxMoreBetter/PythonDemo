import requests
import re
import csv
import time
import os
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}
params = {
    'offset': 0
}
list_time_sleep = 20
detail_time_sleep = 10

def get_html(url):
    '''
    获取一页html页面
    :param page: 页数
    :return: 该页html页面
    '''
    # params['offset'] = page * 10
    if not url:
        return 'url 无效'

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            return html
        else:
            return -1
    except:
        if 'antispider' in requests.url or '请输入验证码' in requests.text:
            return '触发反爬虫机制'


def get_news_list(url,news_list):
    # url = 'https://weixin.sogou.com/weixin?query=疫苗&type=2&page=1&ie=utf8&p=75351221&dp=1'
    html = get_html(url)
    # print('重新请求========'+html)
    soup = BeautifulSoup(html,features='lxml')
    title_arr = soup.select('a[data-share]')
    author_arr = soup.select('a[data-isV]')
    time_arr =soup.select('div[t]')
    content_arr = soup.find_all('p',class_ = 'txt-info')
    img_arr = soup.select('a[data-z]')
    # print(img_arr)

    # for title in title_arr:
    #     print(title.text)
    # for content in content_arr:
    #     print(content.text)

    count = len(title_arr)
    for i in range(count):
        data = {}
        title = str(title_arr[i].text)
        # print('标题:'+ str(title_arr[i].text))

        author = str(author_arr[i].text)
        # print('公众号:'+ str(author_arr[i].text))

        subtitle = str(content_arr[i].text)
        # print('摘要:'+ str(content_arr[i].text))

        timestamp = str(time_arr[i]['t'])
        date = time.localtime(float(str(time_arr[i]['t'])))
        dt = time.strftime("%Y-%m-%d %H:%M:%S", date)
        # print('时间:'+  str(dt))

        link_url = str(title_arr[i]['data-share'])
        # print('link:'+ str(title_arr[i]['data-share']))

        # img_link = img_arr[i].find('img')['src']
        # img_url = str(img_link).split('url=')[1]
        # print(img_url)

        data['title'] = title
        data['time']  = timestamp
        data['subtitle'] = subtitle
        data['link'] = link_url
        data['author'] = author
        # data['coverImg'] = img_url

        news_list.append(data)
    return news_list

def saveJsonData(data):
    file = open('test.json', 'a', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False,indent=4)
    file.write(',')
    file.close()

def getNewsDetail(link_url):
    news_detail_html = get_html(link_url)
    news_detail_soup = BeautifulSoup(news_detail_html, features='lxml')
    content = news_detail_soup.find('div', class_='rich_media_content')
    # print('内容:'+str(content))
    if not content:
        return '暂无内容'
    return content

def uploadImgToSever(img_url):
    return ''
    r = requests.get(img_url)
    img_name =  'upload.png'
    with open(img_name, 'wb') as f:
        f.write(r.content)

    HOST = ''
    url = ''
    token = ''
    files = {'attachment': (img_name, open(img_name, 'rb'), 'image/png', {})}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Authorization': token
    }
    response = requests.request('POST', HOST + url, files=files, headers=headers)
    # print( type(response.text),response.text)
    if response.status_code == 200:
        data = json.loads(response.text)
        print(data)
        if str(data['url']):
           return data['url']

    return img_url



if __name__ == "__main__":

    print('开始获取列表页')
    for i in range(1,2):
        print('获取网页列表 第'+str(i)+'次')
        url = 'https://weixin.sogou.com/weixin?query=疫苗&type=2&page={}&ie=utf8&p=75351221&dp=1'
        url = url.format(i)
        news_list = []
        get_news_list(url,news_list)
        print('延时1分钟执行列表抓取 第'+str(i)+'次')
        time.sleep(list_time_sleep)
        print(url)
        print('开始获取资讯内容')
        count = 0
        for news in news_list:
            print(news['title']+': 开始获取')
            link = news['link']
            content = getNewsDetail(link)
            content_img_urls = content.select('div[data-src]')
            content_img_urls = content.select('img')
            original_content = str(content)
            for img in content_img_urls:
                # print(img['data-src'])
                original_url = str(img['data-src'])
                upload_url = uploadImgToSever(original_url)
                if upload_url != original_url:
                    original_content = original_content.replace(original_url,upload_url)
                    original_content = original_content.replace('data-src','src')

            # print(content_img_urls)

            news['content'] = str(original_content)

            #json 格式存储信息
            saveJsonData(news)
            time.sleep(detail_time_sleep)
            count += 1
    print('抓取完毕')
    #1556439087




