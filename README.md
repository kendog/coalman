![Coalman](https://github.com/kendog/coalman/blob/master/application/static/images/logo-medium.png)
=========

Coleman is a zip packaging and distribution microservice written in Python and Flask.

* File management with scalable taging
* S3 Integration
* Stream S3 objects directly to Zip (no disk required)
* In-memory Zip packaging (no disk required)
* APIs with JWT Authentication


Installation
------------
1. Create a database and user
2. Create S3 Bucket and credentials (optional)
3. Download or Clone Repo `git clone https://github.com/kendog/coalman`
4. Rename `config-sample.py` to `config.py`, then edit with your database/security configurations.
5. Create and activate python3 virtual environment
6. Install dependencies `pip install -r requirements.txt`.
7. Upgrade database `sh upgrade_db.sh`
8. Run the application `sh run_app.sh`
