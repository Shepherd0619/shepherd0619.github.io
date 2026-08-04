---
title: "WebGL读取本机硬盘上的文件"
date: 2023-12-26
source: https://blog.csdn.net/u012587406/article/details/135232001#comments_34853683
categories: Unity 开发
tags: [Unity, WebGL, 文件系统, 浏览器]
---
由于浏览器的安全设置，System.IO的大部分功能都会受限。本文假设你要在Unity做一个头像上传的功能，这里我提供一个通过Unity和JavaScript实现的方法。

先在工程里起一个Plugins文件夹，用文本编辑器新建一个FileUploader.jslib。

在工程里起一个WebGLTemplate文件夹，在里头再新建一个文件夹，名字随意，这里存放着WebGL打包用到的HTML模板。**你可以先把Unity自带的先复制进去。**

**不管你最后基于哪个模板改，你都得在html里再加个JavaScript函数**

其中FileOpenDialog是**GameObject名（这个就相当于Unity里GameObject.SendMessage）**，OnFileSelected顾名思义是**回调**，我们把本地中的文件以JSON形式发送给Unity，里头包含blob地址和
文件名 
。

然后还得再加个隐藏的Input元素来接收选择的文件，例如：

```
<input id="upload" type="file" style="display:none" onchange="onFileSelected(event)">

html
```

这样，就可以在其他地方直接调用`OpenFileDialog`方法来打开文件选择
对话框 
。

调用方式见如下：

```
1. // 通过JavaScript函数来触发文件选择对话框
2. Application.ExternalEval(@"
3. document.getElementById('upload').click();
4. ");


cs运行
```

回调以及文件内容的读取可以参考这个：

**拿到的blob地址一定要用UnityWebRequest去读并拿到二进制数据，切记！**