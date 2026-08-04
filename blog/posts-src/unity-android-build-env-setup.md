---
title: "Unity Android打包环境快速部署"
date: 2023-09-28
source: https://blog.csdn.net/u012587406/article/details/133384929
categories: Unity 开发
tags: [Unity, Android, 打包, SDK]
---
此文章献给所有不是通过Hub安装Unity
编辑器 
的读者。

## 情景再现

我相信你有各种理由不通过Hub安装Unity编辑器，有的能说，有的不能说。你通过官方Download 
Archive 
下载所有你需要的安装包，一顿操作，等到要打安卓包的时候，发现环境没配置。于是乎你装上了jdk，然后通过Android Studio下载Android SDK，结果Unity告诉你版本对不上，它要一个比较旧的platform tools。

那咋办，你也不能卸掉Editor，通过Hub重装，这下载和安装的时间等不起，别担心，我有个好办法。

## Android SDK Manager

Unity比较挑食，你得找到它要的tools，但是Android Developer官网有相当一部分不提供原来的下载地址了。但是Google给我们留下了后路，那就是独立的Android SDK Manager。

![](images/a92f01f4217e.png)

可能网上不太好找了，可以上这里  
下载 Android SDK 24.4.1 Windows 版 - Filehippo.com

安装的时候会自动检测是否安装正确的JDK和JRE，通过以后，请务必选择**“仅为当前用户安装”，**否则安装完就是打不开SDK管理器。

安装成功后，你应该就能看到这个界面了，首次启动可能会提示管理器已更新，那个无所谓。

![](images/23bbc3d2d035.png)

**这里建议是根据你工程配置的最低安卓系统版本选。如果下载很慢的话，去Tools菜单改一下设置，强制把https定向到http就好了。**

祝好运！

（原文最早发布于本人X账号，2023年9月21日）