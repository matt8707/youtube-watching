FROM python:3.10-slim AS build

WORKDIR /youtube-watching
COPY ./app ./app
RUN pip install -r ./app/requirements.txt


FROM python:3.10-alpine

WORKDIR /youtube-watching
COPY --from=build /youtube-watching .
COPY --from=build /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
EXPOSE 5678

CMD ["python", "./app/main.py"]
