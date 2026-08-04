---
title: "退役本地 AD 同步后，Terraform 无法管理 Entra ID 用户？看这篇就够了"
date: 2026-07-17
source: https://blog.csdn.net/u012587406/article/details/162972528
categories: IT 运维
tags: [Entra ID, Terraform, AD 同步, Microsoft 365]
---
### 背景

公司此前使用本地 Windows AD 作为用户主目录，通过 Microsoft Entra Cloud Sync（不是 Microsoft Entra Connect，可以理解为青春版）将用户同步到 Entra ID。随着 IT 基础设施全面上云，我们决定下线本地 AD，将所有用户转换为纯云端管理，并由 OpenTofu（Terraform）全权接管基础设施即代码。

关闭 Cloud Sync 后运行 `tofu plan`，发现被同步过的用户出现如下错误：

```
Error: Could not update User

unexpected status 400 (400 Bad Request) with error: Request_BadRequest:
Unable to update the specified properties for objects that have originated
within an external service.
```

**核心矛盾**：即使 Cloud Sync 已经停用，Entra ID 仍然"记得"这些用户来自外部目录，拒绝 Terraform 对它们进行任何修改。

### 诊断过程

#### Step 1：检查 immutableId

Cloud Sync 会为每个同步用户写入 `onPremisesImmutableId`，这是与本地 AD 对象的关联锚点：

```
Connect-MgGraph -Scopes "User.ReadWrite.All"

Get-MgUser -UserId "user@example.com" \
  -Property OnPremisesSyncEnabled,OnPremisesImmutableId |
  Select-Object OnPremisesSyncEnabled, OnPremisesImmutableId

# OnPremisesSyncEnabled :
# OnPremisesImmutableId : fiITWgo2/ECR/rkgSZpRMA==


powershell
```

#### Step 2：尝试清除 immutableId（失败）

v1.0 API 不允许直接清空此属性：

```
Update-MgUser -UserId "user@example.com" -OnPremisesImmutableId $null

# Error: Invalid value specified for property 'onPremisesImmutableId'


powershell
```

用 beta API 绕过限制：

```
$body = @{ onPremisesImmutableId = $null } | ConvertTo-Json
Invoke-MgGraphRequest -Method PATCH \
  -Uri "https://graph.microsoft.com/beta/users/<object-id>" \
  -Body $body -ContentType "application/json"


powershell
```

成功清空了 immutableId，但 **Terraform apply 依然报错**。

#### Step 3：深入排查所有 on-premises 属性

immutableId 只是冰山一角。Cloud Sync 实际上写入了整套本地 AD 身份标识：

```
Get-MgUser -UserId "user@example.com" -Property \
  onPremisesDistinguishedName, onPremisesDomainName,
  onPremisesSamAccountName, onPremisesUserPrincipalName,
  onPremisesSecurityIdentifier


powershell
```

结果令人震惊——所有属性都还在：

```
onPremisesDistinguishedName  : CN=Zhang San,OU=Beijing Office,DC=corp,DC=local
onPremisesDomainName         : corp.local
onPremisesSamAccountName     : zhangsan
onPremisesUserPrincipalName  : zhang.san@example.com
onPremisesSecurityIdentifier : S-1-5-21-625977442-1185932894-852606376-1613
```

**根本原因**：Entra ID 并非只看 `immutableId` 一个字段。只要 `onPremisesDistinguishedName` 中**任意一个**非空，该用户在目录层面就被标记为"源自外部服务"。这个判断是整体性的，与具体要修改哪个属性无关。

#### Step 4：批量清除所有 on-premises 属性（仍然失败）

API 返回成功，所有可见属性都变成了空字符串。但是——

**Terraform apply 仍然报同样的错误！**

这说明 Entra ID 目录层级存在不对外暴露的"来源标记"，即便清空了所有 on-premises 属性，内核依然认定该用户来源于外部同步服务。

#### 另一种可能性：等 72 小时

Microsoft 官方文档 Turn off directory synchronization for Microsoft 365 提到：执行 `Update-MgOrganization -OnPremisesSyncEnabled $false` 关闭租户级目录同步后，微软后端会在 **72 小时内** 自动清理部分 on-premises 属性（`DnsDomainName`、`NetBiosName`、`OnPremisesDistinguishedName`、`OnPremisesSamAccountName`、`OnpremisesUserPrincipalName`）。

理论上，如果你不急于恢复 Terraform 管理，这可能是最省事的方案。但需要注意：

- 文档列出的清理属性**不包含** `onPremisesImmutableId` 和 `onPremisesSecurityIdentifier`，后端是否会一并清理未明确说明
- **我们未实际测试此方法**，不确定 72 小时后是否一定能解决本文的错误

如果你愿意等并且想验证，可以一试；如果不愿意冒险，直接用下面验证过的方法。

### 最终方案：软删除 + 从回收站还原

手动软删除后从回收站还原，是将同步用户转为云端用户的即时、已验证方法。

#### 完整脚本

关键点：**Object ID 保持不变**，所以 Terraform state 中已有的资源引用无需更新。

#### 批量处理

如果生产环境有多用户需要转换，可以写成循环：

删除和还原之间有短暂的异步延迟，给每个用户留 5 秒足够。

#### 验证

```
tofu plan
# Plan: 0 to add, N to change, 0 to destroy.
# No errors — 成功！


bash
```

### 总结

| 尝试的方法 | 结果 | 原因 |
| --- | --- | --- |
| 关闭 Cloud Sync | ❌ | 已有用户的同步标记不会自动清除 |
| 清除 `onPremisesImmutableId` | ❌ | 还有其他 on-premises 属性在生效 |
| 清除所有 on-premises 属性 | ❌ | Entra ID 内部仍有不可见的来源标记 |
| **软删除 + 回收站还原** | ✅ | 彻底重置用户身份，失去所有同步关联 |

### 经验教训

1. **退役 AD 同步前要做好规划**：理想的做法是先在 Cloud Sync 中将用户移出同步范围，让同步引擎执行"解绑"流程。本文的场景是因为关闭同步较快而留下的技术债。
2. **Object ID 是宝**：删除 + 还原不会改变 Object ID，因此 Terraform state 中的 `id` 引用、组成员关系、角色分配、应用授权等全部自动保留。不需要 `tofu state mv` 或 `terraform import`。
3. **密码策略**：原来由 Cloud Sync 设置的 `passwordPolicies: DisablePasswordExpiration` 可能保留在用户身上，这不是问题——Terraform 可以在后续 `apply` 中按自己的配置改写它，此时不会再被拒绝。
4. **权限要求**：整个过程需要 `User.ReadWrite.All` 或更高级别的 Graph 权限。如果使用 Application 权限（而非 Delegated），还需额外的 `Directory.ReadWrite.All`。
5. **推荐使用官方工具**：Microsoft 提供了 `ADSyncTools` PowerShell 模块，内置 `Clear-ADSyncToolsOnPremisesAttribute` 和 `Get-ADSyncToolsOnPremisesAttribute` cmdlet，封装了本文手动调用的 beta API。安装方式：`Install-Module ADSyncTools`（最低 v2.5.0）。如果你在一个合规性要求较高的环境中，建议优先使用官方模块而非手动调用 beta API。详见 Clear on-premises attributes from migrated Microsoft Entra ID users。

---

*适用场景：从 Microsoft Entra Cloud Sync / Azure AD Connect 迁移到纯云端管理，使用 OpenTofu / Terraform 管理 Entra ID 用户*

### 参考文档

| 文档 | 链接 |
| --- | --- |
| Clear on-premises attributes from migrated Microsoft Entra ID users | https://learn.microsoft.com/entra/identity/hybrid/connect/tshoot-clear-on-premises-attributes |
| Turn off directory synchronization for Microsoft 365 | https://learn.microsoft.com/microsoft-365/enterprise/turn-off-directory-synchronization |
| Update user — Microsoft Graph v1.0 / beta | https://learn.microsoft.com/graph/api/user-update |
| Restore deleted item (directory) — Microsoft Graph | https://learn.microsoft.com/graph/api/directory-deleteditems-restore |
| Microsoft Graph PowerShell SDK — Users module | https://learn.microsoft.com/powershell/module/microsoft.graph.users |
| Troubleshoot Entra Connect sync errors (deletion access violation) | https://learn.microsoft.com/entra/identity/hybrid/connect/tshoot-connect-sync-errors |
| Configure user Source of Authority (SOA) | https://learn.microsoft.com/entra/identity/hybrid/how-to-user-source-of-authority-configure |
| MS Q&A: Unable to update properties for on-premises mastered objects | https://learn.microsoft.com/answers/a/1911300 |
| MS Q&A: Converting a Synced User Object to Cloud-Only | https://learn.microsoft.com/answers/a/1989480 |
| MS Q&A: Convert a Directory Sync’d User to Cloud User | https://learn.microsoft.com/answers/a/2055447 |
| MS Q&A: Common issues after converting On Premise Users to the cloud | https://learn.microsoft.com/answers/a/12613890 |