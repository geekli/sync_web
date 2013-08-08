sync_web
=======

将本地的修改通过ftp一键同步到服务器上 ，非常适合维护一个网站并且经常改动代码的情况(监测文件变动依赖于svn)

author: [ksc](http://blog.geekli.cn)

用法: sync_web config.ini
> 需要安装python2.7环境与svn客户端（确保svn所在目录加入到环境变量path中）

> 在window下多个网站的话比较方便的方法是
   
> 1. 右击脚本-\>发送到桌面快捷方式
> 2. 右击快捷方式点击属性 修改**目标**一栏
> 3. 在脚本路径后面添加配置文件路径 例如D:\\Python27\\test\\sync_web.py D:\\temp\\upload_file\\config.ini



 
配置文件格式如下
config.ini:

    [ftp]
    host = test.com #FTP主机地址
    port = 21       #FTP端口
    user = ftp_user #FTP 用户名
    passwd = ftp_passwd
    ssl = True #是否启用ssl
    webroot = /web/ #网址相对于ftp根目录的绝对地址 
    automkdir = true #若服务器上目录不存在是否自动建立

    [local]
    local_webroot = D:/xampp/web/ 
    log_file = #不存储日志留空

    [var]
    lasttime = 0 #或者是当前时间
需要注意的是webroot这一项
>比如 网站的绝对路径是 /var/www/web/ 但是ftp登陆后的根目录是/var/www/ 也就是说不能再往上走了
那么你的webroot 填写 /web/就可以了

###计划

* 配置文件中可设置忽略目录

* 添加更新时是否需要确认一遍要上传的文件
