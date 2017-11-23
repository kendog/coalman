FROM python:3.6
ADD . /coalman
WORKDIR /coalman
EXPOSE 5000
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "app.py"]