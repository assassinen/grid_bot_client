from flask import Blueprint
from project import app, db
from project.models import User, Post

# main = Blueprint('main', __name__)
#
# app = create_app()

if __name__ == '__main__':
    # u = User(username='susan', email='susan@example.com')
    # db.session.add(u)
    # db.session.commit()
    # print(u)

    u = User.query.get(1)
    # print(u)
    # p = Post(body='my first post!', author=u)
    # db.session.add(p)
    # db.session.commit()
    posts = u.posts.all()
    print(posts)