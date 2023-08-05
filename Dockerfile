FROM python:3.11

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

RUN pip3 install geos

EXPOSE 8501

COPY . /app

ENTRYPOINT [ "streamlit", "run" ]

CMD [ "HOME.py" ]