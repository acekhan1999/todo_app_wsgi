FROM python:3.8
COPY . /app
RUN pip install pymongo
RUN pip install pymongo[srv]
RUN pip install jinja2

WORKDIR /app

EXPOSE 8000
CMD [ "python", "app.py" ]
