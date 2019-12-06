##############################
# spider for school of business
# filename:spider_bs.py
# author:  liwei
# StuID:   1711350
# date:    2019.12.1
##############################

import scrapy
import os
from teacherInfo.items import TeacherinfoItem
import re

class HTTeacherInfoSpider(scrapy.Spider):
    name = "bs"
    # 创建存储爬取信息的文件夹
    if not os.path.exists('../docs/%s'%name):
        os.mkdir('../docs/%s'%name)

    if not os.path.exists('../docs/%s/imgs'%name):
        os.mkdir('../docs/%s/imgs'%name)

    baseurl = 'https://bs.nankai.edu.cn/'

    img_name_dict = {}
    def start_requests(self):
        urls = [
            'https://bs.nankai.edu.cn/bm/list.htm',
            'https://bs.nankai.edu.cn/caccounting/list.htm',
            'https://bs.nankai.edu.cn/cmarketing/list.htm',
            'https://bs.nankai.edu.cn/financial/list.htm',
            'https://bs.nankai.edu.cn/hr/list.htm',
            'https://bs.nankai.edu.cn/mse/list.htm',
            'https://bs.nankai.edu.cn/irm/list.htm',
            'https://bs.nankai.edu.cn/mrc/list.htm'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        # 得到锚文本
        teacherItems = response.xpath('//ul[@class="wp_article_list"]')

        #获取每位老师具体介绍页面链接锚文本解析得到链接
        nexturls = teacherItems.xpath('.//li')
        for urlt in nexturls:
            nurl = str(self.baseurl+urlt.xpath(".//a/@href").get()).replace('\n','').replace(' ','').replace('\r','').replace('\t','')
            # 递归回调解析教师信息的解析器
            print(nurl)
            yield scrapy.Request(url=nurl, callback=self.parseTeacher)

    def parseImg(self, response):
        item = response.meta['item']
        last = str(item['image_url']).split('.')[-1]
        #if last == 'gif' :                  # gif格式为空的图片
        #    return
        with open('../docs/%s/imgs/%s.%s'%(self.name,item['image_name'],last),'wb') as f:
            f.write(response.body)
        f.close()

    def parseTeacher(self,response):
        #/html/body/div[3]/div/div/div
        # 保存网页的主体内容
        details = response.xpath('//div[@portletmode="simpleArticleAttri"]')
        filename=str(details.xpath('.//div[@class="name"]/text()').get()).replace('\n','').replace(' ','').replace('\r','')
        f = open('../docs/%s/%s.txt'%(self.name,filename),'w',encoding='utf-8')
        f.write(filename+'\n')
        for item in details.xpath('.//div[@class = "lxfs-info"]').xpath('.//div[@class="info"]'):
            #print(item)
            for text in item.xpath('.//text()').getall():
                f.write(str(text).replace('\n','').replace(' ','').replace('\r',''))
                f.write('\n')
        for item in details.xpath('.//div[@class="layui-tab layui-tab-brief"]'):
            #print(item)
            for text in item.xpath('.//text()').getall():
                f.write(str(text).replace('\n','').replace(' ','').replace('\r',''))
                f.write('\n')
        f.close()
        # 存儲教师姓名和网址映射信息
        file = open('../docs/%s/index.txt'%self.name,'a',encoding='utf-8')
        file.write(filename+ "," + response.url+ '\n')
        file.close()
        # 递归回调函数保存图片
        imgurl = details.xpath('.//img/@src').get()
        item = TeacherinfoItem()
        item['image_name'] = filename
        item['image_url'] = self.baseurl + imgurl
        request = scrapy.Request(url=item['image_url'], callback=self.parseImg)
        request.meta['item'] = item
        yield request