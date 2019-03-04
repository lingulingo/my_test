import requests
import json
import re
import pymysql
import random
from lxml import etree

headers = {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Mobile Safari/537.36'}
# 获取代理IP
def get_proxy():
    '''
    获取代理ip列表
    :return:
    '''
    proxies = requests.get(
        'http://api3.xiguadaili.com/ip/?tid=558328278574326&num=1000&delay=1&format=json&filter=1').json()
    proxies = [{"http": "http://{}:{}".format(_['host'], _["port"])} for _ in proxies]
    return proxies

proxie = random.choice(get_proxy())


# 获取板块id列表
def get_ids():
    item = {}
    url = 'https://mrobot.pcauto.com.cn/v3/bbs/pcauto_v3_bbs_forum_tree?callback=brand'
    res = requests.get(url=url, headers=headers, proxies=proxie).text
    con = re.compile('^brand\((.*)\)')
    res = con.findall(res)[0]
    content = json.loads(res)
    brand_id = content['children'][0]['children']
    for i in brand_id:
        try:
            ids = i['children']
            for j in ids:
                item[j['me'][0]] = j['me'][1]
        except:
            item[j['me'][0]] = j['me'][1]
    return item


def save(datas):
    print(len(datas))
    connection = pymysql.connect(host='122.144.167.182',port=33306,user='admin',password='admin',db='python_test',charset='utf8')
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO car_taipinyang(name,article_id,article_url,content_author,content_title,content_time,content,content_replay_count,r_author,r_vip,r_count,r_time,r_id,r_res_author,r_res_vip,r_res_content,r_res_id) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, datas)
            connection.commit()
            print(datas)
            print('写入成功！！！！')
    except Exception as e:
        print("error:")
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def get_id():
    conn = pymysql.connect(host='122.144.167.182',port=33306,user='admin',password='admin',db='python_test',charset='utf8')
    # 获得Cursor对象
    cursor = conn.cursor()
    # 此处需要修改日期，来获取正确的品类信息
    query = '''SELECT DISTINCT(article_id) FROM car_taipinyang '''
    cursor.execute(query)
    l=[]
    for i in cursor.fetchall():
        l.append(i[0])
    cursor.close()
    conn.close()
    return l

print(get_id())
# 贴子回复内容
def T_replay(total_page, id,sub_url,content_title,content_author,content_time,content_replay_count,content,name):
    for k in range(1,total_page+1):
        url_T = 'https://bbs.pcauto.com.cn/3g/loadPostByTid.ajax?callback=jsonp8&tid=%s&pageNo=%s&order=false'% (id,k)
        print(url_T)
        res = requests.get(url=url_T, headers=headers,proxies=proxie).text
        con1 = re.compile('jsonp8\((.*)\)')
        res_json = con1.findall(res)[0]
        res_json = json.loads(res_json)
        # print(res_json)
        r_lists = res_json['resultList']
        if r_lists == []:
            r_author = r_vip = r_content = r_time = r_id = r_res_author = r_res_vip= r_res_content = r_res_id = None
            # print(id, sub_url, content_title, content_author, content_time, content_replay_count, content, name)
            datas = (name,id,sub_url,content_author,content_title,content_time,content,content_replay_count,r_author,r_vip,r_content,r_time,r_id,r_res_author,r_res_vip,r_res_content,r_res_id)
            save(datas)
        else:
            for m in r_lists:
                r_author = m['author']['nickName']                      # 回复者昵称
                r_vip = m['author']['vipUser']                          # 是否是vip
                r_content = m['contentWithoutQuote']                    # 回复内容
                r_time = m['showTime']                                  # 回复时间
                r_id = m['pid']                                         # 回复者id
                r_html = etree.HTML(r_content)
                r_content = r_html.xpath('.//text()')
                r_content = ''.join(r_content).replace('\n','')
                try:
                    r_res = m['quote']
                    r_res_author = r_res['author']['nickName']
                    r_res_vip = r_res['author']['vipUser']
                    r_res_content = r_res['content']
                    r_res_id = r_res['pid']
                    r_res_html = etree.HTML(r_res_content)
                    r_res_content = r_res_html.xpath('.//text()')
                    r_res_content = ''.join(r_res_content).replace('\n','')
                except:
                    r_res = r_res_author = r_res_vip = r_res_content = r_res_id = None
                # print(id,sub_url,content_title,content_author,content_time,content_replay_count,content,name,r_author,r_vip,r_content,r_time,r_id,r_res_author,r_res_vip,r_res_content,r_res_id)
                datas = (name, id, sub_url, content_author, content_title, content_time, content,content_replay_count, r_author, r_vip, r_content, r_time, r_id, r_res_author, r_res_vip,r_res_content, r_res_id)
                save(datas)



def main(i):
    url = 'https://bbs.pcauto.com.cn/forum-%s.html' % i
    # print(url)
    res = requests.get(url=url, headers=headers,proxies=proxie).text
    html = etree.HTML(res)
    lists = html.xpath('//table[@class="data_table"]//tbody')
    # 获取论坛名称
    name = ids[i]
    print(name)
    try:
        total_page = html.xpath('//div[@class="pager"]/a/text()')[-2].replace('...','')
        total_page = int(total_page)
        for k in range(total_page):
            url_a = 'https://bbs.pcauto.com.cn/forum-%s-%s.html'%(i,k)
            res = requests.get(url=url_a, headers=headers,proxies=proxie).text
            html = etree.HTML(res)
            lists = html.xpath('//table[@class="data_table"]//tbody')
            # print(url_a)
            # 解析标题等基本信息
            for j in lists:
                title = j.xpath('./tr/th/span[@class="checkbox_title"]/a/text()')
                if title != []:
                    title_url = 'https:' + j.xpath('./tr/th/span[@class="checkbox_title"]/a/@href')[0]
                    key = title_url.partition('-')[2].split('.')[0]
                    if int(key) in get_id():
                        print(key)
                        continue
                    sub_url = 'https://m.pcauto.com.cn/bbs/topic-%s.html' % key
                    author = j.xpath('./tr/td[@class="author"]/cite/a/text()')
                    rep_time = j.xpath('./tr/td[@class="author"]/em/text()')
                    rep_count = j.xpath('./tr/td[@class="nums"]/cite//text()')[-1].strip()
                    # check_count = j.xpath('./tr/td[@class="nums"]/em/text()')
                    lastpost_user = j.xpath('./tr/td[@class="lastpost"]/cite/a/text()')
                    last_time = j.xpath('./tr/td[@class="lastpost"]/em/text()')
                    # print(sub_url,author,rep_time,rep_count,lastpost_user,last_time)
                    res = requests.get(url=sub_url, headers=headers,proxies=proxie).text
                    html_1 = etree.HTML(res)
                    content_title = title[0]
                    content_author = author[0]
                    content_time = '20' + rep_time[0]                                          # 文章发表时间
                    content_replay_count = rep_count                                  # 文章回复数
                    content = html_1.xpath('//section[@class="m-topic-con-wrap"]//div[@id="Jcont_con"]//text()')
                    content = ''.join(content).strip().replace('\n', '')
                    if content == '':
                        content = html_1.xpath('//div[@id="Jcont_con"]//text()')
                        content = ''.join(content).strip().replace('\n', '')
                    # print(content)
                    total_page = int(content_replay_count)//19+1
                    T_replay(total_page,key,sub_url,content_title,content_author,content_time,content_replay_count,content,name)
    except:
        total_page = 1
        for j in lists:
            title = j.xpath('./tr/th/span[@class="checkbox_title"]/a/text()')
            if title != []:
                title_url = 'https:' + j.xpath('./tr/th/span[@class="checkbox_title"]/a/@href')[0]
                key = title_url.partition('-')[2].split('.')[0]
                if int(key) in get_id():
                    print(key)
                    continue
                sub_url = 'https://m.pcauto.com.cn/bbs/topic-%s.html' % key
                author = j.xpath('./tr/td[@class="author"]/cite/a/text()')
                rep_time = j.xpath('./tr/td[@class="author"]/em/text()')
                rep_count = j.xpath('./tr/td[@class="nums"]/cite//text()')[-1].strip()
                # check_count = j.xpath('./tr/td[@class="nums"]/em/text()')
                lastpost_user = j.xpath('./tr/td[@class="lastpost"]/cite/a/text()')
                last_time = j.xpath('./tr/td[@class="lastpost"]/em/text()')
                print(sub_url, author, rep_time, rep_count, lastpost_user, last_time)
                res = requests.get(url=sub_url, headers=headers,proxies=proxie).text
                html_1 = etree.HTML(res)
                content_title = title[0]
                content_author = author[0]
                content_time = '20' + rep_time[0]  # 文章发表时间
                content_replay_count = rep_count  # 文章回复数
                content = html_1.xpath('//section[@class="m-topic-con-wrap"]//div[@id="Jcont_con"]//text()')
                content = ''.join(content).strip().replace('\n', '')
                if content == '':
                    content = html_1.xpath('//div[@id="Jcont_con"]//text()')
                    content = ''.join(content).strip().replace('\n', '')
                # print(content)
                total_page = int(content_replay_count) // 19 + 1
                T_replay(total_page, key, sub_url, content_title, content_author, content_time, content_replay_count,content, name)


if __name__ == '__main__':
        ids = get_ids()
        for i in get_ids():
            while 1:
                try:
                    a = main(i)
                    break
                except:
                    continue




































