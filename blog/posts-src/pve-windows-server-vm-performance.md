---
title: "Windows Server虚拟机硬盘和网卡性能常见问题"
date: 2025-11-23
source: https://blog.csdn.net/u012587406/article/details/155161094
categories: 其他
tags: [PVE, Windows Server, 虚拟化, 性能优化]
---
## 背景

笔者有一个倍控软路由，其中有一个
Windows 
 Server放着域控和RRAS，系统IO延迟较高，
远程桌面 
维护体验很差，也影响了下游的上网体验。如果还赶上了Windows Update，基本处于无法使用的状态。

后经调查，发现PVE有相关的最佳实践指南。但是笔者已经按照Web UI默认创建，不可能重建，故着手调整优化。

## 步骤

1. 挂载驱动安装ISO，完成Setup

![在这里插入图片描述](images/b0b80662c622.png)  
 2. 手动安装SCSI控制器驱动，笔者是2022，所以路径在`vioscsi/2k22/amd64`。若你是其他版本的Windows系统，请自行选择对应驱动版本。

![在这里插入图片描述](images/152ecaa5ad95.png)  
 3. 关闭虚拟机，重新挂载硬盘，调整网卡
类 
型和启动顺序。  
 ![在这里插入图片描述](images/f1a69d6576c1.png)  
 ![在这里插入图片描述](images/b47a9e99c7f4.png)  
 ![在这里插入图片描述](images/60e0ea7542e8.png)

4. 开机启动验证

## 遇到的问题

### INACCESSIBLE\_BOOT\_DEVICE蓝屏

这个蓝屏一般意味着Windows没有找到对应的硬盘控制器驱动，你必须得在PVE调整硬盘前安装好VirtIO驱动。安装驱动步骤请见前文。

### 系统找不到启动盘，即便BIOS明确设置硬盘排在前面

启动顺序需要在PVE的WebUI指定，在BIOS指定是无效的。启动顺序设置请见第三步的第三张截图，务必保证硬盘为enable并在前面。