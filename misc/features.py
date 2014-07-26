from datetime import datetime
from index_preprocess import *
import re
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

def contains_list(post, sel):
    if (sel.xpath('//div')[0].xpath('.//ol | .//ul | .//li') or
                len(re.findall('\n\s*[\*\-]\s*[\w\-\.,:;\(\)]+', post['content_no_quotes_no_html'])) > 1):
        return True
    else:
        return False

def duration_minutes(start, end):
    start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
    end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
    delta = end - start
    return int(delta.total_seconds() / 60)

def compute_thread_positions(rank_posts, thread_lookup, all_posts=None):
    print('Compute thread-dependent features...')
    if all_posts == rank_posts:
        print('  Using per-thread iteration')
        rank_threads = {}
        for post in rank_posts:
            thread_id = post['thread_id']
            if thread_id not in rank_threads:
                rank_threads[thread_id] = thread_lookup[thread_id]
                rank_threads[thread_id]['posts'] = []
            rank_threads[thread_id]['posts'].append(post)

        for thread in rank_threads.itervalues():
            thread['posts'] = sorted(thread['posts'], key=lambda k: int(k['post_id']))
            index = 0
            thread_len = len(thread['posts'])
            op = thread['posts'][0]
            thread_start = op['date']
            thread_end = thread['posts'][-1]['date']
            thread_dur = duration_minutes(thread_start, thread_end)

            for post in thread['posts']:
                post['thread_position'] = index
                post['thread_post_count'] = thread_len
                if post['author'] == op['author']:
                    post['author_is_op'] = True
                else:
                    post['author_is_op'] = False
                post['thread_start'] = thread_start
                post['thread_end'] = thread_end
                post['thread_duration_minutes'] = thread_dur
                index += 1

    else:
        # This is for when we are processing a small subset of randomly selected posts
        print('  Using per-post iteration')
        if not all_posts:
            with open('xda_posts.json') as f:
                all_posts = json.load(f)

        # Build dictionary from thread ID --> {'thread': thread, 'posts': []} for relevant threads
        rank_threads = {}
        for post in rank_posts:
            if post['thread_id'] not in rank_threads:
                rank_threads[post['thread_id']] = thread_lookup[post['thread_id']]
                rank_threads[post['thread_id']]['posts'] = []

        # Populate post lists in rank_threads
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

def compute_features(posts, thread_lookup, all_posts=None):
    print('Compute individual features...')
    for post in posts:
        (post['term_count'], post['term_count_unique']) = term_counts(post['content_no_html'])
        (post['term_count_no_quotes'], post['term_count_no_quotes_unique']) = term_counts(post['content_no_quotes_no_html'])
        sel = Selector(text=post['content'])
        post['quotes_count'] = quotes_count(sel)
        sel_no_quotes = Selector(text=post['content_no_quotes'])
        post['hyperlink_count'] = hyperlink_count(sel_no_quotes)
        post['is_html'] = is_html_formatted(sel_no_quotes)
        post['contains_list'] = contains_list(post, sel_no_quotes)

    compute_thread_positions(posts, thread_lookup, all_posts)

if __name__ == "__main__":
    print('Parsing JSON...')
    with open('xda_threads.json') as f:
        threads = json.load(f)
    with open('xda_posts_index.json') as f:
        posts = json.load(f)

    thread_lookup = build_thread_lookup(threads)
    #index_preprocess(posts, thread_lookup)
    compute_features(posts, thread_lookup, posts)
    print('Saving JSON...')
    json.dump(posts, open('xda_posts_features.json', 'w'), indent=2)