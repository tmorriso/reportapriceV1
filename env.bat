@echo off
echo .....
echo .....
echo .....
echo "Setting up REPORTAPRICE project environment!"
echo .....

echo .....
set FLASK_APP=reportaprice.py
echo "FLASK_APP:"
echo %FLASK_APP%
echo .....

echo .....
set DATABASE_URL=postgres://tom:Chapo4hire!@localhost/reportaprice
echo "DATABASE_URL:"
echo %DATABASE_URL%
echo .....


echo .....
echo "Activating virtual environment"
echo .....
echo .....
echo .....
echo .....
venv\Scripts\activate
