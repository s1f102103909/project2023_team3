FROM python:3.10

COPY . /opt/project2023_team3
WORKDIR /opt/project2023_team3

RUN apt-get update
RUN pip install --upgrade wheel
RUN pip install -U alkana
RUN apt -y update && apt -y upgrade
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN apt -y install libopencv-dev
RUN pip install -r requirements.txt

RUN python3 manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]