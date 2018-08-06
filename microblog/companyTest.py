from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post, Company, Service

# create service
s1 = Service(parent_id=1, title='Fence Painting')
db.session.add(s1)
db.session.commit()

# create company
c1 = Company(company_name='Paint Team', company_address='123 Main St.',
 company_website='Paintteam.com', company_phone_number='2086783456', company_email='PaintTeam@example.com')
db.session.add(c1)
db.session.commit()

# add company to service
#check1 = s1.add_company(c1)
check1 = s1.companies.append(c1)
db.session.commit()

