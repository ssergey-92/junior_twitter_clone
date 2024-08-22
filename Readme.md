<h1 align="center">Junior Twitter Clone</h1>
<p align="center">
<img src="app_screenshot.png">
</p>

### Description  ###

This is social messenger is similar to former 'Twitter' with basic implemented 
functions. Where users can post, read and like twits of each other. 

### Functions ###

Any registered user can:
- Get a tweet feed sorted by the most popular tweets
- Post tweets with and without images
- Delete their own tweets
- Like and dislike tweets
- Follow and unfollow users
- View other users' profiles and their own profile

### Backend Stack ###

- Python 3.10
- FastAPI(async) 
- PostgreSQL and SQLAlchemy(async)
- NGINX + Gunicorn with Uvicorn workers
- Docker Compose
- Pytest
- mypy and wemake-python-styleguide(flake8 with different plugins)
- Swagger in YAML format, Docstring and Type hint 

### Getting started 

This app is easy to start. Follow  the bellow requirements for Linux (Ubuntu): 

#### Installation
Ignore the following steps if you have already installed Docker Compose, Python 3.10.12 and Git.

1. Install docker engine and compose plugin for it.   
- Follow steps from official site:  [Docker Engine Install](https://docs.docker.com/engine/install/ubuntu/) and [Docker Compose Install](https://docs.docker.com/compose/install/)

2. Install one of 
- Python 3.10.12 from official site:  [Python Downloads](https://www.python.org/downloads/)
- IDE (PyCharm or Visual Stidio Code or ...)

3. Install Git if required.
- Follow steps from official site: [Git install](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

#### Clone repository
From the command line: 
```
git clone https://github.com/ssergey-92/junior_twitter_clone.git
```

#### Running the application:

- From the command line: 
```
cd 'your path to project root directory'
python main.py
```
- From IDE
```
run main.py
```

You can also run linters by running 'run_linters.py' and pytests by running 'run_pytests.py'.

### Developers ###

Backend code was written by Sergey Solop.    
Contact email for suggestions and feedbacks: solop1992@mail.ru  
Frontend code was provided by Skillbox learning platform as a part of Python Course.  
Website: [Skillbox](https://skillbox.ru/)