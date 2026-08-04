---
title: "使用 Tenant Configuration Management API 完成微软租户备份自动化"
date: 2026-04-23
source: https://blog.csdn.net/u012587406/article/details/160426374
categories: IT 运维
tags: [Microsoft 365, API, 租户备份, 自动化]
---
## 背景

在企业级 Azure/Microsoft Entra ID 运维中，我们难免会使用 Terraform 和 M365 DSC 脚本等途径实现安全基准一致性和备份，今年微软推出了一个工作在 Graph 的、集备份和 Drift 监视于一体的 API 方案（Tenant Configuration Management，简称 TCM），允许 IT 运维通过**自动化方式在云端实现目标**。

重点是可以备份 Exchange 
Online 
 和 Teams 的配置，有效解决了 Terraform 目前 provider 无法接管 Exchange 的痛点。

但因为官方文档步骤分布较为零散，并不是一站式的、直接的指引，故笔者开一个文章总结，希望能帮到读者。

## 前置条件

微软没有明确表示订阅限制，所以哪怕你用的是最便宜的 Microsoft 365 F1 也可受益。

另外也请确保你的账号能够执行 Service Principal 创建和 Grant admin consent。

## 创建 Service Principal

详细步骤请见 https://learn.microsoft.com/en-us/graph/utcm-authentication-setup#set-up-the-tcm-service-principal

## 给 Service Principal 授权

原文只举例了部分 Graph permission 的授权，而且是通过 Graph Explorer 或 
PowerShell 
。对于 Exchange 授权，只是链接到了非常笼统的指南。

但经过一番折腾，笔者发现了一个更友好的方式。

先访问 Entra Admin Center，找到 Tenant Governance

![在这里插入图片描述](images/f0a5e7a77319.png)  
 在这里，你可以添加你需要的 Graph 权限、Exchange 权限以及 Teams 
Reader
 role。

## 自动化角色的权限配置

根据你的需求，选择 Delegated 或者 Application。

![在这里插入图片描述](images/2d779c6c3843.png)

## API call 流程示意

下图流程适合你想打 Snapshot，把配置结果上传到 Git 进行版本控制。

![在这里插入图片描述](images/42f436c7107d.png)

先 Create snapshot，得到 job id，然后轮询 job 状态，直到返回 status 为 succeeded，取出 json body 里的 resourceLocation 字段，最后发送 GET 请求到 resourceLocation 去拿 snapshot 结果 json 上传到 Git。