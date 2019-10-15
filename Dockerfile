# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3

LABEL Name=cloud-photo-gallery Version=0.0.1

WORKDIR /app
ADD . /app
#COPY . /app

#for windows containers & heroku(?)
# Using pip:
RUN py -3 -m pip install --upgrade pip
RUN py -3 -m pip install -r requirements.txt
CMD ["py", "-3", "runserver.py"]

#for linux containers
# Using pip:
#RUN pip install --upgrade pip
#RUN python3 -m pip install -r requirements.txt
#CMD ["python3", "runserver.py"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "cloud-photo-gallery"]

