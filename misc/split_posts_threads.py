import json

with open('xda_all.json') as f:
    items = json.load(f)

posts = []
threads = []
for item in items:
    if "post_id" in item:
        posts.append(item)
    else:
        threads.append(item)

json.dump(posts, open('xda_posts.json', 'w'))
json.dump(threads, open('xda_threads.json', 'w'))