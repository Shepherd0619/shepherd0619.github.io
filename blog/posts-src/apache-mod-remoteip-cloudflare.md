---
title: "Apache 使用 mod_remoteip 恢复 Cloudflare 后的真实访客 IP"
date: 2026-06-16
source: https://blog.csdn.net/u012587406/article/details/162042087
categories: IT 运维
tags: [Apache, Cloudflare, mod_remoteip, 运维]
---
### 前言

当你的网站使用 Cloudflare CDN 时，Apache 日志中记录的 
IP 
 地址会变成 Cloudflare 代理节点的 IP，而不是访客的真实 IP。这会导致：

- 网站统计（如 Google Analytics）失去精确度
- 无法根据 IP 进行地域分析
- 防火墙/WAF 规则无法准确拦截
- 日志审计追踪困难

Cloudflare 早已弃用 `mod_cloudflare` 模块，官方推荐使用 Apache 内置的 **`mod_remoteip`** 来解决这个问题。

本文基于 **Rocky Linux 8.10 + Apache 2.4.37** 环境，完整记录配置过程。

---

### 环境说明

| 项目 | 信息 |
| --- | --- |
| 操作系统 | Rocky Linux 8.10 (Green Obsidian) |
| Web 服务器 | Apache 2.4.37 |
| 模块状态 | `mod_remoteip` 已加载，未配置 |
| 目标 | 恢复 Cloudflare 后的真实访客 IP |

---

### 第一步：检查 mod\_remoteip 模块

```
# 检查模块是否已加载
httpd -M | grep remoteip


bash
```

输出 `remoteip_module (shared)` 表示模块已启用。如果未加载，在 `/etc/httpd/conf.modules.d/` 中添加：

```
LoadModule remoteip_module modules/mod_remoteip.so


apache
```

---

### 第二步：创建 remoteip 配置文件

创建 `/etc/httpd/conf.d/remoteip.conf`：

#### 关键指令说明

| 指令 | 作用 |
| --- | --- |
| `RemoteIPHeader` | 指定从哪个 HTTP 请求头获取真实 IP。Cloudflare 使用 `CF-Connecting-IP` |
| `RemoteIPTrustedProxy` | 声明哪些代理 IP 是可信的，**只有来自这些 IP 的请求才会被替换 IP** |

> ⚠️ **安全提示**：不要使用 `RemoteIPTrustedProxy 0.0.0.0/0` 等通配规则，攻击者可以伪造 `CF-Connecting-IP` 请求头来欺骗服务器。

---

### 第三步：修改日志格式（推荐）

将 `%h` 替换为 `%a`，这让日志语义更明确：

```
# 先备份
cp /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.bak

# 修改
sed -i 's/^    LogFormat "%h /    LogFormat "%a /' /etc/httpd/conf/httpd.conf


bash
```

修改前后对比：

```
- LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
+ LogFormat "%a %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined


diff
```

| 占位符 | 含义 |
| --- | --- |
| `%h` | 远程主机名（默认情况下即对端 IP） |
| `%a` | 经过 `mod_remoteip` 处理后的真实客户端 IP |

> 💡 实际上 `mod_remoteip` 配置正确后，`%h` 也会显示真实 IP。但使用 `%a` 语义更清晰，是 Cloudflare 官方推荐的最佳实践。

---

### 第四步：测试并重启

```
# 1. 检查配置语法
apachectl configtest
# 输出: Syntax OK

# 2. 重启 Apache
systemctl restart httpd

# 3. 确认服务状态
systemctl status httpd


bash
```

---

### 第五步：验证效果

#### 方法一：curl 模拟测试

```
curl -s -H "CF-Connecting-IP: 1.2.3.4" http://localhost/ -o /dev/null
tail -1 /var/log/httpd/access_log


bash
```

访问日志中应显示 `1.2.3.4` 而非 `127.0.0.1`。

#### 方法二：实际访问验证

从外部访问网站，检查日志中的 IP 是否为真实访客 IP（而非 Cloudflare 的 IP 段）。

---

### 常见问题

#### Q: 配置后仍然显示 Cloudflare IP？

1. 确认 `remoteip.conf` 放在了 `/etc/httpd/conf.d/` 目录下
2. 检查 Cloudflare IP 段是否最新：https://www.cloudflare.com/ips/
3. 确认请求确实经过了 Cloudflare（检查是否存在 `CF-Connecting-IP` 请求头）

#### Q: mod\_remoteip 和 mod\_cloudflare 有什么区别？

| 对比 | mod\_cloudflare | mod\_remoteip |
| --- | --- | --- |
| 维护状态 | 已弃用 | 活跃维护 |
| 来源 | 第三方模块 | Apache 内置 |
| 安装方式 | 需手动编译 | 系统自带 |

#### Q: 需要定期更新 Cloudflare IP 段吗？

建议定期检查。Cloudflare 的 IP 段不常变动，但偶尔会有新增。可以考虑编写 cron 脚本自动
拉取 
更新：

```
# 示例：每月自动更新 Cloudflare IP 段
curl -s https://www.cloudflare.com/ips-v4/ > /tmp/cf-ips.txt


bash
```

---

### 总结

通过三步即可完成配置：

1. **创建 `remoteip.conf`** — 信任 Cloudflare IP 段，使用 `CF-Connecting-IP` 头
2. **修改 LogFormat** — `%h` → `%a`（最佳实践）
3. **重启 Apache** — 使配置生效

配置完成后，Apache 日志将正确记录访客的真实 IP，便于后续的日志分析和安全审计。

---

### 参考 链接

- Cloudflare 官方文档 - Restoring Original Visitor IPs
- Cloudflare IP Ranges
- Apache mod\_remoteip 文档

---