FROM python:3.11-slim AS build

WORKDIR /youtube-watching
COPY ./app ./app
RUN pip install -r ./app/requirements.txt


FROM python:3.11-alpine

WORKDIR /youtube-watching
COPY --from=build /youtube-watching .
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
EXPOSE 5678

CMD ["python", "./app/main.py"]
