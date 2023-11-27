# Flask Personal Portfolio with blog

## Installation
- Python 3.5+ environment.

## Quick Start Guide
1. Clone this repository.
2. Create a virtualenv and install all dependencies in `requirement.txt`. 
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Change the URL for database configuration in the `init.py`
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'Your database URI'
```
The database URI that should be used for the connection. 

Examples:
```
sqlite:////tmp/test.db
mysql://username:password@server/db
```

4. Set your MAIL_USERNAME and MAIL_PASSWORD to a valid Gmail account credentials (these will be used to send test emails) in `init.py`
5. Cd to your project directory and run the flask using following command 
```bash
$ flask --app wsgi run
```
6. Go to http://localhost:5000/ and enjoy this application! Enjoy :)


