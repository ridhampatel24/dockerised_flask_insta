FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
COPY . .
EXPOSE 5000
CMD flask db upgrade && gunicorn -b 0.0.0.0:5000 run:app
#CMD flask db upgrade && python3 run.py