---
title: "Unity与Jenkins打包机实战"
date: 2023-11-23
source: https://blog.csdn.net/u012587406/article/details/134577153
categories: Unity 开发
tags: [Unity, Jenkins, 自动化打包, DevOps]
---
## 前言

Jenkins是一个开源的
持续集成
工具，用人话来说就是**没有感情的打包机**。一般常见于公司
项目 
用于持续交付。

可能有个人开发者对打包机很陌生或者不是很在意（比如在写这篇文章之前的我），项目小，本机写完本机打，甚至能边写边打，也没觉得怎么样。直到后来打包卡电脑没法做其他事情的时候，是时候单拎出来个电脑做个打包机了，要不耽误事情。

## Jenkins侧

### 安装

![](images/476413d801e3.png)

前往官网下载安装，有国内下载站，直接下
Windows
的LTS版本即可。

![](images/8624f06d23f3.png)

接着就按照安装向导一步一步走，直到你进入Jenkins的WebUI界面。

![](images/6edc8efd7651.png)

现在请点击左侧Manage Jenkins，然后点右侧的Plugins。

![](images/aeed3c481208.png)

单击左侧的Available Plugins，搜索Unity并安装。

### 配置

接下来需要告诉Jenkins你的Unity编辑器安装在哪里。

回到Manage Jenkins，点开Tools，一直下拉到底部添加安装

![](images/452eca42196e.png)

![](images/aeaad438e537.png)

### 创建工程

![](images/44f971eb0517.png)

选择Freestyle project，写好名字点击OK

![](images/6418f81504e4.png)

这些选项你可以根据个人喜好配置，包括Github库位置（若需要更新CI/CD状态）、Git账号啥的。

但建议打开时间戳log和打包无响应自动叫停。

![](images/e2f09c35d60d.png)

Build Steps那里添加指令，通过命令行启动Unity编辑器进行后台打包编译。

命令行参数可参考如下：

```
-projectPath "工程路径" -nographics -batchmode -quit -executeMethod JenkinsBuild.BuildWindows64 "${JOB_Name}" "工程打包存放位置\${BUILD_NUMBER}\output"
```

至此，Jenkins配置告一段落，接下来需要写一个和Jenkins联调的Unity编辑器脚本。

## Unity侧

### 联调脚本

在你的工程下，在Assets
文件夹 
下创建Editor文件夹，然后再创建一个JenkinsBuild.cs脚本，内容可参考如下：

至此Unity侧配置完毕

## 开始打包

![](images/ab48cd596c5c.png)

现在你可以单击Build Now开始打包，也请注意，**Jenkins显示的打包成功状态并不是很准**，如果Unity工程那里出现了C#脚本语法错误等，Jenkins大概率是不会识别出来这是个错误的，**因为Unity只要不是编辑器进程退出的过程中出了阻断性问题，Jenkins就会认为我正常走完了没有什么问题。**

![](images/9df4a2fe6b3a.png)

所以**每次打完包记得一定要看log确认。**

![](images/5ec02199b1b5.png)

Happy programming!