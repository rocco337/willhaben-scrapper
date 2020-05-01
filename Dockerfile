FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python python-dev python-pip chromium-chromedriver
RUN python -m pip install requests bs4 selenium
COPY . /
CMD python /scrapper.py
#CMD tail -f /dev/null

