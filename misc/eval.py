import simplejson as json
import webbrowser

print("""
Please follow these guidelines when ranking posts:
  1 - adds nothing to discussion (off-topic, spam, "lolwut", lone smiley, etc.)
  2 - common in conversation but not otherwise worthwhile ("It worked", "Thanks", etc.)
  3 - asks a relevant question or provides a typical answer ("I tried doing this
      but it doesn't work", "Try this, it worked for me", etc.)
  4 - provides an authoritative answer or useful original content
  5 - very important or useful post (FAQ, software release announcement, etc.)
""")

with open('xda_eval.json') as f:
    posts = json.load(f)

quit = False
index = 0
for post in posts:
    index += 1
    if 'user_quality' in post:
        continue

    print("Opening %s" % post['url'])
    webbrowser.open(post['url'])

    while 42:
        print("Please provide a quality ranking for post %s (by %s) [%d / %d]" %
              (post['post_id'], post['author'], index, len(posts)))
        value = raw_input("(1-5), or Q to quit: [3] ")

        if not value:
            value = "3"

        value = str(value).upper()
        if value == "Q":
            quit = True
            break
        else:
            try:
                value = int(value)
                if 1 <= value <= 5:
                    post['user_quality'] = value
                    break
                else:
                    print("Out of expected range, try again")
            except ValueError:
                print("Not a valid number or 'Q', try again")
    if quit:
        break

json.dump(posts, open('xda_eval.json', 'w'), indent=2)
