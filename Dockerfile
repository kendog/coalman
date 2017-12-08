FROM python:2.7
ADD . /coalman
WORKDIR /coalman
EXPOSE 5000
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]


FROM python:2.7

EXPOSE 5000

RUN mkdir /coalman
WORKDIR /coalman

COPY requirements.txt /coalman/requirements.txt
RUN pip install -r requirements.txt

COPY . /coalman

CMD python app.py