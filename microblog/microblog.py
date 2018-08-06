from app import app, db
from app.models import User, Post, Company, Service, Service_Attributes

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Company': Company, 'Service': Service, 'Service_Attributes': Service_Attributes}