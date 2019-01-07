FROM python:2.7

MAINTAINER Andrew Steffano "andrew.steffano@gmail.com"

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY static/ /app/static
COPY app.py /app
COPY session.py /app
COPY helper.py /app
COPY templates/ /app/templates


ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
