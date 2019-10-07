![Coalman](https://github.com/kendog/coalman/blob/master/app/static/images/logo-medium.png)
=========

Coleman is an open-source file management, zipping and distribution microservice written in Python and Flask.

* Built-in CMS and scalable taging system
* Create zip packages for distribution
* S3 Integration (Incomplete)
* Email notifications
* APIs for your front-end applications
  * Files: [GET] /api/v1/files
  * Tags: [GET] /api/v1/tags
  * Tag Groups: [GET] /api/v1/tag_groups
  * Create Package: [POST] /api/v1/request/package
  * Download Package: [GET] /download/package/<uuid>

Installation
------------
1. Download or clone package.
2. Create a database for coalman on your web server, as well as a user who has all privileges for accessing and modifying it.
3. Find and rename `config-sample.py` to `config.py`, then edit the file and add your database/security configurations.
4. Install dependencies from `requirements.txt`.
5. Set enviromental vars when for Flask-Migrate: 
   * `export FLASK_APP=main.py` (MAC/Linux)  
   * `set FLASK_APP = main.py` (WIN), 
   * `$env:FLASK_APP = main.py` (PowerShell)
6. Run `flask migrate db`.

Development
-----------
To run the application for development execute `main.py` with the Python interpreter from the flask virtual environment.
Example: `flask run`

Docker Deployment
-----------
1. docker build -f Dockerfile -t coalman:latest .
2. docker image ls
3. docker run -p 5001:5000 main

Kubernettes Deployment
-----------
1. kubectl version
2. kubectl config use-context docker-for-desktop
3. kubectl get nodes
4. kubectl apply -f deployment.yaml
5. kubectl get pods

Mod WSGI Deployment
----------
If you are deploying to an Apache server, `apache/coalman.wsgi` has been provided for mod_wsgi deployments.

Follow the mod_wsgi (Apache) instructions here:
http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/

Alternative deployment options:
http://flask.pocoo.org/docs/0.12/deploying/
