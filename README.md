![Coalman](https://github.com/kendog/coalman/blob/master/application/static/images/logo-medium.png)
=========

Coleman is a microservice for managing and archiving (zip) files written in Python and Flask.

* Barebones CMS for managing and archiving (zip) files.
* JWT Authentication for APIs
* S3 Integration
  * Manage S3 objects
  * Stream S3 objects into zip archives.
* Performance Options:
  * In-memory zipper
  * Local caching
  

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

Default admin user credentials can be configured in `config.py`.
Change the password after login.
