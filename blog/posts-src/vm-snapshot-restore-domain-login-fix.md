---
title: "迁移/恢复快照后的Windows Server虚拟机无法域账号登录"
date: 2025-02-14
source: https://blog.csdn.net/u012587406/article/details/145623670
categories: 其他
tags: [VMware, Windows Server, 域控, 快照]
---
笔者最近在在调整AD证书环境时，误卸载了Web Enrollment，导致证书申请地址404，故恢复快照。

但恢复几天前的快照后，无法使用域账号登录桌面。

> ```
> The trust relationship between this workstation and the primary domain failed.
> ```

根本原因为域控上的计算机账户哈希与本机不一致，或者快照时间点后修改过密码，也有可能计算机账号被禁掉，故域控拒绝了验证请求。

正常来说是需要管理员将设备leave后再join，但这不适合处理多台设备，时间成本较高。

最快的办法为使用PowerShell去操作。

我们可以先查一下当前域控auth状态：

```
Test-ComputerSecureChannel –Verbose
```

若为False，那么需要进行修复：

```
Test-ComputerSecureChannel -Repair -Credential woshub\administrator -Verbose
```