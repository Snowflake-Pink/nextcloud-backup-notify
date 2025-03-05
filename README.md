# Nextcloud Backup Notification

一个简单的工具，用于监控 nextcloud-aio-borgbackup 容器的备份日志，并通过 PushPlus 发送备份状态通知。

## 功能

- 每天早上 5 点自动检查 nextcloud-aio-borgbackup 容器的日志
- 提取关键备份信息：存档名称、时间、大小等
- 格式化信息并通过 PushPlus 推送到微信
- 如有错误，自动发送完整日志

## 安装与使用

### 前提条件

- Docker 和 Docker Compose 已安装
- PushPlus 账号和 Token（可从 [PushPlus官网](https://www.pushplus.plus) 获取）
- Nextcloud AIO 已安装并配置了 borgbackup 容器

### 安装步骤

1. 克隆本仓库：

```bash
git clone https://github.com/yourusername/nextcloud-backup-notify.git
cd nextcloud-backup-notify
```

2. 创建环境配置文件：

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，填入您的 PushPlus Token 和群组编码：

```
PUSHPLUS_TOKEN=your_pushplus_token_here
PUSHPLUS_TOPIC=your_pushplus_topic_here
```

4. 构建并启动容器：

```bash
docker-compose up -d
```

### 手动测试

要手动测试通知是否正常工作，可以执行：

```bash
docker exec nextcloud-backup-notify python /app/backup_notify.py
```

## 自定义

如需更改通知时间，请编辑 `Dockerfile` 中的 cron 表达式：

```dockerfile
# 默认为每天早上 5 点运行
echo "0 5 * * * cd /app && python /app/backup_notify.py >> /var/log/cron.log 2>&1"
```

## 故障排除

如果遇到问题：

1. 检查容器日志：

```bash
docker logs nextcloud-backup-notify
```

2. 确认 nextcloud-aio-borgbackup 容器可访问且正在运行
3. 验证 PushPlus Token 是否正确
4. 确保 docker.sock 已正确挂载

## 注意事项

- 本工具需要访问 Docker socket，请确保安全考虑
- 请保管好您的 PushPlus Token 