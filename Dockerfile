FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python python-dev python-pip chromium-chromedriver
RUN python -m pip install requests bs4 selenium
CMD python app/scrapper.py


