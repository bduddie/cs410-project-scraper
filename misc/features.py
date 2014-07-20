from datetime import datetime
from index_preprocess import *
import simplejson as json
from scrapy.selector import Selector

def count_unique_terms(terms):
    unique_terms = set()
    for term in terms:
        if term not in unique_terms:
            unique_terms.add(term)
    return len(unique_terms)

def term_counts(content):
    terms = content.split()
    return (len(terms),  count_unique_terms(terms))

def hyperlink_count(sel):
    return len(sel.xpath('.//a'))

def quotes_count(sel):
    return len(sel.xpath('//div[@style="margin:0px 0px 10px 0px "]'))

def is_html_formatted(sel):
    if sel.xpath('//div')[0].xpath('.//b | .//i | .//u | .//strong | .//em | .//font | .//h1 | .//h2 | .//h3 | .//h4 | '
                                   './/h5 | .//h6 | .//ol | .//ul | .//li | .//span[@style] | .//p[@style] | '
                                   './/div[@style] | .//table'):
        return True
    else:
        return False

def contains_list_html(sel):
    return True if sel.xpath('//div')[0].xpath('.//ol | .//ul | .//li') else False

def duration_minutes(start, end):
    start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
    end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
    delta = end - start
    return int(delta.total_seconds() / 60)

def compute_thread_positions(rank_posts, thread_lookup, all_posts=None):
    if not all_posts:
        with open('xda_posts.json') as f:
            all_posts = json.load(f)

    post_lookup = {}
    for post in rank_posts:
        post_lookup[post['post_id']] = post

    rank_threads = {}
    for post in rank_posts:
        if post['thread_id'] not in rank_threads:
            rank_threads[post['thread_id']] = thread_lookup[post['thread_id']]
            rank_thread = rank_threads[post['thread_id']]
            rank_thread['posts'] = []
            #rank_thread['rank_posts'] = {}
        #rank_thread['rank_posts'][post['post_id']] = post

    for post in all_posts:
        if post['thread_id'] in rank_threads:
            rank_threads[post['thread_id']]['posts'].append(post)

    for post in rank_posts:
        thread = rank_threads[post['thread_id']]
        index = 0
        thread['posts'] = sorted(thread['posts'], key=lambda k: int(k['post_id']))
        for thread_post in thread['posts']:
            if thread_post['post_id'] == post['post_id']:
                post['thread_position'] = index
                break
            else:
                index += 1

        post['thread_post_count'] = len(thread['posts'])
        op = thread['posts'][0]
        if post['author'] == op['author']:
            post['author_is_op'] = True
        else:
            post['author_is_op'] = False

        post['thread_start'] = op['date']
        post['thread_end'] = thread['posts'][-1]['date']
        post['thread_duration_minutes'] = duration_minutes(post['thread_start'], post['thread_end'])

    # note: was thinking about calculating how many times a post is quoted, but decided
    # against it (for now)
    #for rank_thread in rank_threads:
        #for post in rank_thread:

def compute_features(posts, thread_lookup, all_posts=None):
    for post in posts:
        (post['term_count'], post['term_count_unique']) = term_counts(post['content_no_html'])
        (post['term_count_no_quotes'], post['term_count_no_quotes_unique']) = term_counts(post['content_no_quotes_no_html'])
        sel = Selector(text=post['content'])
        post['quotes_count'] = quotes_count(sel)
        sel_no_quotes = Selector(text=post['content_no_quotes'])
        post['hyperlink_count'] = hyperlink_count(sel_no_quotes)
        post['is_html'] = is_html_formatted(sel_no_quotes)
        post['contains_list'] = contains_list_html(sel_no_quotes)

    compute_thread_positions(posts, thread_lookup, all_posts)

if __name__ == "__main__":
    with open('xda_threads.json') as f:
        threads = json.load(f)
    with open('xda_rank_posts.json') as f:
        posts = json.load(f)

    thread_lookup = build_thread_lookup(threads)
    index_preprocess(posts, thread_lookup)
    compute_features(posts, thread_lookup)
    json.dump(posts, open('xda_rank_posts_features.json', 'w'), indent=2)