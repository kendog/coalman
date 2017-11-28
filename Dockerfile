FROM python:2.7
ADD . /coalman
WORKDIR /coalman
EXPOSE 5000
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]