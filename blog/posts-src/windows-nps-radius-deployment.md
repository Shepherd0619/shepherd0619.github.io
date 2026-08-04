---
title: "生产环境云和NPS快速搭建"
date: 2025-02-02
source: https://blog.csdn.net/u012587406/article/details/145422844
categories: Windows Server
tags: [Windows Server, NPS, RADIUS, 802.1X]
---
## 前置条件

本文假定你已达成以下前提条件：

- 有域控DC。
- 有证书服务器（AD CS）。
- 已使用Microsoft Intune或者GPO为客户机申请证书。
- 服务器上至少有两张网卡（如果用虚拟机做的测试环境，可以用一张HostOnly网卡做测试）。

阅读本文后，你应该会：

- 安装和配置生产环境云。
- 安装和配置NPS，并配置RADIUS实现证书验证。
- 使用客户机进行生产环境云网关连接验证和路由表验证。

## 服务端

打开服务器管理器，添加所需角色。

（注：下图笔者环境中，DC也有NPS。这里笔者勾上NPS是为了做负载均衡和RADIUS请求转发。）

![](images/8ff6a2741b2b.png)![](images/f224ce3e24c9.png)

 安装完成后，启动初始化向导。

![](images/0ca8f9133559.png)![](images/32e78268d65c.png)

选择仅部署生产环境云。

![](images/5ba814b31a45.png)

打开路由和远程访问MMC控制台，右键本机服务器，开始配置。

![](images/3f403a384af3.png)![](images/0033fe461807.png)

这里选择要监听的网卡，另一张网卡将被用于转发。

![](images/3e0bb2312cbd.png)

 配置完成后，需要安装NPS。NPS请视你内网环境情况安装在对应的服务器上，也可安装在本机。

NPS安装后，打开其控制台，选择配置生产环境云或拨号，并视情况配置验证方式。

![](images/69af1fd126be.png)

由于本文笔者使用的是证书环境，故选择智能卡或其他证书方式，并选择正确的CA。

![](images/819a7e9b79de.png)

## 

如果NPS并不是在生产环境云网关服务器上安装，那么一旦连接请求策略和网络请求策略创建成功，你需要先创建出来RADIUS客户端并记住其密钥。

![](images/6f51e223e5af.png)

然后你需要立即修改生产环境云的验证方式为RADIUS，并将RADIUS服务器地址和密钥输入。

![](images/0f89d604882e.png)

![](images/3064785a13dd.png)

## 客户端

如果你使用Microsoft Intune做设备管理和证书申请，那么你只需要添加一个Device Configuration即可。

![](images/8b37b80d5bc5.png)

![](images/388dec725f02.png)在Authentication certificate中选择你的SCEP profile或PKCS profile。 ![](images/8a8b7e22e1d9.png)

有关EAP，请参考EAP configuration | Microsoft Learn。大致思路为在测试机上做一个连接模板，使用
PowerShell 
输出XML粘贴到这里。

如果不是Intune，那么请直接运行rasphone去创建连接，并参考下图配置验证。

![](images/c6a990cb76d3.png)

![](images/d942180275ab.png)

连接成功后，使用tracert命令验证，确保第一跳是我们的虚拟网关服务器。

![](images/d347acdb3156.png)

## 常见问题

### 连接后无互联网连接

首先检查用于转发的网卡（如上图的Ethernet 2）是否有互联网访问，确认路由表是否异常。

如果本身不支持上网，只用于内网机器互访，那么请修改以下配置来避免所有流量全部经过生产环境云网关。

![](images/cb539334cdf7.png)

对于Intune，可以配置
Split 
 Tunneling来实现。

![](images/c3c595d0b6e5.png)

### 连接请求 timeout 或被ignore

一般建议直接去服务器上的事件查看器排查。对于笔者的环境来说，是因为Accounting在写入日志时出了问题。推荐使用SQL Server去做或者两者结合去做，而不是依赖本地文本文档。

![](images/68296e69f008.png)

默认情况下，如果日志写入失败，是要直接忽略掉连接。

![](images/9f2821821818.png)

另一个可以排查的点是数据库用户权限（如果你用SQL Server做日志记录），确认一下服务器身份验证模式和成员身份。

![](images/bb7469e76b37.png)

![](images/2eb321becbb0.png)