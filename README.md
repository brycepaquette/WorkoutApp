# Strength & Fitness Workout Tracking App
#### Video Demo: https://youtu.be/cHuwDk4Itlo
#### Description: A Workout Tracking App built using Python's Flask Framework, Sqlite3, and Bootstrap. This is the Final Project Submission for CS50x, Harvard's Introduction to Computer Science Course.

#### Resources & Process:

Step 1 - Creating a database of exercises to choose from in the app
* Found a website Programmableweb.com which lead me to an API on RapidAPI.com
* This looks promising and rapidAPI gives you access to hundreds of APIs
* Fitness APIs: https://www.programmableweb.com/category/fitness/api
* ExerciseDB API: https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb/


--Create sqlite db
* how to Create Tables: https://www.sqlitetutorial.net/sqlite-create-table/
* sqlite datatypes: https://www.tutorialspoint.com/sqlite/sqlite_data_types.htm

--Load Exercises into the database
* need python sqlite3 module: https://docs.python.org/3/library/sqlite3.html
* sqlite browser GUI: https://sqlitebrowser.org/dl/
* Altering existing tables: https://www.sqlitetutorial.net/sqlite-alter-table/

Step 2 - Initializing a Flask App from Scratch
* Flask QuickStart: https://flask.palletsprojects.com/en/2.0.x/quickstart/
* Turned on debug mode: <$env:FLASK_ENV = "development"> https://flask.palletsprojects.com/en/2.0.x/quickstart/#debug-mode
* Debug app.py in vscode debugger: https://code.visualstudio.com/docs/python/tutorial-flask
* Template Inheritance: https://flask.palletsprojects.com/en/2.0.x/patterns/templateinheritance/
* Created layout.html as base template to extend from. Created index.html
* Manage dependencies by using pipreqs: <pipreqs --force --print> https://pypi.org/project/pipreqs/

Step 3 - Connecting to git and pulling/pushing
* CS50 Web Class on Git: https://cs50.harvard.edu/web/2020/notes/1/

Step 4 - Starting the Web App UI Design
* Freemium Icon Site: https://fontawesome.com/
* Free Icon Site: https://phosphoricons.com/ (No Python Flask support, need to use svg or png)
* Free App UI Designer Tool: https://framer.com/
* SVG formats can be copied into an html page for rendering. <img> tags don't work for this format

Step 5 - Adding Authentication
* Using flask login for authentication: https://flask-login.readthedocs.io/en/latest/ 
                                        https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
                                        https://pythonbasics.org/flask-login/
* Using flask-sqlalchemy to communicate with sqlite3 db: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
                                                         https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/#querying-records
* Flask Sessions feature: https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions
* Run this cmd to generate a secret key for sessions: <python -c 'import secrets; print(secrets.token_hex())'>
