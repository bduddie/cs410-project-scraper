import simplejson as json
import sys


def normalize(posts, keys):
    '''Performs min-max normalization of numerical features to [0,1]'''
    min = {}
    max = {}
    for key in keys:
        min[key] = sys.maxsize
        max[key] = -sys.maxsize - 1

    for post in posts:
        for key in keys:
            if post[key] < min[key]:
                min[key] = post[key]
            if post[key] > max[key]:
                max[key] = post[key]

    for post in posts:
        for key in keys:
            post[key] = (float(post[key]) - min[key]) / (max[key] - min[key])


def bool_to_int(posts, keys):
    for post in posts:
        for key in keys:
            if post[key]:
                post[key] = 1
            else:
                post[key] = 0

if __name__ == "__main__":
    with open('xda_posts_features.json') as f:
        posts = json.load(f)

    for post in posts:
        if post['thread_duration_minutes'] == 0:
            post['thread_duration_minutes'] = 1
        post['thread_views_per_minute'] = float(post['thread_view_count']) / post['thread_duration_minutes']
        post['thread_position'] = float(post['thread_position']) / post['thread_post_count']
        if 'quality' not in post:
            post['quality'] = 0

    bool_to_int(posts, ['contains_list', 'author_is_op', 'is_html'])

    if False: # normalized
        normalize(posts, ['term_count', 'term_count_unique', 'term_count_no_quotes', 'term_count_no_quotes_unique',
                      'thanks_count', 'hyperlink_count', 'quotes_count', 'thread_views_per_minute'])
        for post in posts:
            print('%d 1:%d 2:%d 3:%d 4:%f 5:%f 6:%f 7:%f 8:%f 9:%f 10:%f 11:%f 12:%f' %
                  (post['quality'], post['contains_list'], post['author_is_op'], post['is_html'],
                   post['term_count'], post['term_count_unique'], post['term_count_no_quotes'],
                   post['term_count_no_quotes_unique'], post['thanks_count'], post['hyperlink_count'],
                   post['quotes_count'], post['thread_position'], post['thread_views_per_minute']))
    else: # not normalized
        for post in posts:
            print('%d 1:%d 2:%d 3:%d 4:%d 5:%d 6:%d 7:%d 8:%d 9:%d 10:%d 11:%f 12:%f' %
                  (post['quality'], post['contains_list'], post['author_is_op'], post['is_html'],
                   post['term_count'], post['term_count_unique'], post['term_count_no_quotes'],
                   post['term_count_no_quotes_unique'], post['thanks_count'], post['hyperlink_count'],
                   post['quotes_count'], post['thread_position'], post['thread_views_per_minute']))