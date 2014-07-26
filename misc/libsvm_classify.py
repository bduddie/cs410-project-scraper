from svmutil import *
import simplejson as json

model = svm_load_model('posts.model')

(y, x) = svm_read_problem('svm_input_full.txt')
(p_labels, p_acc, p_vals) = svm_predict(y, x, model)

with open('posts.json') as f:
    posts = json.load(f)

for label, post in zip(p_labels, posts):
    post['quality'] = label

with open('posts_classified.json', 'w') as f:
    json.dump(posts, f)