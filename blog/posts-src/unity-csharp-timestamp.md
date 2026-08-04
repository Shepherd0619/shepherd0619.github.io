---
title: "时间戳"
date: 2024-01-29
source: https://blog.csdn.net/u012587406/article/details/135903119
categories: Unity 开发
tags: [Unity, C#, 时间戳, DateTime]
---
## 前言

时间戳在
计算机科学 
和游戏设计中有着重要的意义。它是记录和比较时间的一种标准方式，经常用在网游的营销活动等，通过比较时间戳，可以确定是否在活动时间范围内诸如此类。一般来说它是一个long类型的数据。

可能也会有同志问了，long和ulong它俩区别一个有符号，一个无符号，难道说时间戳还能是负数？是的，因为做的是减法，看下面原理。

在C#中，时间戳通常是以Unix时间戳的形式存在，它是指从格林威治时间1970年1月1日00:00:00起至指定时间点的总秒数。C#中的DateTime
类 
型提供了一些方法和属性，可以方便地进行时间戳的计算。

## 网上一般操作

网上搜的话，一般都是使用DateTime.Now属性获取系统当前的日期和时间信息。通过DateTime对象的ToUniversalTime()方法将其转换为格林威治时间，然后使用Subtract方法**减去**1970年1月1日00:00:00，得到当前时间相对于1970年1月1日00:00:00的总秒数，也就是我们最终要的时间戳了。

示例代码如下：

```
1. DateTime now = DateTime.Now;
2. DateTime unixEpoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
3. TimeSpan timeSpan = now.ToUniversalTime() - unixEpoch;
4. long timestamp = (long)timeSpan.TotalSeconds;
5. Console.WriteLine("当前时间戳：" + timestamp);


cs运行
```

同样地，也可以使用DateTime对象的ToUniversalTime()方法将指定时间转换为格林威治时间，然后使用Subtract方法减去1970年1月1日00:00:00的时间戳，得到指定时间相对于1970年1月1日00:00:00的总秒数。

示例代码如下：

```
1. DateTime specifiedTime = new DateTime(2022, 1, 1, 0, 0, 0, DateTimeKind.Local);
2. DateTime unixEpoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
3. TimeSpan timeSpan = specifiedTime.ToUniversalTime() - unixEpoch;
4. long timestamp = (long)timeSpan.TotalSeconds;
5. Console.WriteLine("指定时间的时间戳：" + timestamp);


cs运行
```

## 一句代码完活儿的方法

事实上，自.NET进入4.6版本，我们可以使用DateTimeOffset类型来算时间戳。DateTimeOffset类型包含了日期和时间信息以及与协调世界时（UTC）的偏移量。我们可以通过DateTimeOffset.Now属性获取当前的时间戳，并使用DateTimeOffset对象的ToUnixTimeSeconds()方法将其转换为Unix时间戳。

示例代码如下：

```
long timestamp = new DateTimeOffset(DateTime.UtcNow).ToUnixTimeMilliseconds();

cs运行
```

基本现在主流的Unity版本的.NET都支持这个东西，不是什么新鲜东西了，可能也是习惯原因，用最原始的减法解决，这也不是什么问题，这也说明是懂这个原理的。

既然做交付，怎么快怎么省力就怎么来，别苦了自己，要学会“偷懒”。