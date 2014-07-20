import simplejson as json
import random

with open('xda_posts.json', 'r') as f:
    posts = json.load(f)

random.seed(1461728916)
rank_posts = []
for i in range(250):
    while 42:
        index = random.randint(0, len(posts))
        if 'used' not in posts[index]:
            break
    rank_posts.append(posts[index])
    posts[index]['used'] = 1

for post in posts:
    post.pop('used', None)

json.dump(rank_posts, open('xda_rank_posts.json', 'w'), indent=2)
