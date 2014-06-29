import scrapy
import re
from urlparse import urljoin
from scraper.items import ThreadItem, PostItem


class XdaSpider(scrapy.Spider):
    name = "xda"
    #allowed_domains = "forum.xda-developers.com"
    start_urls = [
        "http://forum.xda-developers.com/google-nexus-5/general"
    ]

    THREAD_PAGE_LIMIT = 10

    def parse(self, response):
        split_url = response.url.split('/')
        if split_url[-1].startswith('page'):
            offset = -1
        else:
            offset = 0

        forum = split_url[offset - 2]
        sub_forum = split_url[offset - 1]
        for sel in response.xpath('//a[@class="threadTitle"]'):
            item = ThreadItem()
            item['title'] = sel.xpath('text()')[0].extract()
            item['link'] = sel.xpath('@href')[0].extract().strip()
            item['thread_id'] = re.search('.\-t([0-9]+)', item['link']).group(1)
            item['forum'] = forum
            item['sub_forum'] = sub_forum
            item['view_count'] = sel.xpath('../../../td[@class="statsColumn"]/div/text()').re('Views: ([0-9,]+)')[0]
            item['view_count'] = item['view_count'].replace(',', '')
            yield item
            yield scrapy.Request(urljoin(response.url, item['link']), callback=self.parse_thread)

        next_page = response.xpath('//a[@class="smallfont" and @rel="next"]/@href').extract()
        if len(next_page):
            next_page = next_page[0].strip()
            page_num_offset = next_page.find('page')
            if page_num_offset != -1 and int(next_page[page_num_offset + 4:]) < self.THREAD_PAGE_LIMIT:
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_thread(self, response):
        split_url = response.url.split('/')
        if split_url[-1].startswith('page'):
            offset = -1
        else:
            offset = 0

        thread_name = split_url[offset - 1]
        thread_id = re.search('.\-t([0-9]+)', thread_name).group(1)
        for sel in response.xpath('//table[@class="tborder"]'):
            post_sel = sel.xpath('..//td[@class="alt1 postContent"]')
            if not post_sel:
                # No postContent means this is a thank-you table, so skip
                continue

            item = PostItem()
            item['thread_id'] = thread_id
            item['author'] = sel.xpath('..//a[@class="posterName"]//text()')[0].extract()
            item['date'] = sel.xpath('..//div[@class="postDate"]/text()')[1].extract().strip()
            item['post_id'] = post_sel.xpath('@id').re('td_post_([0-9]+)')[0]

            post_message = post_sel.xpath('div[@id="post_message_' + item['post_id'] + '"]')
            item['content'] = post_message[0].extract()
            # If this is the first post on a page, it has an ad... remove it
            ad = post_message.xpath('div[@style="margin: 0 0 15px 15px; float: right"]')
            if ad:
                item['content'] = item['content'].replace(ad[0].extract(), '', 1)
                # Also, the post title will appear at the top if this is the first post in a thread
                title = post_message.xpath('div[@class="smallfont"] | hr')
                if title:
                    item['content'] = item['content'].replace(title[0].extract(), '', 1)
                    item['content'] = item['content'].replace(title[1].extract(), '', 1)
            item['content'] = re.sub('[\r\n\t]', '', item['content'])

            item['thanks'] = []
            for ty in response.xpath('//tr[@id="collapseobj_Thanks_' + item['post_id'] + '"]//a/text()'):
                item['thanks'].append(ty.extract())

            yield item

        next_page = response.xpath('//a[@class="smallfont" and @rel="next"]/@href').extract()
        if len(next_page):
            next_page = next_page[0].strip()
            page_num_offset = next_page.find('page')
            if page_num_offset != -1:
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse_thread)
