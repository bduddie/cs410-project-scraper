import simplejson as json
import webbrowser

print("""
Please follow these guidelines when ranking posts:
  1 - adds nothing to discussion (off-topic, spam, "lolwut", etc.)
  2 - necessary in conversation but not otherwise worthwhile ("It worked", etc.)
  3 - asks a relevant question or provides a typical answer ("I tried doing this
      but it doesn't work", "Try this, it worked for me", etc.)
  4 - provides an authoritative answer or useful original content
  5 - very important or useful post (FAQ, etc.)
""")

with open('xda_threads.json') as f:
    threads = json.load(f)
with open('xda_rank_posts.json') as f:
    posts = json.load(f)

thread_lookup = {}
for thread in threads:
    thread_lookup[thread['thread_id']] = thread

quit = False
index = 0
for post in posts:
    index += 1
    if 'quality' in post:
        continue

    if not post['content_no_quotes_no_html']:
        print("Removing post since no original, non-HTML content")
        posts.remove(post)
        continue

    thread = thread_lookup[post['thread_id']]
    url = 'http://forum.xda-developers.com%s/post%s' % (thread['link'], post['post_id'])
    print("Opening", url)
    webbrowser.open(url)

    while 42:
        print("Please provide a quality ranking for post %s (by %s) [%d / %d]" %
              (post['post_id'], post['author'], index, len(posts)))
        value = input("(1-5), or Q to quit: [3] ")

        if not value:
            value = "3"

        value = value.upper()
        if value == "Q":
            quit = True
            break
        else:
            try:
                value = int(value)
                if 1 <= value <= 5:
                    post['quality'] = value
                    break
                else:
                    print("Out of expected range, try again")
            except ValueError:
                print("Not a valid number or 'Q', try again")
    if quit:
        break

json.dump(posts, open('xda_rank_posts.json', 'w'), indent=2)

