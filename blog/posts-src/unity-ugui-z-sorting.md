---
title: "UGUI和Z轴排序那点事儿"
date: 2024-02-27
source: https://blog.csdn.net/u012587406/article/details/136326983
categories: Unity 开发
tags: [Unity, UGUI, Canvas, UI]
---
如果读者是从Unity 4.x时代过来的，可能都用过NGUI这个插件（后来也是土匪成了正规军），NGUI一大特点是可以靠transform位移的Z值进行遮挡排序，然而这个事情在UGUI成了难题（Sorting Layer、Inspector顺序等因素综合作为遮挡前置条件）。

![](images/feec6fcb28aa.png)

如图所示，现在我们有三个Image，白红蓝。在Inspector中的顺序如下：

![](images/547feb089c7c.png)

如果我们尝试让白色遮挡红色，按照NGUI的做法，我们把红色的Z值改为50，然而这种做法在UGUI直接现场寄。

![](images/c1e7ff4221db.png)

![](images/f9c5b2dc6ed5.png)

其中一种解决办法是改一下Inspector顺序。

![](images/352a845f0510.png)

至于如果想动态地调整顺序，你可以参考如下代码：

效果如图：

![](images/0a9067702492.gif)