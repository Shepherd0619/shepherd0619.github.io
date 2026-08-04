---
title: "使用Linux搭建企业证书认证的WiFi热点"
date: 2025-02-28
source: https://blog.csdn.net/u012587406/article/details/145905739
categories: IT 运维
tags: [Linux, Wi-Fi, WPA3-Enterprise, FreeRADIUS]
---
## 前置条件

- 无线网卡一张及其Linux驱动（若使用虚拟机做服务器，请使用USB外接无线网卡，并让其独占）
- 可用的RADIUS服务器和证书环境。若使用微软NPS，建议证书Common Name为UPN或者OnPremDistinguishedName以免域控定位不到object导致拒绝。

## 部署流程

笔者使用TP-Link USB无线网卡去做，由于官网只提供
DEB安装包
，且编译中header判断linux版本需要至少6.3及以上，故使用Ubuntu Server等kernel比较新的发行版来做这个实验。

进入系统后，先拔掉无线网卡，再安装驱动。

虚拟机在安装驱动前，还需要开一个module

```
modprobe cfg80211
```

安装完无线网卡驱动后，插入设备，使用如下命令验证

```
ip addr
```

此命令结果会显示无线网卡的interface名称，请记好备用。

确认无线网卡后，请立即安装hostapd。

```
apt install hostapd
```

默认hostapd没有配置文件，正常配置文件应为/etc/hostapd/hostapd.conf

如果没有，你需要手动创建，配置文件参考如下：

interface填网卡名字（ip addr或ifconfig命令可以查），auth\_server请填RADIUS服务器信息。

SSID即网络名字，其余不改。

配置好以后，需要修改hostapd daemon的配置文件（/etc/default/hostapd），写死前文创建的配置文件路径，这样带着配置文件启动服务

![](images/872715a60bd5.png)

其余参数解释，请参考hostapd.conf(5)

现在部署基本完成，可以起服务，你可以使用systemctl，也可以直接call hostapd来进入debug模式。

```
hostapd -d /etc/hostapd/hostapd.conf
```

当然你可以末尾加一个&来实现后台运行，或者加一下redirect输出的修饰。

有一定可能，你没法通过systemctl去启动hostapd，因为该服务可能masked。

若如此，你可以unmask后再启动试试。

```
1. systemctl unmask hostapd
2. systemctl start hostapd
```

理论上hostapd没有异常退出，那就没问题了。现在你可以测试连接了，但是现在这个热点没有DHCP，所以设备可能会卡在分配地址阶段。

如果你只是想测试一下WiFi和RADIUS之间的流程，那么这些工作部署已经足够。

## DHCP服务

如果你不希望设备卡在地址分配，或者有想法做个上网功能（使用NAT共享互联网连接），这一步是必要的，后面写路由表规则好规定网卡和IP地址范围。

先安装dnsmasq服务

```
apt install dnsmasq
```

默认dnsmasq配置文件在/etc下，你可参考下方示例调整：

主要修改点总结如下：

- server：指定DNS服务器
- interface：监听哪张网卡
- listen-address: 可以理解为网关地址（这个地址后续会写死在无线网卡上）
- bind-interfaces：此选项主要避免和systemd-resolv冲突，不写明此选项会导致端口占用。
- dhcp-range：IP地址分配范围

完成后，需要给无线网卡写死IP

```
ifconfig wlx80ae54b151c3 192.168.0.1 netmask 255.255.255.0 up
```

如果要做ipv4数据包转发，那么去改一下系统配置（/etc/sysctl.conf）

```
net.ipv4.ip_forward=1
```

 若要生效，请敲sysctl -p

## 排障思路

一般服务器排障主要关注hostapd的日志和RADIUS，前者可以开debug模式看更细的日志，后者可以看Accounting。如果是Windows的NPS，可以看事件查看器中自定义视图——NPS。如果后者没有日志记录，建议Linux抓网包排查。

一种情况可以分享的是笔者的环境NPS日志的确没有动静，但如果我用不相干的证书或者验证方式，NPS会留日志，说明无线网络和RADIUS之间网络没问题。最后发现是证书的extended key usage有问题，没有包含client authentication。默认模板IPsec (Offline)并没有这个usage。