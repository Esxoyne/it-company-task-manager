FROM python:3.14-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password django-user

COPY . .

RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/staticfiles && \
    chown -R django-user:django-user /app

ENTRYPOINT ["/app/entrypoint.sh"]
USER django-user
