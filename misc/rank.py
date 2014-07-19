import json
import webbrowser

print("""
Please follow these guidelines when ranking posts:
  Low - does not add to the discussion (spam, off-topic, no real content, etc.)
  Medium - moves the discussion forward but is not otherwise helpful (e.g. asks a relevant question)
  High - important post in the thread; contributes useful information that a reader browsing through the thread should see

""")

with open('xda_threads.json') as f:
    threads = json.load(f)
with open('xda_rank_posts.json') as f:
    posts = json.load(f)

thread_lookup = {}
for thread in threads:
    thread_lookup[thread['thread_id']] = thread

quit = False
for post in posts:
    if 'quality' in post:
        continue

    thread = thread_lookup[post['thread_id']]
    url = 'http://forum.xda-developers.com%s/post%s' % (thread['link'], post['post_id'])
    print("Opening", url)
    webbrowser.open(url)

    while 42:
        print("Please provide a quality ranking for post %s (by %s)" % (post['post_id'], post['author']))
        value = input("(0,1,2|L,M,H), or Q to quit: [M] ")
        if not value:
            value = "M"
        elif value == "0":
            value = "L"
        elif value == "1":
            value = "M"
        elif value == "2":
            value = "H"

        value = value.upper()
        if value == "Q":
            quit = True
            break
        elif value != "L" and value != "M" and value != "H":
            print("Unrecognized input '" + value + "' - please enter L, M, or H (case insensitive)")
        else:
            post['quality'] = value
            break
    if quit:
        break

json.dump(posts, open('xda_rank_posts.json', 'w'), indent=2)

