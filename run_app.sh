# load env vars
#bash env.sh

# run_app.sh
export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=config.py

flask run
