import scrapy
from scraper.items import ThreadItem


class XdaSpider(scrapy.Spider):
    name = "xda"
    allowed_domains = "forum.xda-developers.com"
    start_urls = [
        "http://forum.xda-developers.com/google-nexus-5/general"
    ]

    def parse(self, response):
        urlsplit = response.url.split('/')
        forum = urlsplit[-2]
        sub_forum = urlsplit[-1]
        for sel in response.xpath('//a[@class="threadTitle"]'):
            ti = ThreadItem()
            ti['title'] = sel.xpath('text()').extract()
            ti['link'] = sel.xpath('@href').extract()
            ti['thread_id'] = sel.xpath('@href').re('.\-t([0-9]+)')
            ti['forum'] = forum
            ti['sub_forum'] = sub_forum
            yield ti
