# c22011528_cmt120_cw2



## Student Username

My username: c22011528

## URL of my website on the OpenShift

http://blog-c22011528.apps.openshift.cs.cf.ac.uk/


## Reference

- sd
- sad
- asd
- sad


## Installation
- Python 3.5+ environment.

## Quick Start Guide
1. Clone this repository.
2. Create a virtualenv and install the requirements. 
```bash
python venv venv 
pip install -r requirements.txt
```
3. Change the URL for database configuration in the `init.py`
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'Your database URI'
```
The database URI that should be used for the connection. Examples:
sqlite:////tmp/test.db
mysql://username:password@server/db

4. Set your MAIL_USERNAME and MAIL_PASSWORD to a valid Gmail account credentials (these will be used to send test emails) in `init.py`
5. Cd to your project directory and run the flask using following command 
```bash
flask run 
```
6. Go to http://localhost:5000/ and enjoy this application! Enjoy :)


