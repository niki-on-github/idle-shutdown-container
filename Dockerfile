FROM nvidia/cuda:12.3.0-base-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip python3 software-properties-common
RUN pip install --no-cache-dir psutil pynvml

COPY monitor.py /monitor.py

CMD ["python3", "-u", "/monitor.py"]
