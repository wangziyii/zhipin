import requests
import json
from lxml import etree
from requests.exceptions import RequestException
from pymysql import *
class BossSpider():
    def get_html(self,url):
        try:
            headers = {
                'cookie': 'acw_tc=0bdd34c216443073410138069e01a689827014423406d078ec890e2ed2b1be; lastCity=100010000; __c=1644307341; __g=-; __a=73545514.1644307341..1644307341.1.1.1.1; __zp_stoken__=af72dW2svMl5wJ2cTRTglazxrCxA4GmMxSzsjGjgncl5wXXBLbGQ6N0VnO0VkPmBQD11lSCIoTjp3N3YsLRxuFisIQn5iWVdRHSoPYxlMA1I7OgVyRFofRhI3FGpdAUc/TWRXPC0AT1hpeSw=',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
            }
            response = requests.get(url=url, headers=headers)
            # 更改编码方式，否则会出现乱码的情况
            response.encoding = "utf-8"
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            return None
    def parse_search_html(self,resp):
        base_url = 'https://www.zhipin.com'
        # resp = json.loads(resp)
        # resp_html = resp['html']
        if resp:
            resp_html = etree.HTML(resp)
            detail_url_href = resp_html.xpath('//*[@class="primary-box"]/@href')
            detail_url_ka = resp_html.xpath('//*[@class="primary-box"]/@ka')
            detail_url_href_list = [base_url+i for i in detail_url_href]
            return detail_url_href_list
        else:
            return None

    def parse_detail_html(self, resp,job_json):
        resp_html = etree.HTML(resp)
        job_detail = resp_html.xpath('//div[@class="job-detail"]/div[@class="detail-content"]/div[1]/div//text()')
        job_detail = [i.replace('\n','').replace(' ','') for i in job_detail]
        job_detail = ''.join(job_detail)

        # import ipdb
        # ipdb.set_trace()
        company_name = resp_html.xpath('//*[@id="main"]/div/div[2]/ul/li[1]/div/div[1]/div[2]/div/h3/a/text()')[0]
        # company_name = resp_html.xpath('//div[@class="info-primary"]/div[@class="flex-box"]/div[@class="name"]/text()')[0]
        job_title = resp_html.xpath('//div[@id="main"]/div[@class="job-banner"]/h1[@class="name"]/text()')[0]
        job_salary = resp_html.xpath('//div[@id="main"]/div[@class="job-banner"]//span[@class="salary"]//text()')[0]
        job_vline = resp_html.xpath('//div[@id="main"]/div[@class="job-banner"]/p/text()')[2]
        job_years = resp_html.xpath('//div[@id="main"]/div[@class="job-banner"]/p/text()')[1]
        job_json['job_detail'] = job_detail
        job_json['company_name'] = company_name
        job_json['job_title'] = job_title
        job_json['job_salary'] = job_salary
        job_json['job_vline'] = job_vline
        job_json['job_years'] = job_years
        self.connect_mysql(job_json)
    def get_full_url(self,url, uri: dict) -> str:
        return url + '?' + '&'.join([str(key) + '=' + str(value) for key, value in uri.items()])
    def connect_mysql(self,job_json):
        try:
            job_list = [job_json['company_name'],job_json['job_title'],
                        job_json['job_salary'],job_json['job_vline'],
                        job_json['job_years'],job_json['job_detail'],
                        job_json['keyword']]
            print(job_list)
            conn = connect(host = 'localhost',port = 3306,
                           user = 'root',passwd = '123456',
                           db = 'spider',charset='utf8')
            cursor = conn.cursor()
            sql = 'insert into boss_job(company_name,job_title,job_salary,job_vline,job_years,job_detail,keyword) values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql,job_list)
            conn.commit()
            cursor.close()
            conn.close()
            print('一条信息录入....')
        except Exception as e:
            print(e)
    def spider(self,url,job_json):
        resp_search = self.get_html(url)
        detail_urls = self.parse_search_html(resp_search)
        if detail_urls:
            for detail_url in detail_urls:
                resp_detail = self.get_html(detail_url)
                if type(resp_detail) is str:
                    self.parse_detail_html(resp_detail,job_json)
if __name__ == '__main__':
    keywords = ['软件测试']
    MAX_PAGE = 1
    for keyword in keywords:
        for page_num in range(MAX_PAGE):
            url = f'https://www.zhipin.com/c101090100-p100301/?query={keyword}&page={page_num+1}&ka=page-{page_num+1}'
            job_json = {'keyword':keyword}
            boss_spider = BossSpider()
            boss_spider.spider(url,job_json)
