FROM python:3.10.16-alpine3.21

WORKDIR /app
COPY requirements.txt .
RUN \
    apk add --no-cache postgresql-libs libffi-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

COPY . .

EXPOSE 8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]