FROM apache/airflow:2.9.2-python3.10

COPY requirements.txt /requirements.txt
COPY embedded_dags /opt/airflow/dags

RUN pip install --upgrade pip
RUN pip install  -r /requirements.txt
