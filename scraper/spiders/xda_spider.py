import scrapy

class XdaSpider(scrapy.Spider):
    name = "xda"
    allowed_domains = "forum.xda-developers.com"
    start_urls = [
        "http://forum.xda-developers.com/google-nexus-5/general"
    ]

    def parse(self, response):
        uri_split = response.url.split("/")
        filename = uri_split[-1]
        with open(filename, 'wb') as file:
            file.write(response.body)