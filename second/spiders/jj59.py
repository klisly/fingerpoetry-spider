#-*- coding:utf-8 –*-
from scrapy.selector import Selector
import os
import scrapy
from ..CommonUtil import  CommonUtil
from ..items import XiaohuaItem, SanWenItem
import time, datetime
site = 'http://www.jj59.com'
maxdepth = 100;
util = CommonUtil();
domain = "www.jj59.com";
acceptPre="http://www.jj59.com";
class SanwenSpider(scrapy.Spider):
    name = "jj59"
    allowed_domains = ["jj59.com"]
    start_urls = (
        "http://www.jj59.com/",
        # "http://www.jj59.com/jjart/375944.html",
     )

    def parse(self, response):
        # self.parseData(response);
        sel = Selector(response)
        count = 0;
        for link in sel.xpath('//a/@href').extract():
            if link.startswith("/"):
                link = site + link;
            if link.startswith(domain):
                link = "http://" + link;
            if link.startswith(acceptPre):
                isContinue = True;
            else:
                isContinue = False;
            fdep = util.getDep(response.url);
            if fdep is None:
                fdep = 1
            if isContinue and not util.hasUrl(link) and fdep <= maxdepth:
                util.saveUrl(link);
                util.saveDep(link, fdep+1);
                count += 1;
                request = scrapy.Request(link, callback=self.parse_url_item)
                yield request

    def parse_url_item(self, response):
        sel = Selector(response)
        count = 0;
        for link in sel.xpath('//a/@href').extract():
            if link.startswith("/"):
                link = site + link;
            if link.startswith(domain):
                link = "http://" + link;
            if link.startswith(acceptPre):
                isContinue = True;
            else:
                isContinue = False;
            fdep = util.getDep(response.url);
            if fdep is None:
                fdep = 1
            if isContinue and not util.hasUrl(link) and fdep <= maxdepth:
                util.saveUrl(link);
                util.saveDep(link, fdep + 1);
                count += 1;
                if link.find(".html") != -1 and link.find("page_") == -1:
                    request = scrapy.Request(link, callback=self.parseData)
                else:
                    request = scrapy.Request(link, callback=self.parse_url_item)
                yield request

    def parse_item(self, response):
        try:
            print "response url:",response.url
            if response.url.startswith(acceptPre):
                item = self.parseData(response);
            return item
        except Exception as e:
            print e;
            return None

    def parseData(self, response):
        print "parse data:"+response.url
        sel = Selector(response)
        url = response.url
        belong = "";
        title = "";
        author = "";
        readNum = 0;
        content = "";
        try:
            belong = sel.xpath('//div[@class="place"]/a/text()').extract();
        except Exception as e:
            pass;
        try:
            title = sel.xpath('//h1/text()').extract()[0];
        except Exception as e:
            pass;
        try:
            info = sel.xpath('//div[@class="info"]').extract()[0];
            info = info.split(" ")
            author = "";

            count = 0;
            for ins in info:
                if (count == 1):
                    index = ins.find("</small>");
                    date = ins[index + 8:];
                if (count == 3):
                    index = ins.find("</small>");
                    author = ins[index + 8:];
                # if (count == 5):
                #     ins = ins.replace("</small></div>", "");
                #     index = ins.find('">');
                #     readNum = ins[index + 2:];
                # insif(count == 1):
                #     ins = ins.replace("</a></span>","");
                #     index = ins.encode("utf-8").find(">");
                #     author = ins[index+1:]
                count = count + 1;
        except Exception as e:
            pass;
        try:
            contents = sel.xpath('//div[@class="content"]/p').extract();
            for c in contents:
                content = content + c;
        except Exception as e:
            pass;



        # print belong,"\ntitle:",title,"\ninfo:",info,"\ncontent:",content,"\nreadNum:",readNum,"\ndate:",date,"\n author:",author
        if (len(content) > 10):
            item = SanWenItem();
            item['url'] = url
            item['belong'] = belong
            item['title'] = title
            item['read'] = readNum
            item['content'] = content
            item['author']=author
            # ftime = time.strptime(date, "%Y-%m-%d")
            # y, m, d = ftime[0:3]
            # item['publishAt'] = datetime.datetime(y, m, d);
            ftime = time.localtime();
            y, m, d, h, mi, s = ftime[0:6]
            item['createAt'] = datetime.datetime(y, m, d, h, mi, s);
            item['updateAt'] = datetime.datetime(y, m, d, h, mi, s);
            item['publishAt'] = datetime.datetime(y, m, d, h, mi, s);
            item['checked'] = False;
            return item
