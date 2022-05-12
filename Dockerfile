FROM python:3.9
WORKDIR /usr/src
RUN mkdir /tmp/out/
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY src/* ./
COPY src/serials/ ./serials/
ENTRYPOINT [ "python", "." ]
CMD ["-h"]
