---
title: "OpenVPN与AD CS离线联动"
date: 2025-04-16
source: https://blog.csdn.net/u012587406/article/details/147262060
categories: IT 运维
tags: [OpenVPN, AD CS, 证书服务, Linux]
---
## 前言

笔者最近对一家企业的多个生产云服务器的网关入口进行证书更新，发现上面一直用的是easy rsa，该企业最近开始使用AD CS进行统一管理。

然而我注意到AD CS签发出来的证书，CRL地址均为LDAP协议，但生产环境的服务器并不是加域的机器，本文将介绍如何让外网的服务器在不加域的情况下，用AD CS提供的证书及其吊销列表进行验证。

## 操作

### 签发服务器证书并导出、上传、解压PFX

在一台Windows计算机上启动mmc，查看本机证书，以本机身份（不是用户身份）申请服务器证书。

![](images/2025f7f14c92.png)

根据实际需要，填写好证书的参数（如域名、公网静态地址）。

![](images/f7fb9e8dfa95.png)

完成后右键新签发的证书，导出PFX格式（PKCS 12）。

![](images/cb4fb70e5866.png)

若导出选项变灰，需检查证书模板是否支持导出私钥。

![](images/7319c8bf725a.png)

导出后将PFX上传到
Linux
，上传完毕后，需要使用openssl命令将pfx解包。

```
1. openssl pkcs12 -in certificate.pfx -clcerts -nokeys -out server.pem
2. openssl pkcs12 -in certificate.pfx -cacerts -nokeys -out server-ca.pem
3. openssl pkcs12 -in certificate.pfx -nocerts -out server.key
4. openssl rsa -in server.key -out my.key


bash
```

上面命令会将证书解压并转换格式，其中key需要转换两次，第一次转换的是被PEM加密的，第二次转换会转成纯文本。

最后修改OpenVPN的服务端配置文件，指向刚转换完的证书路径：

```
1. ca /etc/openvpn/server/server-ca.pem
2. cert /etc/openvpn/server/server-cert.pem
3. key /etc/openvpn/server/server-key.key
4. dh none


bash
```

### 客户端配置使用PFX验证

对于Windows，可以考虑干掉原先的ca, cert, key参数，用pkcs12代替：

```
1. ;ca ca.crt
2. ;cert client.crt
3. ;key client.key
4. pkcs12 openvpn-user.pfx


bash
```

下次连接，OpenVPN 
Community 
客户端会在每次连接询问pfx的密码，但可以选择记住密码。

如果使用的是OpenVPN 
Connect 
，可以正常走文件导入，将证书永久导入到OpenVPN的证书存储。

### OpenVPN导入CRL文件以拒绝使用已吊销证书的连接

AD CS侧，用浏览器访问Web Enrollment地址，下载出来Base CRL文件。

![](images/b340b6211257.png)

下载完毕后上传到OpenVPN服务端，将CRL文件转为PEM以便OpenVPN读取已吊销证书序列号名单。

```
openssl crl -in certcrl.crl -inform DER -out crl.pem

bash
```

最后修改配置文件，添加如下配置项：

```
crl-verify /etc/openvpn/server/crl.pem

bash
```

重启OpenVPN服务即可生效。

提示：OpenVPN服务运行期间，可以不停机直接替掉crl文件，所以可以考虑做个计划任务实现定期更新。