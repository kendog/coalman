![Coalman](https://github.com/kendog/coalman/blob/master/app/static/images/logo-medium.png)
=========

Coleman is an open-source file management, zipping and distribution microservice written in Python and Flask.

* Built-in CMS and scalable taging system
* Create zip packages for distribution
* S3 Integration (Incomplete)
* Email notifications
* APIs for your front-end applications
  * Files: [GET] `/api/v1/files`
  * Tags: [GET] `/api/v1/tags`
  * Tag Groups: [GET] `/api/v1/tag_groups`
  * Create Package: [POST] `/api/v1/request/package`
  * Download Package: [GET] `/download/package/<uuid>`

Installation
------------
1. Create a database and user
2. Download or Clone Repo `git clone https://github.com/kendog/coalman`
3. Find and rename `config-sample.py` to `config.py`, then edit the file and add your database/security configurations.
4. Create and Activate Virtual Environment
5. Install dependencies `pip install -r requirements.txt`.
6. Upgrade database `sh upgrade_db.sh`
7. Run the application `sh run_app.sh`
