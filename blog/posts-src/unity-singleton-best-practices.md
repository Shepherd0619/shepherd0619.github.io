---
title: "Singleton在Unity中的最佳实践"
date: 2023-10-06
source: https://blog.csdn.net/u012587406/article/details/133615751
categories: Unity 开发
tags: [Unity, C#, Singleton, 设计模式]
---
## 序言

Singleton即单例，在C#中主要方便找一个脚本的实例。

在Unity中，一般给场景中的某个非常常用的脚本做成Singleton，这样其他脚本就方便找它，而不是每次用的时候FindObjectOfType或者在脚本里写个公共变量然后在编辑器中拖拽进去。

## 示例

废话不多说，上代码

这是比较标准的应用。先声明一个私有变量和一个公共变量（都是静态），然后在Instance里写一个Get，里头判断一下m\_Instance是否为空。

如果是，则找一下整个场景里这个脚本的实例。如果没有，则返回null。

## 错误示范

```
1. public static VideoChatHelper Instance;

3. private void Awake()
4. {
5. Instance = this;
6. }


cs运行
```

别笑，这是我以前写的（在GitHub上非常
光 
明正大的亮出这低级错误，多亏同好提醒），以前不太注意。

这个虽说也能达到效果，但是不稳定。

因为Unity里有一个东西叫做Script Execution Order，即脚本执行顺序。假设脚本A要在Awake中调脚本B的Instance做一些事情。如果脚本B按照上面的写法，那么脚本A可能会拿到一个null的Instance。

## 结语

学海无涯，不忘初心，牢记使命。多沉淀，多学习，实现从码农到艺术家的蜕变。

加油！