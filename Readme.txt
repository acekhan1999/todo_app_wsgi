# to clone this app

git clone https://github.com/acekhan1999/todo_app_wsgi.git

# build docker file

docker build -t app .

# deploy container

docker run -itd -p 8000:8000 app

# open browser and open http://localhost:8000
