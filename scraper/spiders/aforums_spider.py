import arrow
from dateutil import tz
import scrapy
import re
from urlparse import urljoin
from scraper.items import ThreadItem, PostItem


class AForumsSpider(scrapy.Spider):
    name = "aforum"
    #allowed_domains = "forum.xda-developers.com"
    start_urls = [
        "http://androidforums.com/nexus-5/?prefixid=General",
    ]

    THREAD_PAGE_LIMIT = 10

    def convert_date(self, datestr):
        """Convert XDA's timestamp to ISO-8601-based representation. Expected input should match one
           of the following examples:
            4th November 2013, 03:07 PM
            Yesterday, 12:37 PM
            Today, 01:43 AM
        """
        m = re.search('(Today|Yesterday), ([0-9]{2}):([0-9]{2}) (AM|PM)', datestr)
        if m:
            day = m.group(1)
            hour = int(m.group(2))
            minute = int(m.group(3))
            if m.group(4) == 'PM' and hour < 12:
                hour += 12
            elif m.group(4) == 'AM' and hour == 12:
                hour = 0
            date = arrow.get(tz.gettz('US/Pacific')).replace(hour=hour, minute=minute, second=0, microsecond=0)
            if day == 'Yesterday':
                date.replace(days=-1)
        else:
            date = arrow.get(datestr, 'D MMMM YYYY, HH:mm A').replace(tzinfo=tz.gettz('US/Pacific'))
        # Return in form like '2013-11-04T23:07:00Z'
        return date.to('UTC').isoformat()[:-6] + 'Z'


    def parse(self, response):
        split_url = response.url.split('/')
        if split_url[-1].startswith('index'):
            offset = -1
        else:
            offset = 0

        forum = split_url[offset - 2]
        sub_forum = split_url[offset - 1]
        for sel in response.xpath('//a[@id="thread_title_*"]'):
            item = ThreadItem()
            item['title'] = sel.xpath('text()')[0].extract()
            item['link'] = sel.xpath('@href')[0].extract().strip()
            item['thread_id'] = re.match('thread_title_([0-9]+)', sel.xpath('@id').extract()[0]).group(1)
            item['forum'] = forum
            item['sub_forum'] = sub_forum
            item['view_count'] = sel.xpath('../../../td[last()]/text()')
            item['view_count'] = item['view_count'].replace(',', '')
            yield item
            yield scrapy.Request(urljoin(response.url, item['link']), callback=self.parse_thread)

        next_page = response.xpath('//a[@class="smallfont" and @rel="nofollow"]/@href').extract()
        if len(next_page):
            next_page = next_page[0].strip()
            page_num_offset_begin = next_page.find('index')
            page_num_offset_end = next_page.find('.html')
            page_num = next_page[page_num_offset_begin+4:-page_num_offset_end]
            if page_num != -1 and int(page_num) < self.THREAD_PAGE_LIMIT:
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_thread(self, response):
        split_url = response.url.split('/')
        if split_url[-1].startswith('index'):
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
            author_xpath = sel.xpath('..//a[@class="posterName"]//text()')
            if len(author_xpath):
                item['author'] = author_xpath[0].extract()
            else:
                # Guest account most likely, no link to profile page
                author_xpath = sel.xpath('..//td[@class="posterInfoHead"]//text()')
                if not len(author_xpath):
                    scrapy.log.error("Missing post author name!")
                    continue
                item['author'] = author_xpath[0].extract().strip() + " (Guest)"

            item['date'] = sel.xpath('..//div[@class="postDate"]/text()')[1].extract().strip()
            item['date'] = self.convert_date(item['date'])
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
