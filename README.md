![Coalman](https://github.com/kendog/coalman/blob/master/app/static/images/logo-medium.png)
=========

Coleman is an open-source content management, packaging and delivery microservice written in Python and Flask.

* Categorize, package and distribute your content.
* Create APIs for your front-end applications.

Installation
------------

1. Download or clone package.

2. Create a database for coalman on your web server, as well as a user who has all privileges for accessing and modifying it.

3. Find and rename `config-sample.py` to `config.py`, then edit the file and add your database/security configurations.

4. Install dependencies from `requirements.txt`.

5. Run flask migrate db (export FLASK_APP=main.py)

Development
-----------

To run the application for development execute `app.py` with the Python interpreter from the flask virtual environment.


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
