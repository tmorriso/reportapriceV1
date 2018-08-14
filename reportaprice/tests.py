from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post, Company, Service

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)


    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    def test_service_add_company(self):
        # create service
        s1 = Service(parent_id=1, title='plumbing')
        s2 = Service(parent_id=2, title='electrical')
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

        # create company
        c1 = Company(company_name='Paint Team', company_address='123 Main St.',
         company_website='Paintteam.com', company_phone_number='2086783456', company_email='PaintTeam@example.com')
        c2 = Company(company_name='Bob Team', company_address='123 Main St.',
         company_website='Paintteam.com', company_phone_number='2086783456', company_email='PaintTeam@example.com')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()

        # add company to service
        check1 = s1.add_company(c1)
        db.session.commit()
        check2 = s2.add_company(c1)
        db.session.commit()

        # check that the connection was made
        self.assertEqual(c1.services.count(), 2)
        self.assertEqual(s1.companies.first().company_name, 'Paint Team')

        # remove companies
        check3 = s2.remove_company(c1)

        # check that it was removed
        self.assertEqual(c1.services.count(), 1)

        # add services to company
        check4 = c2.services.append(s1)

        # check that the connection was made
        self.assertEqual(c2.services.count(), 1)
        self.assertEqual(c2.services.first().title, 'plumbing')

    def test_service_posts(self):
        # create services
        s1 = Service(parent_id=1, title='plumbing')
        s2 = Service(parent_id=2, title='electrical')
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1)
        p2 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1)
        p3 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=2)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        # check service_posts function
        check1 = s1.service_posts()
        check2 = s2.service_posts()

        # check that the correct posts are returned
        self.assertEqual(check1.count(), 2)
        self.assertEqual(check2.count(), 1)

    def test_post_filter(self):
        # create company
        c1 = Company(id=1, company_name='Paint pods', company_address='Boise', company_zipcode='83706',
         company_website='Paintteam.com', company_phone_number='20867832', company_email='PaintTeam@example.com')
        c2 = Company(id=2, company_name='Bob Team', company_address='Salt Lake City', company_zipcode='81504',
         company_website='Paintteam.com', company_phone_number='2086783456', company_email='PaintTeam@example.com')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()

         # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create services
        s1 = Service(parent_id=1, title='plumbing')
        s2 = Service(parent_id=2, title='electrical')
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1, company_id=1)
        p2 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1, company_id=1)
        p3 = Post(body="Test post",
                  timestamp=now + timedelta(seconds=1), service_id=2, company_id=2)
        p4 = Post(body="test post",
                  timestamp=now + timedelta(seconds=1), service_id=2, company_id=2)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # check service_posts function
        check1 = u1.filter_posts(1, "Boise", "None", "None")
        

        # check that the correct posts are returned
        self.assertEqual(check1.count(), 2)

    def test_average(self):
        # create company
        c1 = Company(id=1, company_name='Paint pods', company_address='Boise', company_zipcode='83706',
         company_website='Paintteam.com', company_phone_number='20867832', company_email='PaintTeam@example.com')
        c2 = Company(id=2, company_name='Bob Team', company_address='Salt Lake City', company_zipcode='81504',
         company_website='Paintteam.com', company_phone_number='2086783456', company_email='PaintTeam@example.com')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()

         # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create services
        s1 = Service(parent_id=1, title='plumbing')
        s2 = Service(parent_id=2, title='electrical')
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1, company_id=1, price=35.0)
        p2 = Post(body="post from john",
                  timestamp=now + timedelta(seconds=1), service_id=1, company_id=1, price=36.0)
        p3 = Post(body="test post",
                  timestamp=now + timedelta(seconds=1), service_id=2, company_id=2, price=37.0)
        p4 = Post(body="test post",
                  timestamp=now + timedelta(seconds=1), service_id=2, company_id=2, price=38.0)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # check service_posts function
        posts = u1.filter_posts(1, "Boise", "None", "None")

        # check that the correct posts are returned
        self.assertEqual(posts.count(), 2)
        
        # check average
        average = u1.find_average(posts)

        # check that the correct posts are returned
        self.assertEqual(average, 35.5)
        




if __name__ == '__main__':
    unittest.main(verbosity=2)