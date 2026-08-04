---
title: "Win11安装向导不识别硬盘"
date: 2024-12-04
source: https://blog.csdn.net/u012587406/article/details/144226194
categories: Windows Server
tags: [Windows 11, 部署, 驱动, 硬盘]
---
默认情况下，如果引导用的boot.wim镜像取自Windows 11，大概率客户机会出现找不到硬盘报错

![](images/c8871f39ae4d.png)

Microsoft Learn明确指明Windows 11的boot.wim已经将WDS屏蔽。

| Windows Version being deployed | Boot.wim from Windows 10 | Boot.wim from Windows Server 2016 | Boot.wim from Windows Server 2019 | Boot.wim from Windows Server 2022 | Boot.wim from Windows 11 |
| --- | --- | --- | --- | --- | --- |
| **Windows 11** | Not supported, blocked. | Not supported, blocked. | Not supported, blocked. | Not supported, blocked. | Not supported, blocked. |

Windows Deployment Services (WDS) boot.wim support | Microsoft Learn

可用的workaround为使用Windows 10镜像的boot.wim做引导，而安装文件使用Win11的install.wim。

最好是使用MDT做Task Sequence,导出来wim启动映像放到WDS里。

Download Microsoft Deployment Toolkit (MDT) from Official Microsoft Download Center