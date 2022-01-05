from project.models import Post, User
from project import app, db
from datetime import datetime, timedelta

u1 = User.query.filter_by(username='john').first()
u2 = User.query.filter_by(username='susan').first()
u3 = User.query.filter_by(username='mary').first()
u4 = User.query.filter_by(username='david').first()


# db.session.add_all([u3, u4])
#
now = datetime.utcnow()
p1 = Post(body="post from john #3", author=u1,
          timestamp=now + timedelta(seconds=1))
p2 = Post(body="post from susan #3", author=u2,
          timestamp=now + timedelta(seconds=4))
p3 = Post(body="post from mary #3", author=u3,
          timestamp=now + timedelta(seconds=3))
p4 = Post(body="post from david #3", author=u4,
          timestamp=now + timedelta(seconds=2))
db.session.add_all([p1, p2, p3, p4])
db.session.commit()

# setup the followers
# u1.follow(u2)  # john follows susan
# u1.follow(u4)  # john follows david
# u2.follow(u3)  # susan follows mary
# u3.follow(u4)  # mary follows david
# db.session.commit()

# check the followed posts of each user
# f1 = u1.followed_posts().all()
# f2 = u2.followed_posts().all()
# f3 = u3.followed_posts().all()
# f4 = u4.followed_posts().all()
print(u1, p4)
# print(u2, f2)
# print(u3, f3)
# print(u4, f4)