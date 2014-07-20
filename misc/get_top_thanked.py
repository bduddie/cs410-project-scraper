import simplejson as json
from index_preprocess import *
from features import *

with open('xda_posts.json') as f:
    posts = json.load(f)

posts = sorted(posts, key=lambda k: len(k['thanks']), reverse=True)
top_posts = posts[0:100]

with open('xda_threads.json') as f:
    thread_lookup = build_thread_lookup(json.load(f))

index_preprocess(top_posts, thread_lookup)
compute_features(top_posts, thread_lookup, posts)

with open('xda_posts_top_100_thanked.json', 'w') as f:
    json.dump(top_posts, f, indent=2)