This is the report a price project using a python framework "Flask"


Steps to activate the virtual environment (Windows)
$ venv\Scripts\activate
(venv) $ _

Set the FLASK_APP environment variable to reportaprice.com
(venv) $ set FLASK_APP=reportaprice.py

If you are setting up a new repository there are various dependencies that
need to be in place:

To install all of the dependencies: 
(venv) $ python -m pip install -r requirements.txt

To set up the database: 
(venv) $ flask db upgrade

The migration scripts in the "migrations" directory will set up the database
to the current state. Once everything is installed you can run the app locally using:

(venv) $ flask run

The site should be live on http://localhost:5000/
