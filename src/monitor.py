#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import docker
import re
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN')
PUSHPLUS_TOPIC = os.getenv('PUSHPLUS_TOPIC')
CONTAINER_NAME = os.getenv('DOCKER_CONTAINER', 'nextcloud-aio-borgbackup')
PUSHPLUS_URL = 'https://www.pushplus.plus/send'

def get_container_logs():
    """获取指定容器的日志"""
    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)
        logs = container.logs().decode('utf-8')
        return logs
    except Exception as e:
        print(f"获取容器日志失败: {e}")
        return None

def parse_backup_info(logs):
    """解析备份日志中的关键信息"""
    result = {
        "success": False,
        "archive_name": "",
        "start_time": "",
        "end_time": "",
        "duration": "",
        "original_size": "",
        "compressed_size": "",
        "deduplicated_size": "",
        "pruned_data": "",
        "error": ""
    }
    
    # 检查是否成功完成
    if "Backup finished successfully" in logs:
        result["success"] = True
        
        # 提取存档名称
        archive_match = re.search(r'Archive name: ([\w\d_-]+)', logs)
        if archive_match:
            result["archive_name"] = archive_match.group(1)
        
        # 提取时间信息
        start_time_match = re.search(r'Time \(start\): ([^\n]+)', logs)
        if start_time_match:
            result["start_time"] = start_time_match.group(1)
            
        end_time_match = re.search(r'Time \(end\): ([^\n]+)', logs)
        if end_time_match:
            result["end_time"] = end_time_match.group(1)
            
        duration_match = re.search(r'Duration: ([^\n]+)', logs)
        if duration_match:
            result["duration"] = duration_match.group(1)
        
        # 提取大小信息
        original_size_match = re.search(r'This archive:\s+(\d+\.\d+ \w+)', logs)
        if original_size_match:
            result["original_size"] = original_size_match.group(1)
            
        compressed_size_match = re.search(r'This archive:\s+\d+\.\d+ \w+\s+(\d+\.\d+ \w+)', logs)
        if compressed_size_match:
            result["compressed_size"] = compressed_size_match.group(1)
            
        deduplicated_size_match = re.search(r'This archive:\s+\d+\.\d+ \w+\s+\d+\.\d+ \w+\s+(\d+\.\d+ \w+)', logs)
        if deduplicated_size_match:
            result["deduplicated_size"] = deduplicated_size_match.group(1)
            
        # 提取删除数据信息
        pruned_match = re.search(r'Deleted data:\s+[^\n]+\s+[^\n]+\s+([^\n]+)', logs)
        if pruned_match:
            result["pruned_data"] = pruned_match.group(1)
    else:
        # 检查是否有错误信息
        result["success"] = False
        error_lines = []
        for line in logs.splitlines():
            if "error" in line.lower() or "fail" in line.lower() or "exception" in line.lower():
                error_lines.append(line)
        
        if error_lines:
            result["error"] = "\n".join(error_lines)
        else:
            result["error"] = "备份可能未完成或日志信息不完整"
    
    return result

def format_message(backup_info, full_logs=None):
    """根据备份信息格式化消息内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if backup_info["success"]:
        content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 5px;">
            <h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">Nextcloud 备份成功 ✅</h2>
            <p style="color: #666;">检查时间: {now}</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="margin-top: 0; color: #333;">备份详情</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; width: 40%;"><strong>存档名称:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["archive_name"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>开始时间:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["start_time"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>结束时间:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["end_time"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>耗时:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["duration"]}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="margin-top: 0; color: #333;">存储信息</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; width: 40%;"><strong>原始大小:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["original_size"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>压缩大小:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["compressed_size"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>去重大小:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["deduplicated_size"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>清理数据:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{backup_info["pruned_data"]}</td>
                    </tr>
                </table>
            </div>
            
            <p style="color: #4CAF50; font-weight: bold;">备份已成功完成并验证！</p>
        </div>
        """
    else:
        content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 5px;">
            <h2 style="color: #F44336; border-bottom: 2px solid #F44336; padding-bottom: 10px;">Nextcloud 备份失败 ❌</h2>
            <p style="color: #666;">检查时间: {now}</p>
            
            <div style="background-color: #fff9f9; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #ffcdd2;">
                <h3 style="margin-top: 0; color: #d32f2f;">错误信息</h3>
                <pre style="background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow: auto; white-space: pre-wrap; word-wrap: break-word;">{backup_info["error"]}</pre>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="margin-top: 0; color: #333;">完整日志</h3>
                <pre style="background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow: auto; max-height: 300px; white-space: pre-wrap; word-wrap: break-word;">{full_logs if full_logs else "无法获取完整日志"}</pre>
            </div>
            
            <p style="color: #F44336; font-weight: bold;">请检查备份系统并尝试修复问题！</p>
        </div>
        """
    
    return content

def send_notification(title, content):
    """发送通知到pushplus"""
    try:
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "html",
            "topic": PUSHPLUS_TOPIC
        }
        
        response = requests.post(PUSHPLUS_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print(f"通知发送成功: {result.get('msg', '未知')}")
                return True
            else:
                print(f"通知发送失败: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"通知发送失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"发送通知时出错: {e}")
        return False

def main():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 开始检查 {CONTAINER_NAME} 容器的备份状态...")
    
    # 检查必要的环境变量
    if not PUSHPLUS_TOKEN:
        print("错误: 未设置PUSHPLUS_TOKEN环境变量")
        return
    
    # 获取日志
    logs = get_container_logs()
    
    if not logs:
        title = "⚠️ Nextcloud 备份状态未知"
        content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 5px;">
            <h2 style="color: #FF9800; border-bottom: 2px solid #FF9800; padding-bottom: 10px;">Nextcloud 备份状态未知 ⚠️</h2>
            <p style="color: #666;">检查时间: {current_time}</p>
            <p>无法获取备份容器的日志。可能的原因：</p>
            <ul>
                <li>备份容器未运行</li>
                <li>容器名称配置错误</li>
                <li>权限问题导致无法访问容器日志</li>
            </ul>
            <p style="color: #FF9800; font-weight: bold;">请检查备份系统状态！</p>
        </div>
        """
        send_notification(title, content)
        return
    
    # 解析备份信息
    backup_info = parse_backup_info(logs)
    
    # 根据结果发送通知
    if backup_info["success"]:
        title = "✅ Nextcloud 备份成功"
        content = format_message(backup_info)
    else:
        title = "❌ Nextcloud 备份失败"
        content = format_message(backup_info, logs)
    
    send_notification(title, content)
    print(f"[{current_time}] 检查完成，通知已发送")

if __name__ == "__main__":
    main() 