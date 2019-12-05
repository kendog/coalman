![Coalman](https://github.com/kendog/coalman/blob/master/application/static/images/logo-medium.png)
=========

Coleman is a Headless CMS Microservice for S3 written in Python/Flask.

* Light-weight CMS for managing and archiving (zip) files.
* Access to content via JWT Authenticated REST APIs.
* S3 Integration
  * Manage S3 objects
  * Stream S3 objects into zip archives.
* Local Disk Option (non-scaling instances).
* Performance Options:
  * In-memory zipper
  * Local caching


Requirements
------------
* Python3
* PostgreSQL


Installation
------------
1. Create PostgreSQL database and user
2. Create S3 Bucket and credentials (optional)
3. Download or Clone Repo `git clone https://github.com/kendog/coalman`
4. Edit `config.py` with your database/security configurations.
5. Create and activate python3 virtual environment
6. Install dependencies `pip install -r requirements.txt`.
7. Update database `sh db_upgrade.sh`
8. Run the application `sh run_app.sh`

Default admin user credentials can be configured in `config.py`.
Change the password after login.
