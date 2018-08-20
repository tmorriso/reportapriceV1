This is the report a price project using a python framework "Flask"


Steps to activate the virtual environment (Windows)
$ venv\Scripts\activate
(venv) $ _

(venv) $ set FLASK_APP=microblog.py

If you are setting up a new repository there are various dependencies that
need to be in place and the database must be set up...

The migration scripts in the "migrations" directory will set up the database
automatically to the current state. Once everything is installed you can run:

(venv) $ flask db upgrade 

To run the app use the command:

(venv) $ flask run

The site should be live on http://localhost:5000/
