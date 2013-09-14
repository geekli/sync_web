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
    
    paths= #多个目录用英文逗号"," 分割path1,path2 
    
    [var]
    lasttime = 0 #或者是当前时间
需要注意的是

webroot
>比如 网站的绝对路径是 /var/www/web/ 但是ftp登陆后的根目录是/var/www/ 也就是说不能再往上走了
那么你的webroot 填写 /web/就可以了

paths
>paths 需要强制检测的目录，不依赖于版本控制软件
也就是说即使版本控制忽略了该目录，只有该目录下有文件变动，也会自动上传到服务器
另外程序是根据时间戳进行检测的，所以对那些修改名称（文件内容没有变化）的并不会检测到
目录结构也尽量不要太复杂

###计划

* 配置文件中可设置忽略目录

* <del>配置文件中可设置强制监测是否有修改的目录（即使该目录没有纳入版本控制）</del>

* 添加更新时是否需要确认一遍要上传的文件

* 增加对git的支持