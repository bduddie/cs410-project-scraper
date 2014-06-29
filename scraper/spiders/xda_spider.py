import scrapy

class XdaSpider(scrapy.Spider):
    name = "xda-developers"
    allowed_domains = "forum.xda-developers.com"
    start_urls = [
        "http://forum.xda-developers.com/google-nexus-5/general"
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2]
        print(filename)