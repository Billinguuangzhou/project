#!/usr/bin/env python
# coding=utf-8

import sys
reload(sys) 
sys.setdefaultencoding('utf-8')
import requests
from requests.adapters import HTTPAdapter
import re
import time, os, shutil, logging
from GetConfig import config
#from GetPageDetail import page_detail
#from urllib.parse import quote
from bs4 import BeautifulSoup

HEADER = config.crawl_headers
HEADER4ResearchGate = config.headers4ResearchGate
# 获取cookie
BAIDU_XUESHU = 'http://xueshu.baidu.com'
BASIC_URL = 'http://xueshu.baidu.com/s'
DOWNLOAD_PATH = '../../data/baidu/'

class SearchTools(object):
    '''
    构建搜索类
    实现搜索方法
    '''

    def __init__(self):
        self.session = requests.Session()
        self.cur_page_num = 1
        # 保持会话
        #self.session.get(BASIC_URL, headers=HEADER)

    def search_reference(self, query):
        '''
        第一次发送post请求
        再一次发送get请求,这次请求没有写文献等东西
        两次请求来获得文献列表
        '''
        get_data = {
            'wd': query,
            'rsv_bp': '0',
            'tn': 'SE_baiduxueshu_c1gjeupa',
            'rsv_spt': 3,
            'ie': 'utf-8',
            'f': '3',
            'rsv_sug2': '1',
            'sc_f_para':'sc_tasktype={firstSimpleSearch}',
            'rsp': '4'
            #'__': time.asctime(time.localtime()) + ' GMT+0800 (中国标准时间)'
        }
        url = 'https://www.researchgate.net/profile/Peter_Smagorinsky/publication/306154788_Praxis_shock_Making_the_transition_from_a_student-centered_university_program_to_the_corporate_climate_of_schools/links/57c3559008ae2f5eb3396353/Praxis-shock-Making-the-transition-from-a-student-centered-university-program-to-the-corporate-climate-of-schools.pdf'
        page = self.session.get(url, headers=HEADER4ResearchGate)
        #print page.headers
        #print page.status_code
        #print len(page.text)
        print type(page.text)
        with open('paper.pdf', 'wb') as f:
            f.write(page.content)

        """
        result_list_page = self.session.get(BASIC_URL, params=get_data, headers=HEADER)
        #print result_list_page.text
        #result_list_page.encoding = 'gbk'
        #with open('result_list_page.html', 'w') as f:
        #   f.write(result_list_page.text)
        #with open('result_list_page.html', 'w') as f:
        #   f.write(result_list_page.text)
        title_hrefs = self.parse_result_list_page(result_list_page.text) #[('t1','h1'), ('t2','h2'), ('t3', 'h3')]
        title_download_urls = [] #[('t1', ['download1', 'download2']), ...]
        for item in title_hrefs:
            title = item[0]
            href = item[1]
            detail_url = BAIDU_XUESHU + href
            detail_page = self.session.get(detail_url, headers=HEADER)
            download_urls = self.parse_detail_page(detail_page.text)
            title_download_urls.append((title, download_urls))
        self.download_pdf(DOWNLOAD_PATH, title_download_urls)
        """

    def Unicode2HexStr(self, Unicde_Str):
        Hex_Str = ""
        for i in range(0, len(Unicde_Str)):
            Hex_Str += (hex(ord(Unicde_Str[i])).replace('0x','').zfill(2)) + ' '
        return Hex_Str

    def parse_result_list_page(self, page_source):
        '''
        #保存页面信息
        #解析每一页的下载地址
        '''
        title_hrefs = []
        soup = BeautifulSoup(page_source, 'lxml')
        content1 = soup.find(name='div', attrs={'id': 'content_leftrs'})
        for index, content2 in enumerate(content1.find_all(name='div', attrs={'class': 'sc_default_result'})):
            h3 = content2.find(name='h3', attrs={'class': {'t', 'c_font'}})
            a = h3.find(name='a')
            href = a['href'].strip()
            title = a.text.strip()
            title_hrefs.append((title, href))
        return title_hrefs

    #返回一篇论文的下载地址列表
    def parse_detail_page(self, detail_page):
        download_urls = []
        soup = BeautifulSoup(detail_page, 'lxml')
        download_items = soup.find_all(name='a', class_="dl_item", target="_blank", href=re.compile(r'http.+?\.pdf'))
        if download_items is None:
            return download_urls
        for item in download_items:
            download_urls.append(item['href'].strip())
        return download_urls

    def download_pdf(self, download_dir, title_download_urls):
        self.set_session_retry_times(3)
        for item in title_download_urls:
            title = item[0]
            download_urls = item[1]
            if len(download_urls) == 0: #下载列表为空
                continue
            print '题目:[' + title + ']'
            #进行下载
            for url in download_urls:
                print '链接1:' + url
                findFlag = False
                try:
                    pdf = self.session.get(url, allow_redirects=False, headers=HEADER4ResearchGate, timeout=5) 
                    print pdf.status_code

                    if pdf.status_code == 200:
                        findFlag = True
                    while pdf.status_code != 200:
                        new_url = pdf.headers['Location'].strip()
                        print '新链接:' + new_url
                        matchObj = re.match(r'.*?\.pdf', new_url)
                        if matchObj: #如果还是以.pdf结尾的链接，则继续
                            try:
                                pdf = self.session.get(new_url, allow_redirects=False, headers=HEADER4ResearchGate, timeout=5) 
                                if pdf.status_code == 200: #经过一系列以.pdf结尾的链接找到真实pdf
                                    findFlag = True
                                    break
                            except requests.exceptions.RequestException as e:
                                print(e)
                                break
                        else:
                            break
                    
                    if findFlag:
                        file_name = download_dir + '_'.join(title.split()) + '.pdf'
                        print file_name
                        with open(file_name, 'w') as f:
                            f.write(pdf.text)
                        break
                except requests.exceptions.RequestException as e:
                    print(e)
                print "-----------------------------"
        self.set_session_retry_times(1)

    def set_session_retry_times(self, retry_times = 3):
        self.session.mount('http://', HTTPAdapter(max_retries=retry_times))
        self.session.mount('https://', HTTPAdapter(max_retries=retry_times))

    """
    def pre_parse_page(self, page_source):
        '''
        #用户选择需要检索的页数
        '''
        reference_num_pattern_compile = re.compile(r'.*?找到&nbsp;(.*?)&nbsp;')
        reference_num = re.search(reference_num_pattern_compile,
                                  page_source).group(1)
        reference_num_int = int(reference_num.replace(',', ''))
        print('检索到' + reference_num + '条结果，全部下载大约需要' +
              s2h(reference_num_int * 5) + '。')
        is_all_download = input('是否要全部下载（y/n）?')
        # 将所有数量根据每页20计算多少页
        if is_all_download == 'y':
            page, i = divmod(reference_num_int, 20)
            if i != 0:
                page += 1
            return page
        else:
            select_download_num = int(input('请输入需要下载的数量：'))
            while True:
                if select_download_num > reference_num_int:
                    print('输入数量大于检索结果，请重新输入！')
                    select_download_num = int(input('请输入需要下载的数量（不满一页将下载整页）：'))
                else:
                    page, i = divmod(select_download_num, 20)
                    # 不满一页的下载一整页
                    if i != 0:
                        page += 1
                    print("开始下载前%d页所有文件，预计用时%s" % (page, s2h(page * 20 * 5)))
                    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
                    return page

    def parse_page(self, download_page_left, page_source):
        '''
        #保存页面信息
        #解析每一页的下载地址
        '''
        soup = BeautifulSoup(page_source, 'lxml')
        # 定位到内容表区域
        tr_table = soup.find(name='table', attrs={'class': 'GridTableContent'})
        # 处理验证码
        try:
            # 去除第一个tr标签（表头）
            tr_table.tr.extract()
        except Exception as e:
            logging.error('出现验证码')
            return self.parse_page(
                download_page_left,
                crack.get_image(self.get_result_url, self.session,
                                page_source))
        # 遍历每一行
        for index, tr_info in enumerate(tr_table.find_all(name='tr')):
            tr_text = ''
            download_url = ''
            detail_url = ''
            # 遍历每一列
            for index, td_info in enumerate(tr_info.find_all(name='td')):
                # 因为一列中的信息非常杂乱，此处进行二次拼接
                td_text = ''
                for string in td_info.stripped_strings:
                    td_text += string
                tr_text += td_text + ' '
                with open(
                        'data/ReferenceList.txt', 'a',
                        encoding='utf-8') as file:
                    file.write(td_text + ' ')
                # 寻找下载链接
                dl_url = td_info.find('a', attrs={'class': 'briefDl_D'})
                # 寻找详情链接
                dt_url = td_info.find('a', attrs={'class': 'fz14'})
                # 排除不是所需要的列
                if dt_url:
                    detail_url = dt_url.attrs['href']
                if dl_url:
                    download_url = dl_url.attrs['href']
            # 将每一篇文献的信息分组
            single_refence_list = tr_text.split(' ')
            self.download_refence(download_url, single_refence_list)
            # 是否开启详情页数据抓取
            if config.crawl_isdetail == '1':
                time.sleep(config.crawl_stepWaitTime)
                page_detail.get_detail_page(self.session, self.get_result_url,
                                            detail_url, single_refence_list,
                                            self.download_url)
            # 在每一行结束后输入一个空行
            with open('data/ReferenceList.txt', 'a', encoding='utf-8') as file:
                file.write('\n')
        # download_page_left为剩余等待遍历页面
        if download_page_left > 1:
            self.cur_page_num += 1
            self.get_another_page(download_page_left)

    def get_another_page(self, download_page_left):
        '''
        #请求其他页面和请求第一个页面形式不同
        #重新构造请求
        '''
        time.sleep(config.crawl_stepWaitTime)
        curpage_pattern_compile = re.compile(r'.*?curpage=(\d+).*?')
        self.get_result_url = CHANGE_PAGE_URL + re.sub(
            curpage_pattern_compile, '?curpage=' + str(self.cur_page_num),
            self.change_page_url)
        get_res = self.session.get(self.get_result_url, headers=HEADER)
        download_page_left -= 1
        self.parse_page(download_page_left, get_res.text)


    def download_refence(self,url, single_refence_list):
        '''
        #拼接下载地址
        #进行文献下载
        '''
        print('正在下载: ' + single_refence_list[1] + '.caj')
        name = single_refence_list[1] + '_' + single_refence_list[2]
        # 检查文件命名，防止网站资源有特殊字符本地无法保存
        file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
        name = re.sub(file_pattern_compile, '', name)
        # 拼接下载地址
        self.download_url = DOWNLOAD_URL + re.sub(r'../', '', url)
        # 保存下载链接
        with open('data/Links.txt', 'a', encoding='utf-8') as file:
            file.write(self.download_url + '\n')
        # 检查是否开启下载模式
        if config.crawl_isdownload == '1':
            if not os.path.isdir('data/CAJs'):
                os.mkdir(r'data/CAJs')
            refence_file = requests.get(self.download_url, headers=HEADER)
            with open('data/CAJs\\' + name + '.caj', 'wb') as file:
                file.write(refence_file.content)
            time.sleep(config.crawl_stepWaitTime)
    """


def s2h(seconds):
    '''
    将秒数转为小时数
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return ("%02d小时%02d分钟%02d秒" % (h, m, s))


def main():
    if os.path.isdir('data'):
        # 递归删除文件
        shutil.rmtree('data')
    # 创建一个空的
    os.mkdir('data')
    #query = '爬虫'
    query = 'We have designed and implemented the Google File System (GFS) to meet the rapidly growing demands of Google’s data processing n'
    search = SearchTools()
    search.search_reference(query)
    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
    #print('爬取完毕，共运行：'+s2h(time.perf_counter()))


if __name__ == '__main__':
    main()
