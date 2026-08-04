---
title: "使用 EntraRadius 打通 FreeRADIUS 与 Microsoft Entra 的认证桥梁"
date: 2026-03-02
source: https://blog.csdn.net/u012587406/article/details/158568321
categories: IT 运维
tags: [FreeRADIUS, Entra ID, RADIUS, 认证, Wi-Fi]
---
### 引言

在企业网络环境中,传统的 RADIUS 认证协议仍然广泛应用于 VPN、WiFi 和
网络设备 
的身份验证。然而,随着企业逐步迁移到云端,如何让这些传统网络设施能够使用 Microsoft 365 的云端身份进行认证,成为了一个实际的技术挑战。

本文将介绍 **EntraRadius** 项目——一个轻量级的 ASP.NET Core 8.0 Web API,它巧妙地充当 FreeRADIUS 与 Microsoft Entra (原 Azure AD) 之间的"翻译器",并通过智能缓存机制实现了高可用的双层认证架构。

### 问题背景

#### 核心痛点

FreeRADIUS 作为一个成熟的 RADIUS 服务器,无法直接与 Microsoft Entra 进行通信。企业面临的典型场景包括:

1. **VPN 接入**:员工使用 VPN 连接公司网络时,希望用 Microsoft 365 账号进行身份验证
2. **WiFi 认证**:企业内部 WiFi 需要对接云端身份管理系统
3. **网络设备登录**:路由器、交换机等设备的管理员登录需要统一认证
4. **高可用需求**:当 Microsoft 云服务临时不可用时,不能影响正常的业务访问

传统解决方案往往需要复杂的目录同步、本地 AD 
部署 
,或者依赖第三方商业产品。

#### 我们的目标

设计一个简单、可靠的解决方案,满足以下需求:

- ✅ 让 FreeRADIUS 能够验证 Microsoft Entra 账号
- ✅ 当 Microsoft 云服务不可用时,系统仍能提供认证服务
- ✅ 保持架构简单,易于部署和维护
- ✅ 提供清晰的认证来源追踪(云端 vs 缓存)

### 解决方案架构

#### 整体架构图

```
用户登录 → FreeRADIUS → EntraRadius API → Microsoft Entra
                              ↓
                         内存缓存层 (容错机制)
```

#### 双层认证流程

EntraRadius 的核心创新在于其**双层认证架构**,这种设计既保证了安全性,又实现了高可用性:

##### 第一层:主认证(Microsoft Entra)

1. **接收认证请求**:FreeRADIUS 通过 HTTP POST 将用户凭证发送到 EntraRadius API
2. **云端验证**:EntraRadius 使用 MSAL (Microsoft Authentication Library) 通过 ROPC 流程与 Entra 通信
3. **成功响应**:如果认证成功,返回 200 状态码,`source: "entra"`
4. **缓存更新**:成功的认证会立即缓存到内存中,为后续容错做准备

##### 第二层:缓存回退(Cache Fallback)

当第一层认证遇到**服务级异常**(网络故障、服务不可达等)时:

1. **异常捕获**:Controller 捕获 `EntraServiceException`
2. **缓存验证**:从内存缓存中查找该用户的历史认证记录
3. **密码哈希比对**:使用 SHA256 哈希值比对密码
4. **回退成功**:如果缓存命中,返回 200 状态码,`source: "cache"`
5. **双重失败**:如果缓存也未命中,返回 503 Service Unavailable

#### 关键设计决策

##### 1. 异常分类策略

这是整个架构中最精妙的设计。`GraphClientService` 对 MSAL 异常进行了精确分类:

**为什么这样设计?**

- **认证失败**(密码错误)≠ **服务故障**(Entra 不可达)
- 密码错误不应该尝试缓存,否则会降低安全性
- 只有当 Entra 服务本身出现问题时,才启用缓存机制

##### 2. 缓存键值规范化

```
var cacheKey = $"user:{userName.ToLowerInvariant()}";


csharp运行
```

用户名统一转换为小写,避免 `User@Domain.com` 和 `user@domain.com` 被视为不同用户。

##### 3. 密码哈希存储

虽然这是**内存缓存而非持久化存储**,但仍然对密码进行 SHA256 哈希:

```
using var sha256 = System.Security.Cryptography.SHA256.Create();
var hashedBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
return Convert.ToBase64String(hashedBytes);


csharp运行
```

这种设计即使
内存 
被意外转储,也不会直接暴露明文密码。

### 技术实现细节

#### 依赖注入配置

在 `Program.cs` 中,服务的生命周期设计非常讲究:

```
// Singleton - 缓存必须在整个应用生命周期中持久化
builder.Services.AddSingleton<IUserCacheService, UserCacheService>();

// Scoped - 每个请求创建新实例,避免线程安全问题
builder.Services.AddScoped<GraphClientService>();


csharp运行
```

#### API 响应设计

通过 `source` 字段明确标识认证来源,便于运维监控和审计:

**Entra 认证成功**:

```
{
  "message": "Authentication successful",
  "source": "entra"
}


json
```

**缓存回退成功**:

```
{
  "message": "Authentication successful (fallback)",
  "source": "cache"
}


json
```

**双重失败**:

```
{
  "message": "Authentication failed - Entra is unreachable and user not found in cache"
}


json
```

HTTP 
状态码 
: 503 Service Unavailable

#### Controller 核心逻辑

`RadiusController.cs:38-78` 中的实现清晰展示了双层认证的流程:

### 配置与部署

#### Microsoft Entra 配置要点

在 Azure 
Portal
 中注册应用时,有几个关键配置:

1. **启用公共客户端流**:Authentication → Advanced settings → Allow public client flows = YES
2. **配置重定向 URI**:即使 ROPC 不使用重定向,添加一个 URI 可以绕过某些 MFA 策略的限制
3. **API 权限**:授予 `User.Read` 权限并进行管理员同意

> ⚠️ **重要提示**:如果你的 Tenant 强制要求 MFA,必须添加 Redirect URI,否则 ROPC 会被条件访问策略阻止。

#### 应用配置

`appsettings.json`:

```
{
  "EntraConfiguration": {
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "Scopes": ["https://graph.microsoft.com/.default"],
    "CacheDurationMinutes": 60
  }
}


json
```

**生产环境建议**:使用环境变量或 Azure Key Vault,避免在配置文件中硬编码敏感信息。

#### 与 FreeRADIUS 集成

配置 FreeRADIUS 的 `rlm_rest` 模块:

### 容错能力验证

#### 场景一:正常情况

```
$ curl -X POST https://localhost:5001/api/radius/authenticate \
  -H "Content-Type: application/json" \
  -d '{"userName":"user@domain.com","password":"correct-password"}'

{
  "message": "Authentication successful",
  "source": "entra"
}


bash
```

#### 场景二:Entra 不可达(首次认证)

如果用户从未成功认证过,缓存中没有记录:

```
{
  "message": "Authentication failed - Entra is unreachable and user not found in cache"
}


json
```

HTTP 状态码: 503

#### 场景三:Entra 不可达(缓存命中)

用户在 60 分钟内成功认证过,此时即使 Entra 断网:

```
{
  "message": "Authentication successful (fallback)",
  "source": "cache"
}


json
```

HTTP 状态码: 200

这确保了即使 Microsoft 云服务出现故障,用户仍然可以登录网络。

### 安全性考量

#### ROPC 流程的局限性

ROPC (Resource Owner Password Credentials) 是一个**已被 Microsoft 标记为遗留**的认证流程:

- ❌ 绕过多因素认证(MFA)
- ❌ 不支持条件访问策略
- ❌ 无法使用现代认证特性(如 FIDO2、Windows Hello)

**为什么仍然使用 ROPC?**

在 RADIUS 场景下,传统网络设备**无法**支持现代 OAuth2/OIDC 的交互式授权流程(需要浏览器重定向)。虽然来宾网络可以拉起浏览器窗口，但并不符合合规要求，ROPC 是唯一可行的方案。

由于企业有静态公网 IP，我们在 Conditional Access 配置了 Trusted Network Location。

#### 缓存安全性

- ✅ 密码 SHA256 哈希存储
- ✅ 可配置的过期时间(默认 60 分钟)
- ✅ 内存存储,应用重启后自动清空
- ⚠️ 单实例场景,多实例需要迁移到 Redis 等分布式缓存

### 生产环境优化建议

#### 1. 分布式缓存

对于多实例部署,实现基于 Redis 的 `IUserCacheService`:

```
public class RedisUserCacheService : IUserCacheService
{
    private readonly IConnectionMultiplexer _redis;
    // 实现相同接口,使用 Redis 替代 IMemoryCache
}


csharp运行
```

#### 2. 速率限制

添加 `AspNetCoreRateLimit` 防止暴力破解:

#### 3. 结构化日志

集成 Serilog 输出到 
Elasticsearch
/Azure Log Analytics:

#### 4. 健康检查

添加 Health Check 端点供负载均衡器探测:

```
builder.Services.AddHealthChecks()
    .AddCheck<EntraHealthCheck>("entra");

app.MapHealthChecks("/health");


csharp运行
```

### 监控与运维

#### 关键指标

建议监控以下指标:

1. **认证成功率**:

   - `auth_success_entra`: Entra 认证成功次数
   - `auth_success_cache`: 缓存回退成功次数
   - `auth_failed`: 认证失败次数
2. **缓存命中率**:

   - `cache_hit_rate = auth_success_cache / (auth_success_entra + auth_success_cache)`
3. **服务可用性**:

   - `entra_unreachable`: Entra 不可达事件
   - `service_degraded_duration`: 降级服务持续时间

#### 告警规则

- ⚠️ 缓存回退比例 > 30%:可能 Entra 服务异常
- 🚨 连续 5 分钟返回 503:Entra 彻底不可用且缓存过期

### 项目总结

#### 解决的问题

EntraRadius 通过一个轻量级的 Web API,优雅地解决了 FreeRADIUS 与 Microsoft Entra 之间的认证集成问题,并通过智能缓存机制实现了高可用性。

#### 核心亮点

1. **双层认证架构**:主认证 + 缓存回退,兼顾安全与可用性
2. **异常分类策略**:精确区分认证失败与服务故障,避免误用缓存
3. **清晰的认证来源追踪**:通过 `source` 字段明确标识认证路径
4. **简洁的架构设计**:无数据库依赖,易于部署和维护

#### 适用场景

✅ 企业 VPN 接入认证  
 ✅ 企业 WiFi 802.1X 认证  
 ✅ 网络设备统一身份管理  
 ✅ 需要离线容错能力的 RADIUS 场景

#### 局限性

⚠️ ROPC 流程已被标记为遗留,无法使用现代 MFA 特性  
 ⚠️ 内存缓存在应用重启后丢失  
 ⚠️ 默认无速率限制,需要额外配置

### 结语

在云化转型的过程中,如何让传统基础设施平滑过渡到现代身份管理系统,是许多企业面临的实际问题。EntraRadius 项目提供了一个简洁、实用的解决方案,通过巧妙的架构设计,在保证安全性的前提下实现了高可用性。

希望这个项目能够为面临类似问题的技术团队提供参考和启发。

---

**项目地址**: EntraRadius  
 **技术栈**: ASP.NET Core 8.0, MSAL.NET, FreeRADIUS