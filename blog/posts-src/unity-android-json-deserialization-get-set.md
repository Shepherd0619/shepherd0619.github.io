---
title: "get set引起的安卓下Json反序列化错误"
date: 2023-10-18
source: https://blog.csdn.net/u012587406/article/details/133916868
categories: Unity 开发
tags: [Unity, C#, Android, Json, 序列化]
---
## 前言

今天一同事用Newtonsoft.Json解析Addressable里存放的角色服装Json文件，结果一直报键值相同的错误。Editor下一切正常，然而打到安卓上就不行了。解析出来的List数目都对的上，然而里面的数据都是空的或者默认值。

## 排查

### ~~DLL版本~~

最初以为是DLL版本的事情，因为工程用的是ExcelTools带的（毕竟他这个配置文件包括序列化、
反序列化 
是拿工具自动生成的，从Excel表格文件转出来的），所以我当时就先把DLL删掉换成
Unity
 Nuget里的版本。结果还是没解决，故开始研究代码问题。

### ~~Json字符串~~

后来在Addressable加载那里的complete事件打了读取TextAsset的log，结果也没出现什么平台导致的不一致。

### ~~JsonProperty问题~~

后来又去对了一下那几个序列化的class，对了一下名称，名称都对。

为了保险起见，我在每个公共变量的上一行加了JsonProperty修饰，如下：

```
1. [Serializable]
2. public class AvatarConfig{
3. [JsonProperty("Id")]
4. public int Id { get; set; }
5. [JsonProperty("Name")]
6. public string Name { get; set; }
7. [JsonProperty("Sexuality")]
8. public int Sexuality { get; set; }
9. }


cs运行
```

但依旧未解决问题。Android依旧出错。

### Get Set问题

主要是因为本人很少用Get Set，除非是要做singleton，一般我都不用。

折腾一圈，在没啥好的思路的情况下，当时就盲猜是Get Set的问题，只能试试看。

删掉后重新编译，**问题竟然解决了！**

```
1. [Serializable]
2. public class AvatarConfig{
3. public int Id;
4. public string Name;
5. public int Sexuality;
6. }


cs运行
```

看到老哥被这个bug困扰了1-2天，都没寻思是get set的问题，一时不知道怎么解释原因。

但不管怎么说，的确要慎重对待网上的自动生成json相关的代码

**如果读者知道原因，欢迎评论区留言！**