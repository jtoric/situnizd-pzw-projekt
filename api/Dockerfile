# Slika backenda: Python, paketi iz requirements.txt i kod aplikacije (docker-compose.prod.yml)
FROM python:3.13-slim

# Ispis ide odmah u zapis kontejnera, bez međuspremnika; Python ne piše .pyc datoteke
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Paketi prije koda: Docker sloj s paketima ponovno koristi dok se requirements.txt ne
# promijeni, pa izmjena koda ne pokreće ponovnu instalaciju
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Proces ne radi kao root: tko probije aplikaciju, nema prava nad cijelim kontejnerom
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

# Migracije prije pokretanja: nova inačica koda ne prima zahtjeve nad starom shemom.
# exec: uvicorn preuzima mjesto ljuske, pa signal za zaustavljanje stiže njemu.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
