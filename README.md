# c22011528_cmt120_cw2



## Student Username

My username: c22011528

## URL of my website on the OpenShift

http://blog-c22011528.apps.openshift.cs.cf.ac.uk/


## Reference

- Bootstrap (no date) Bootstrap · The most popular HTML, CSS, and JS library in the world. Available at: https://getbootstrap.com/ (Accessed: January 22, 2023).
- Create A Flask Blog - Flask Friday (2021) YouTube. YouTube. Available at: https://www.youtube.com/watch?v=0Qxtt4veJIc&amp;list=PLCC34OHNcOtolz2Vd9ZSeSXWc8Bq23yEz (Accessed: January 1, 2023). 
- Flask-Ckeditor (no date) Flask. Available at: https://flask-ckeditor.readthedocs.io/en/latest/ (Accessed: January 22, 2023).
- Flask-Login (no date) Flask. Available at: https://flask-login.readthedocs.io/en/latest/ (Accessed: January 22, 2023).
- Flask-Mail (no date) flask-mail - Flask-Mail 0.9.1 documentation. Available at: https://pythonhosted.org/Flask-Mail/ (Accessed: January 22, 2023).
- Flask-Migrate (no date) Flask. Available at: https://flask-migrate.readthedocs.io/en/latest/ (Accessed: January 22, 2023). 
- Flask-Sqlalchemy (no date) Flask. Available at: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/ (Accessed: January 22, 2023). 
- Flask-WTF (no date) Flask. Available at: https://flask-wtf.readthedocs.io/en/1.0.x/ (Accessed: January 22, 2023).
- Free icons, clipart illustrations, photos, and Music (no date) Free Icons, Clipart Illustrations, Photos, and Music. Available at: https://icons8.com/ (Accessed: January 22, 2023). 
- Google font for developer (no date) Google fonts. Google. Available at: https://fonts.google.com/ (Accessed: January 22, 2023). 
- Grinberg, M. (no date) Blog.miguelgrinberg.com, miguelgrinberg.com. Available at: https://blog.miguelgrinberg.com/ (Accessed: January 22, 2023).
- Pillow (Python Imaging Library) (no date) Pillow (PIL Fork). Available at: https://pillow.readthedocs.io/en/stable/ (Accessed: January 22, 2023). 
- PyJWT (python jwt library) (no date) Welcome to PyJWT - PyJWT 2.6.0 documentation. Available at: https://pyjwt.readthedocs.io/en/latest/ (Accessed: January 22, 2023). 
- ReCAPTCHA v2 &nbsp;|&nbsp; google developers (no date) Google. Google. Available at: https://developers.google.com/recaptcha/docs/display (Accessed: January 22, 2023). 
- Sending emails with flask - step-by-step Flask-Mail Guide: Mailtrap blog (2023) Mailtrap. Available at: https://mailtrap.io/blog/flask-email-sending/ (Accessed: January 10, 2023). 
- Unsplash (no date) Beautiful free images &amp; pictures, Unsplash. Available at: https://unsplash.com/ (Accessed: January 22, 2023).
- Vanta.js - 3D &amp; webgl background animations for your website (no date) Animated 3D Backgrounds For Your Website. Available at: https://www.vantajs.com/ (Accessed: January 22, 2023). 


## Installation
- Python 3.5+ environment.

## Quick Start Guide
1. Clone this repository.
2. Create a virtualenv and install all dependencies in `requirement.txt`. 
```bash
python venv venv 
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


