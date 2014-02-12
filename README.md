sync_web
=======

将本地的修改通过ftp一键同步到一台或多台服务器上 ，**只同步修改内容**，非常适合维护一个网站并且经常改动代码的情况。

监测文件变动依赖于svn或git，脚本自动检测当前项目所用的版本控制系统

author: [ksc](http://blog.geekli.cn)

####使用方法:
 sync_web 配置文件路径 
 
 如： 
> sync_web /etc/syncweb/config.ini

若脚本所在目录下存在config.ini则默认使用该文件做配置文件

> 需要安装python2.7环境与**svn**|**git**客户端（确保**svn**|**git**命令所在目录加入到环境变量path中，即在终端下可以执行）

> 在window下多个网站的话比较方便的方法是
   
> 1. 右击脚本-\>发送到桌面快捷方式
> 2. 右击快捷方式点击属性 修改**目标**一栏
> 3. 在脚本路径后面添加配置文件路径 例如D:\\Python27\\test\\sync_web.py D:\\temp\\upload_file\\config.ini



 
####配置文件格式
config.ini:

    [ftp]
    host = test.com #FTP主机地址
    port = 21       #FTP端口
    user = ftp_user #FTP 用户名
    passwd = ftp_passwd
    ssl = True #是否启用ssl
    webroot = /web/ #网址相对于ftp根目录的绝对地址 
    automkdir = true #若服务器上目录不存在是否自动建立
    lasttime = 0 #或者是当前时间戳
    
    [ftp2]
    host = test2.com #FTP主机地址
    port = 21       #FTP端口
    user = ftp_user #FTP 用户名
    passwd = ftp_passwd
    ssl = True #是否启用ssl
    webroot = /web/ #网址相对于ftp根目录的绝对地址 
    automkdir = true #若服务器上目录不存在是否自动建立
    lasttime = 0 #或者是当前时间戳
    
    [local]
    local_webroot = D:/xampp/web/ 
    log_file = #不存储日志留空
    prompt=False #同步时是否需要确认，默认False，可空
    paths= #相对(本地web目录)路径，多个目录用英文逗号"," 分割path1/subpath/,path2 
    
    
    [var]
    lasttime = 0 #或者是当前时间戳，由于可同时传到了多台服务器，最后修改时间挪到了[ftp]部分去了。所以这里暂时没有用到
需要注意的是

webroot
>比如在服务器上网站的绝对路径是 /var/www/web/ 但是ftp登陆后的根目录是/var/www/ 也就是说不能再往上走了
那么你的webroot 填写 /web/就可以了

paths
>paths 需要强制检测的目录，不依赖于版本控制软件
也就是说即使版本控制忽略了该目录，只有该目录下有文件变动，也会自动上传到服务器
另外程序是根据时间戳进行检测的，所以对那些修改名称（文件内容没有变化）的并不会检测到
目录结构也尽量不要太复杂

新增ftp
>直接复制一份[ftp]节点内容,然后把对应的信息修改下，修改下节点名称，保证前三个字符是ftp就可以

路径
>配置文件中的路径不要使用反斜杠\\ 即使是在windows下 

>忽略目录是按照路径的前几个字符匹配的
若设置 exclude\_path= ign  则会忽略掉 ignore1/ ignore2/ 、igno/ 等目录

>若不想这样的话 在目录后面加上斜杠 exclude\_path= ign/  

###计划

* <del>配置文件中可设置忽略目录（优先级高）</del>
* <del>配置文件中可设置强制监测是否有修改的目录（即使该目录没有纳入版本控制）</del>
* <del>添加更新时是否需要确认一遍要上传的文件</del>
* <del>增加对git的支持</del>
* <del>支持同时同步到多台服务器上</del>
* 可通过命令行同步单个文件到服务器