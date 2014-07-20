from scrapy.selector import Selector
import json

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
