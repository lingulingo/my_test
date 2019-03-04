import requests
import json
import re
import pymysql
import random
import traceback
from lxml import etree


headers = {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Mobile Safari/537.36'}


def get_main(word):
    url = 'https://ks.pcauto.com.cn/auto_composite.shtml?q=%s' % word
    res = requests.get(url=url, headers=headers).text
    html = etree.HTML(res)
    total_page = html.xpath('//div[@class="pcauto_page"]/a/text()')[-2]
    total_page = int(total_page)
    for i in range(1,total_page+1):
        urls = url + '&pageNo=' + str(i)
        res_main = requests.get(url=urls, headers=headers).text                 # 解析页面列表
        html_main = etree.HTML(res_main)
        title_lists = html_main.xpath('//div[@class="paragraph"]/strong/a')
        for titles in  title_lists:
            title = titles.xpath('.//text()')
            title = ''.join(title)
            artical_url = 'https:' + titles.xpath('./@href')[0]
            sort = titles.xpath('../../div[@class="paragraphInfo"]/span[1]/text()')[0]
            author = titles.xpath('../../div[@class="paragraphInfo"]/span[2]/text()')[0]
            time = titles.xpath('../../div[@class="paragraphInfo"]/span[3]/text()')[0]
            # print(title, artical_url,sort,author,time)
            parse_page(artical_url)

def parse_page(url_content):
    res = requests.get(url=url_content, headers=headers).content
    html = etree.HTML(res)
    print(url_content)
    content = html.xpath('//div[@class="artText clearfix"]//text()')
    if content == []:
        content = html.xpath('//div[@id="js_content"]//text()')
        if content == []:
            content = html.xpath('//div[@class="content"]//text()')
    content = ''.join(content).replace('\t','').replace('\n','').strip()
    # 评论数
    if 'nation' in url_content:
        url_num = 'https://cmt.pcauto.com.cn/action/topic/get_data.jsp?url=%s&callback=jsonpec9jdt18ne'% url_content
        res_nums = requests.get(url=url_num,headers=headers).text
        con = re.compile('jsonpec9jdt18ne\((.*)\)')
        res_nums = con.findall(res_nums)[0]
        res_nums = json.loads(res_nums)
        res_count = res_nums['total']                           # 实际评论数
        res_person = res_nums['commentRelNum']                  # 实际参与人数
        review_id = res_nums['id']                              # 评论id
        review(review_id)
    elif 'article' in url_content:
        res_count = res_person = 0
    else:
        res_count = res_person = 0
    print(res_count, res_person,content)


def review(id):
    url_id = 'https://cmt.pcauto.com.cn/topic/a0/r0/p1/ps30/t%s.html' % id
    res = requests.get(url=url_id, headers=headers)
    rev = res.text
    rev_html = etree.HTML(rev)
    total_pag = rev_html.xpath('//div[@class="pcauto_page"]//text()')
    try:
        total_pag = int(total_pag[-2]) + 1
    except:
        total_pag = 1
    print(total_pag)
    for x in range(1,total_pag):
        urls = 'https://cmt.pcauto.com.cn/topic/a0/r0/p%s/ps30/t%s.html' % (x, id)
        print(urls)
        rev_1 = requests.get(url=urls, headers=headers).text
        rev_html_1 = etree.HTML(rev_1)
        comment_list = rev_html_1.xpath('//ul[@id="commentTable"]//li')
        for com in comment_list:
            author = com.xpath('.//div[@class="thTB"]/span[1]/a//text()')
            if author == []:
                author = com.xpath('.//div[@class="thTB"]/span[1]/em//text()')
            print(author)




if __name__ == '__main__':
    get_main('666')

































































