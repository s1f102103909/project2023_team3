FROM python:3.10

COPY . /opt/project2023_team3
WORKDIR /opt/project2023_team3

RUN pip install -r requirements.txt
RUN pip install --upgrade wheel
RUN pip install -U alkana
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]