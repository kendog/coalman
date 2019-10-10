![Coalman](https://github.com/kendog/coalman/blob/master/application/static/images/logo-medium.png)
=========

Coleman is an open-source file management, zipping and distribution microservice written in Python and Flask.

* Light-weight CMS with scalable taging system
* Create zip packages for distribution
* Email notifications
* APIs with JWT Authentication


Installation
------------
1. Create a database and user
2. Download or Clone Repo `git clone https://github.com/kendog/coalman`
3. Rename `config-sample.py` to `config.py`, then edit with your database/security configurations.
4. Create and activate python3 virtual environment
5. Install dependencies `pip install -r requirements.txt`.
6. Upgrade database `sh upgrade_db.sh`
7. Run the application `sh run_app.sh`
