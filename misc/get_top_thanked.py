import simplejson as json
from index_preprocess import *
from features import *

with open('xda_posts.json') as f:
    posts = json.load(f)

posts = sorted(posts, key=lambda k: len(k['thanks']), reverse=True)
top_posts = posts[0:1000]

with open('xda_threads.json') as f:
    thread_lookup = build_thread_lookup(json.load(f))

index_preprocess(top_posts, thread_lookup)
compute_features(top_posts, thread_lookup, posts)

top_posts_minus_op = []
for post in top_posts:
    if post['thread_position'] != 0 and (post['thread_position'] != 1 or not post['author_is_op']):
        top_posts_minus_op.append(post)

with open('xda_posts_top_100_thanked.json', 'w') as f:
    json.dump(top_posts_minus_op, f, indent=2)