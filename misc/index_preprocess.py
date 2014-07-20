import arrow
from dateutil import tz
import re
from scrapy.selector import Selector
import json

def convert_date(datestr):
    """Convert XDA's timestamp to ISO-8601-based representation, e.g. "2013-11-04T23:07:00Z".
       Input should match one of the following formats:
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
    return date.to('UTC').isoformat()[:-6] + 'Z'

def strip_html(content):
    stripped = ''
    for line in Selector(text=content).xpath('//text()').extract():
        stripped += line + '\n'
    return stripped[:-1]

def strip_quotes(content):
    sel = Selector(text=content)
    for quote in sel.xpath('//div[@style="margin:0px 0px 10px 0px "]'):
        content = content.replace(quote.extract(), '', 1)
    return content

def add_thread_info(post, thread_lookup):
    thread = thread_lookup[post['thread_id']]
    post['thread_title'] = thread['title']
    post['thread_view_count'] = int(thread['view_count'])
    post['url'] = 'http://forum.xda-developers.com%s/post%s' % (thread['link'], post['post_id'])

def build_thread_lookup(threads):
    """Construct a dictionary mapping thread ID to decoded thread JSON object"""
    thread_lookup = {}
    for thread in threads:
        thread_lookup[thread['thread_id']] = thread
    return thread_lookup

def index_preprocess(posts, thread_lookup):
    for post in posts:
        post['content_no_quotes'] = strip_quotes(post['content'])
        post['content_no_quotes_no_html'] = strip_html(post['content_no_quotes'])
        post['content_no_html'] = strip_html(post['content'])
        add_thread_info(post, thread_lookup)
        post['date'] = convert_date(post['date'])
        post['thanks_count'] = len(post['thanks'])
        if 'used' in post:
            post.pop('used', None)

if __name__ == "__main__":
    with open('xda_threads.json') as f:
        threads = json.load(f)
    with open('xda_rank_posts.json') as f:
        posts = json.load(f)

    thread_lookup = build_thread_lookup(threads)
    index_preprocess(posts, thread_lookup)

    json.dump(posts, open('xda_index_posts.json', 'w'), indent=2)
