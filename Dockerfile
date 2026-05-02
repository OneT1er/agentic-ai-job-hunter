# Stage 1: 依赖安装
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: 运行环境
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium && \
    playwright install-deps chromium

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
