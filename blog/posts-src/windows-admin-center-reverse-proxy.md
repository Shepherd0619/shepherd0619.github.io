---
title: "WAC 反向代理配置"
date: 2026-03-02
source: https://blog.csdn.net/u012587406/article/details/156699031
categories: Windows Server
tags: [Windows Admin Center, 反向代理, IIS, ARR]
---
## 如何为 Windows Admin Center 配置 Apache 反向代理

### 概述

众所周知，Windows Admin Center (WAC) 是微软提供的强大的 Windows 
Server 
 管理工具，内网部署确实爽，但难免会有公网访问作为跳板机的需求，只可惜其反向代理情景下 limitation 之多（如频繁要求登录、不能在网站某个子目录下代理WAC），令人咂舌。

本文将介绍如何在 
Linux
 服务器上使用 Apache 配置反向代理，让 WAC 可以通过自定义域名和 Let’s Encrypt SSL 证书进行安全访问。

### 环境说明

- **反向代理服务器**: Linux (运行 Apache)
- **WAC 后端服务器**: 172.25.25.54:443，有内网证书，但是未加域的电脑无法信任证书。
- **域名**: wac.example.com
- **SSL 证书**: Let’s Encrypt

### 配置步骤

#### 1. 启用必要的 Apache 模块

首先需要确保启用了以下 Apache 模块：

```
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod headers
sudo a2enmod rewrite


bash
```

#### 2. 配置 VirtualHost

在 Apache SSL 配置文件中添加以下 VirtualHost 配置（通常是 `/etc/httpd/conf.d/ssl.conf` 或 `/etc/apache2/sites-available/ssl.conf`）：

#### 3. 配置说明

##### SSL 配置

- 使用 Let’s Encrypt 证书提供 HTTPS 加密
- `SSLProxyEngine on` 启用后端 SSL 代理
- 由于 WAC 使用自签名证书，需要禁用证书验证

##### 代理设置

- `ProxyPreserveHost on` - **关键设置**！保留原始 Host 头，让后端知道请求的域名
- `ProxyRequests off` - 禁用正向代理，只启用反向代理

##### NTLM 支持

```
SetEnv proxy-nokeepalive 0
SetEnv proxy-initial-not-pooled 1


apache
```

这两个设置对于 Windows 身份验证（NTLM）至关重要：

- 保持连接活跃，不使用 Keep-Alive
- 确保初始连接不使用连接池

##### WebSocket 支持

WAC 大量使用 WebSocket 进行实时通信，需要特殊的重写规则：

```
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteCond %{HTTP:Connection} upgrade [NC]
RewriteRule ^/(.*)$ wss://172.25.25.54:443/$1 [P,L]


apache
```

#### 4. 测试和重载配置

检查配置语法：

```
sudo apachectl configtest


bash
```

如果显示 “Syntax OK”，重载 Apache：

```
sudo systemctl reload httpd
# 或
sudo apachectl graceful


bash
```

#### 5. 防火墙配置

确保防火墙允许 443 端口：

```
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload


bash
```

### 常见问题排查

#### 问题 1: 访问显示 Apache 默认页面

**原因**: `ProxyPreserveHost` 设置为 `Off`

**解决方案**: 确保设置为 `ProxyPreserveHost on`，这样后端服务器才能收到正确的 Host 头。

#### 问题 2: WebSocket 连接失败

**症状**: WAC 部分功能无法使用，控制台显示 WebSocket 错误

**解决方案**:

1. 确保启用了 `proxy_wstunnel` 模块
2. 检查 WebSocket 重写规则是否正确配置

#### 问题 3: Windows 身份验证失败

**症状**: 无法登录或频繁要求输入凭据

**解决方案**: 确保设置了 NTLM 相关的环境变量：

```
SetEnv proxy-nokeepalive 0
SetEnv proxy-initial-not-pooled 1


apache
```

### 总结

通过以上配置，您可以成功地为 Windows Admin Center 配置 Apache 反向代理。关键点包括：

- ✅ 启用 SSL 和代理模块
- ✅ 配置 `ProxyPreserveHost on` 保留主机头
- ✅ 支持 NTLM 身份验证
- ✅ 启用 WebSocket 支持
- ✅ 使用 Let’s Encrypt 证书