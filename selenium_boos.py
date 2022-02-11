import time
from pymysql import *
from lxml import etree
from selenium import webdriver

import logging
logging.basicConfig(level = logging.DEBUG)

class boos():

    def get_url(self, url2):
        driver = webdriver.Chrome()
        try:
            driver.get(url2)
            time.sleep(10)
            html = driver.page_source
            return html
        finally:
            driver.quit()
            # driver.close()

    #获取job列表url
    def analysis_html1(self,html):
        base_url = 'https://www.zhipin.com'
        if html:
            resp_html = etree.HTML(html)
            detail_url_href = resp_html.xpath('//*[@class="primary-box"]/@href')
            detail_url_ka = resp_html.xpath('//*[@class="primary-box"]/@ka')
            detail_url_li = resp_html.xpath('//*[@class="primary-box"]/@data-lid')
            detail_url_yi = resp_html.xpath('//*[@class="primary-box"]/@data-securityid')

            detail_url_href_list = []
            for i in range(0, 20):
                detail_url_href_list.append(
                    base_url + detail_url_href[i] + "?ka=" + detail_url_ka[i] + "&lid=" + detail_url_li[
                        i] + "&securityId=" + detail_url_yi[i])

            return detail_url_href_list
        else:
            return None
    #根据获取到的url访问job详情页
    def analysis_html2(self, html):
        base_url = 'https://www.zhipin.com'
        if html:
            resp_html = etree.HTML(html)
            detail_url_href = resp_html.xpath('//*[@class="primary-box"]/@href')
            detail_url_ka = resp_html.xpath('//*[@class="primary-box"]/@ka')
            detail_url_li = resp_html.xpath('//*[@class="primary-box"]/@data-lid')
            detail_url_yi = resp_html.xpath('//*[@class="primary-box"]/@data-securityid')

            detail_url_href_list = []
            for i in range(0, 20):
                detail_url_href_list.append(
                    base_url + detail_url_href[i] + "?ka=" + detail_url_ka[i] + "&lid=" + detail_url_li[
                        i] + "&securityId=" + detail_url_yi[i])

            return detail_url_href_list
        else:
            return None

    def getjobinfo(self,resp):
        resp_html = etree.HTML(resp)
        # 公司名
        company_name = resp_html.xpath('//*[@class="company-info"]/a/text()')[2]
        company_name1 = str(company_name).replace(' ', '')
        company_name2 = company_name1.replace('\n','')
        # 工作岗位
        job_title = resp_html.xpath('//*[@class="name"]//h1//text()')[0]
        # 工资范围
        job_salary = resp_html.xpath('//*[@class="salary"]//text()')[0]
        # 学历
        job_education = resp_html.xpath('//*[@class="job-banner"]//p//text()')[2]
        # 工作年龄
        job_years = resp_html.xpath('//*[@class="job-banner"]//p//text()')[1]
        # 职位描述
        job_detail = resp_html.xpath('//*[@class="job-sec"]//div[@class="text"]//text()')
        job_detail1 = ''.join(job_detail).replace(" ", "")
        job_detail2 = job_detail1.replace('\n', '')
        # 工作地点
        job_place = resp_html.xpath('//*[@class="job-banner"]//p//text()')[0]

        job = [company_name2,job_title,job_salary,job_education,job_years,job_detail2,job_place]
        return job

    def connect_mysql(self,job):
        try:
            conn = connect(host = 'localhost',port = 3306,
                           user = 'root',passwd = '123456',
                           db = 'spider',charset='utf8')
            cursor = conn.cursor()
            sql = 'insert into boss_job(company_name,job_title,job_salary,job_education,job_years,job_detail,job_place,keyword) values(%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql, job)
            conn.commit()
            cursor.close()
            conn.close()
            print('一条信息录入....')
        except Exception as e:
            print(e)

if __name__ == '__main__':

    keywords = ['软件测试']
    MAX_PAGE = 20
    for keyword in keywords:
        for page_num in range(MAX_PAGE):
            url = f'https://www.zhipin.com/c101090100-p100301/?query={keyword}&page={page_num + 1}&ka=page-{page_num + 1}'
            job_json = {'keyword': keyword}
            boss_spider = boos()
            for url1 in boss_spider.analysis_html1(boss_spider.get_url(url)):
                time.sleep(5)
                # 请求job详情页
                resp = boss_spider.get_url(url1)
                time.sleep(3)
                job = boss_spider.getjobinfo(resp)
                job.append(keyword)
                boss_spider.connect_mysql(job)













