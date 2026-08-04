---
title: "macOS 设备注册补录或转换"
date: 2026-02-10
source: https://blog.csdn.net/u012587406/article/details/157903734
categories: IT 运维
tags: [macOS, Intune, ABM, 设备注册]
---
## 背景

笔者遇到一个需求，该组织有美国和中国两个办公室，美国办公室早期为了应付合规审查和省钱的目的，**给所有的苹果电脑设备做了 Intune 的“共享设备”（Shared device）的注册方式。中国办公室没有使用 MDM。**

然而随着组织的发展壮大，该组织希望充分发挥 MDM 的全部功能，并降低管理成本（指设备和人一一对应，避免手动维护 Excel 资产管理表），该组织希望**在不擦除电脑的情况下，完成设备注册的补录和升级。**

## 执行

### 前置准备

1. 在 Intune 设置 User Affinity Enrollment Profile，中国和美国办公室各一个。这么做是为了后面好做动态的设备组（eg: `device.enrollmentProfileName -eq "Beijing User-Affinity Enrollment Profile"`）。
2. 给两地设备 assign 对应的 Enrollment Profile，并 Sync Enrollment Token。

### 注册工作

与用户 schedule 一个会议，拿到电脑后确认序列号，在 Intune 定位设备。

#### 设备已被 Intune 管理的

在 Intune 触发 Retire 操作，清空 Enrollment Profile。

> 其实可以不 Retire，但是部分系统可能无法拉起 Safari WebView 去完成微软网页登录。拉不起来就会走很简单的邮箱和密码输入框，这是一种单因素验证，不支持 MFA。Entra 的 Conditional Access 会 fail 这个登录，标记为 Risky sign-in，进而导致 User 被标记为 Risky User。

打开 Terminal，敲以下指令：

```
sudo profiles renew -type enrollment


bash
```

让
用户输入 
登录密码授权，完毕后系统会拉起 Setup Assistant 指引用户完成设备注册。

#### 设备没有被 Intune 管理的

电脑关机，按住开机键进入恢复模式，切割出新分区安装一份 macOS 操作系统，并引导进去。

> 建议提前准备一个 macOS installer U盘，节省下载系统镜像的时间。

引导进去后，选择完语言，拿出手机打开 Apple Configurator 将设备添加到 Apple Business Manager，并 assign MDM server，然后去 Intune sync 一下 Enrollment Program Token。

> 设备添加到 ABM 的步骤只能在 Setup Assistant 中执行，没有其他办法。

Enrollment Profile 成功 assign 到设备后，关机进入恢复模式，引导到原系统，执行“设备已被 Intune 管理的”小节中的步骤即可。

### 收尾工作

通过本 workaround 注册进来的电脑，大概率是无法从 Intune 拿到 FileVault recovery key，从笔者观察来看，一般是做这个 workaround 之前这台电脑就因为 policy 启动过全盘加密，做完后不能重新 enforce 全盘加密（因为本身就是加密的状态），所以拿不到。

若要解决，请在 Terminal 输入以下指令：  
 `fdesetup changerecovery -personal`

触发一下 sync，IT 管理员就能在 Intune 看到 recovery key 了。