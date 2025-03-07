FROM python:3.10-slim

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/monitor.py .
COPY src/entrypoint.sh .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    chmod +x /app/entrypoint.sh && \
    chmod +x /app/monitor.py

# 修复：使用python的完整路径
RUN echo "0 5 * * * /usr/local/bin/python /app/monitor.py >> /var/log/cron.log 2>&1" > /etc/cron.d/backup-check && \
    chmod 0644 /etc/cron.d/backup-check && \
    crontab /etc/cron.d/backup-check && \
    touch /var/log/cron.log

# 使用入口脚本启动cron服务，并保持容器运行
ENTRYPOINT ["/app/entrypoint.sh"] 