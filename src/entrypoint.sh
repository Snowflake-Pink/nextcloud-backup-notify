#!/bin/bash
set -e

# 启动cron服务
cron

# 输出当前时间和时区信息
echo "容器启动于 $(date)"
echo "当前时区: $(cat /etc/timezone)"
echo "下次检查时间：每天早上5:00 (中国时间) / 21:00 (UTC时间)"

# 测试cron配置是否正确
echo "当前cron配置："
crontab -l

# 如果需要立即执行一次
if [ "$RUN_ON_START" = "true" ]; then
  echo "立即执行检查..."
  /usr/local/bin/python /app/monitor.py
fi

# 持续输出cron日志
tail -f /var/log/cron.log 