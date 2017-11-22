![alt text](https://github.com/kendog/coalman/blob/master/static/images/logo.png)

coalman
=========

A document management, packaging and distribution service for your organization written in Python and Flask.

* Manage and categorize your documents with a customizable tagging system.
* Package and distribute groups of documents to end-users -or- send them to the self-service portal.
* APIs for custom web and mobile applications.

Installation
------------

1. Download or clone package.

2. Create a database for coalman on your web server, as well as a user who has all privileges for accessing and modifying it.

3. Find and rename `config-sample.py` to `config.py`, then edit the file and add your database/security configurations.

4. Install dependencies from `requirements.txt`.

5. Create db...  script TBD...

Development
-----------

To run the application for development execute `app.py` with the Python interpreter from the flask virtual environment.

Production
----------

If you are deploying to an Apache server, `coalman.wsgi` has been provided for mod_wsgi deployments.

Follow the mod_wsgi (Apache) instructions here:
http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/

Alternative deployment options:
http://flask.pocoo.org/docs/0.12/deploying/