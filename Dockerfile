FROM python:3.9.2

WORKDIR /cxpoolmon

COPY requirements.txt .
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /cxpoolmon/requirements.txt \
   && rm -rf /cxpoolmon/requirements.txt

COPY src/ .

CMD [ "python", "-u", "monitor.py" ]
