---
title: "Apache反向代理Nextcloud实战"
date: 2023-10-20
source: https://blog.csdn.net/u012587406/article/details/133945816
categories: IT 运维
tags: [Apache, Nextcloud, 反向代理, 运维]
---
## 前言

自更换移动宽带，无公网IP苦不堪言，还好有云服务器，寻思借用云服务器的公网IP完成云服务器到家里NUC主机上的Nextcloud安装的访问。

这里，笔者假定读者已经正确安装Nextcloud，且启用了SSL证书，系统为RHEL，网页服务器为Apache。

## SSL证书复制

因涉及到跨域访问，最好是把证书统一一下，拷贝Nextcloud的证书到你方便的位置，并在云服务器上的/etc/httpd/conf.d/ssl.conf最后面起一个VirtualHost

请注意，以上只代理https请求，如果你用的是
http 
，或者希望把http的都重定向到https，那么请在云服务器上的/etc/httpd/conf/httpd.conf最后面再起一个VirtualHost

```
1. <VirtualHost *:80>
2. ServerName 你的域名
3. RewriteEngine On
4. RewriteCond %{SERVER_PORT} 80
5. RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R,L]
6. </VirtualHost>
```

## 白名单

修改你的Nextcloud配置文件，我们需要把云服务器和域名做个白名单，它位于/
var 
/www/html/nextcloud/config/config.php（因个人而异）

第一件事，给array加上我们的域名或者你的云服务器IP

```
1. array (
2. 0 => '原来的地址',
3. 1 => '新地址',
4. ),
```

第二件事，添加链接重命名规则

```
1. 'overwrite.cli.url' => 'https://新地址/',
2. 'overwritehost'     => '新域名或新IP',
3. 'overwriteprotocol' => 'https',
```

保存，重启Apache，理论上你应该能正常通过网页登录NextCloud，然而这还没有完。

如果你要添加手机应用或者使用WebDAV，那么现在应该是会卡死在登录授权的循环。

## 客户端集成/WebDAV

修改ssl.conf和httpd.conf，在上文写的VirtualHost里写如下的重定向规则

```
1. RewriteRule ^/\.well-known/carddav https://%{SERVER_NAME}/remote.php/dav/ [R=301,L]
2. RewriteRule ^/\.well-known/caldav https://%{SERVER_NAME}/remote.php/dav/ [R=301,L]
```

保存，重启Apache，问题解决。