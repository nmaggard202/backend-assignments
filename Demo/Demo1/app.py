from flask import Flask, request
import json

app = Flask(__name__)

posts = {
    0:{
        'id':0, 
        'upvotes':1, 
        'title':"My cat is the cutest!", 
        'link':"https://i.imgur.com/jseZqNK.jpg", 
        'username':"alicia98"
    }, 
    1:{
        'id':1, 
        'upvotes':3, 
        'title':"Cat loaf", 
        'link':"https://i.imgur.com/TJ46wX4.jpg", 
        'username':"alicia98"
        }
}

comments = {
    0:{
      "id": 0,
      "upvotes": 8,
      "text": "Wow, my first Reddit gold!",
      "username": "alicia98",
    }
}

posts_comments = {
    0:{
        "post_id":0,
        "comment_id":0
    }
}

post_current_id = 1
comment_current_id = 0

@app.route('/')
@app.route('/api/posts/')
def get_posts():
    """
    Gets all posts
    """
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200

@app.route("/api/posts/", methods=["POST"])
def create_post():
    """
    Creates a post

    title: post title
    link: post image URL
    username: poster username
    """
    global post_current_id
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    post_current_id+=1
    post = {'id':post_current_id, 'upvotes':1, 'title':title, 'link':link, 'username':username}
    posts[post_current_id] = post
    return json.dumps(post), 201

@app.route("/api/posts/<int:post_id>/")
def retrieve_post(post_id):
    """
    Returns specific post using post's id.
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    """
    Deletes a post.
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/comments/")
def retrieve_comments(post_id):
    """
    Retrieves a post's comments.
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    comments_res = {}
    comments_number = -1
    for x in posts_comments:
        pair = posts_comments.get(x)
        if pair["post_id"] == post_id:
            comment = comments.get(pair["comment_id"])
            comments_number+=1
            comments_res[comments_number] = comment
    res = {"comments": list(comments_res.values())}
    return json.dumps(res), 200

@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    """
    Creates a new comment.
    """
    global comment_current_id
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    comment_current_id+=1
    comment = {'id':comment_current_id, 'upvotes':1, 'text':text, 'username':username}
    comments[comment_current_id] = comment
    posts_comments[comment_current_id] = {'post_id':post_id, 'comment_id':comment_current_id}
    return json.dumps(comment), 201

@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["PUT"])
def update_comment(post_id, comment_id):
    comment = comments.get(comment_id)
    if comment is None:
        return json.dumps({"error":"Comment not found"}), 404
    body = json.loads(request.data)
    comment["text"]=body.get("text")
    return json.dumps(comment), 200

# Tier 1 Challenges

@app.route("/api/extra/posts/", methods=["POST"])
def create_post_t1():
    """
    Creates a post

    title: post title
    link: post image URL
    username: poster username
    """
    global post_current_id
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if type(title) != str or type(link) != str or type(username) != str:
        return json.dumps({"error":"Bad request"}), 400
    post_current_id+=1
    post = {'id':post_current_id, 'upvotes':1, 'title':title, 'link':link, 'username':username}
    posts[post_current_id] = post
    return json.dumps(post), 201

@app.route("/api/extra/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment_t1(post_id):
    """
    Creates a new comment.
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    global comment_current_id
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    if type(text) != str or type(username) != str:
        return json.dumps({"error":"Bad request"}), 400
    comment_current_id+=1
    comment = {'id':comment_current_id, 'upvotes':1, 'text':text, 'username':username}
    comments[comment_current_id] = comment
    posts_comments[comment_current_id] = {'post_id':post_id, 'comment_id':comment_current_id}
    return json.dumps(comment), 201

@app.route("/api/extra/posts/<int:post_id>/comments/<int:comment_id>/", methods=["PUT"])
def update_comment_t1(post_id, comment_id):
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    comment = comments.get(comment_id)
    if comment is None:
        return json.dumps({"error":"Comment not found"}), 404
    body = json.loads(request.data)
    if type(body.get("text")) != str:
        return json.dumps({"error":"Bad request"}), 400
    comment["text"]=body.get("text")
    return json.dumps(comment), 200

# Tier 2 Challenges
@app.route("/api/extra/posts/<int:post_id>/", methods=["POST"])
def update_upvotes(post_id):
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error":"Post not found"}), 404
    try:
        body = json.loads(request.data)
    except:
        post["upvotes"] = str(int(post["upvotes"])+1)
        return json.dumps(post), 200
    post["upvotes"] = str(int(post["upvotes"])+int(body["upvotes"]))
    return json.dumps(post), 200

@app.route("/api/extra/posts/", methods=["GET"])
def get_posts_sorted():
    """
    Gets all posts
    """
    args = request.args
    posts_list = posts.values()
    if args["sort"] == "increasing":
        list_res = sorted(posts_list, key=lambda x: x['upvotes'])
    if args["sort"] == "decreasing":
        list_res = sorted(posts_list, key=lambda x: x['upvotes'], reverse=True)
    res = {"posts": list_res}
    return json.dumps(res), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
