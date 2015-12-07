# -*- coding: utf-8 -*-
import scrapy ###comment ?
import re
import json 
import time
import re
from Med.items import MedItem
from scrapy.selector import Selector
from scrapy.http import  Request
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup
import urllib2

class DiabetspiderSpider(CrawlSpider):
    name = "diabetSpider"
    allowed_domains = ["http://www.medhelp.org/"]
    start_urls = (
        'http://www.medhelp.org/forums/Diabetes---Type-2/show/46?page=1',
    )

    extractor = {
    	'next_page' : LinkExtractor(allow = r'http://www.medhelp.org/forums/Diabetes---Type-2/show/46(.*)'),
    	'post_page' : LinkExtractor(allow = r'http://www.medhelp.org/posts/Diabetes---Type-2/.*/show/\d+'),
    	'poster_page': LinkExtractor(allow = r'http://www.medhelp.org/personal_pages/user/\d+'),
    }

    path = {
    	'title' : '/html/head/title/text()',
    	'reply_num' :  '//*[@id="comments_header"]/span/text()',
              'qa' : '//div[@class="KonaBody"]',
    	#'qa' : '//div[@class="KonaBody"]/text()[preceding-sibling::br]',
    }

    new_path = {
        'title': '//*[@id="post_question_header"]/div[2]/div[1]/text()', #title = response.xpath('//*[@id="post_question_header"]/div[2]/div[1]/text()').extract()[0].strip()
        'reply_num':'//*[@id="post_answer_header"]/div[1]/text()', #reply_num = int(response.xpath('//*[@id="post_answer_header"]/div[1]/text()').extract()[0].strip().split(' ')[0])
        'qa':'//div[@class="post_message_container"]/div[@class="post_message fonts_resizable"]',
        #re.sub(r'<div(.*)none">|<div class(.*)</div>|\xa0|</div>|<br>|\t|\n|\r','',qa[0].extract()).strip()
    }

    def get_userinfo(self,user_page):
        demo = []
        interest = []
        user_req = urllib2.Request(user_page, headers={'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"})
        user_html = urllib2.urlopen(user_req)

        user_soup = BeautifulSoup(user_html, "lxml")  # soup for user homepage

        # find the user's interests
        for interest_sec in user_soup.find_all('span', {'class': 'interests_show'}):
            for interest_info in interest_sec.find_all('a'):
                interest.append(interest_info.get_text().strip())

        # find the user's demo_info
        for demo_sec in user_soup.find_all('div', {'class': 'bottom float_fix'}):
            demo_sec2 = demo_sec.find_all('div', {'class': 'section'})[0]
            num = 0
            for demo_info in demo_sec2.find_all('span'):
                if (num > 0 and num < 4):
                    if '' != demo_info.get_text().strip():
                        demo.append(demo_info.get_text().strip())
                num = num + 1

        return demo, interest

    def parse(self, response):
        for link in self.extractor['next_page'].extract_links(response) :
        	yield Request(url = link.url, callback = self.parse)

        for link in self.extractor['post_page'].extract_links(response):
        	yield Request(url = link.url, callback = self.parse_poster)

    def parse_poster(self,response):
        medLoader = ItemLoader(item = MedItem(), response = response)
        path = self.path
        version = 0 # 0: old 1:new

        #judege the reply num first
        reply_num = response.xpath(path['reply_num']).extract() 
        if reply_num == []:
            version = 1
            print "new verion!"
            path = self.new_path
            reply_num = response.xpath(path['reply_num']).extract() 
            reply_num = int(reply_num[0].strip().split(' ')[0])
        else:
            reply_num = int(reply_num[0].strip().split(' ')[0])
            print "old version"

        #fill post info
        url = str(response.url)
        post_id = url.split('/')[-1] 
        medLoader.add_value('post_id',post_id)  #is str
        medLoader.add_value('post_url',url) # is str
        medLoader.add_value('reply_num',reply_num) # is int
        title = str(response.xpath(path['title']).extract()[0]).strip()
        medLoader.add_value('title',title)

        #fill question and replies
        allQA = response.xpath(path['qa']).extract()
        if version == 0:
            question = self.getQA(allQA[0])
            answer = []
            for i in range(1,len(allQA)):
                answer.append(self.getQA(allQA[i]))
            medLoader.add_value('question',question)
            medLoader.add_value('replies',answer)
        else:
            question= re.sub(r'<div(.*)none">|<div class(.*)</div>|\xa0|</div>|<br>|\t|\n|\r','',allQA[0].strip())
            answer = []
            for i in range(1,len(allQA)):
                answer.append(re.sub(r'<div(.*)none">|<div class(.*)</div>|\xa0|</div>|<br>|\t|\n|\r','',allQA[i].strip()))
            medLoader.add_value('question',question)
            medLoader.add_value('replies',answer)

        #fill poster info
        poster_url = self.extractor['poster_page'].extract_links(response)[0].url
        poster_id = poster_url.split('/')[-1] 
        #[demo,interest] = self.get_userinfo(poster_url)
        medLoader.add_value('poster_id',poster_id)
        #medLoader.add_value('poster_demo',demo)
        #medLoader.add_value('poster_interest',interest)

        return medLoader.load_item()

    def getQA(self,qa):
        str = re.sub(r'\n|\t|<div class="KonaBody">|</div>|<br>|\r|\xa0','',qa)
        return str.strip()

    






