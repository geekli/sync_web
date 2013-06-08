# coding=utf-8

"""
将本地的修改通过ftp一键同步到服务器上 ，非常适合维护一个网站并且经常改动代码的情况(监测文件变动依赖于svn)
usage: sync_web config.ini
author: ksc (http://blog.geekli.cn)
 
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
比如 网站的绝对路径是 /var/www/web/ 但是ftp登陆后的根目录是/var/www/ 也就是说不能再往上走了
那么你的webroot 填写 /web/就可以了

"""
import os,time,sys
import stat
from ftplib import FTP
from ftplib import FTP_TLS as FTPS
import ConfigParser
script_path=sys.argv[0]
if len(sys.argv)==2:
    config_file=sys.argv[1]
else:#use default test config file
    config_file='D:/temp/upload_file/sync_2.ini'
    
if os.path.isfile(config_file)==False:
    print 'config file does not exist'
    exit()
if os.path.isabs(config_file)==False:
    config_file=os.path.realpath(os.path.dirname(script_path)+os.sep+config_file)
    
print 'config: ',config_file    
   

cf = ConfigParser.ConfigParser()
try:
    cf.read(config_file)
    ftp_host    =cf.get('ftp','host')
    ftp_user    =cf.get('ftp','user')
    ftp_webroot =cf.get('ftp','webroot')
    ftp_port    =cf.get('ftp','port')
    ftp_passwd  =cf.get('ftp','passwd')
    ftp_ssl     =cf.getboolean('ftp','ssl')
    automkdir   =cf.getboolean('ftp','automkdir')
    local_webroot =cf.get('local','local_webroot')
    log_file      =cf.get('local','log_file')
    
except Exception,e:
    print 'Parse config file failed'
    print e
    exit()

local_webroot=os.path.realpath(local_webroot)+os.sep
#print local_webroot

# 获取最后一次上传时间
def getLastTime():
    global cf
    try:
        ltime= cf.getfloat('var','lasttime')
    except:
        return 0
    return ltime
    
# 设置最后一次修改时间    
def setLastTime():
    global cf,config_file
    cf.set("var", "lasttime", time.time())
    cf.write(open(config_file, "w"))
#获取文件列表
def getSvnFiles():
    global local_webroot
    #fpath=config_path+'file_list.txt'
    os.chdir(local_webroot)
    #导出修改的文件列表
    #os.system('svn st >'+fpath)
    file_list=os.popen('svn st','r')
    f = file_list #open(fpath,'r')
    files=[]
    for line in f:
        line=line.rstrip()
        #print line
        files.append({'op':line[0:1],'file':line[8:]})
    return files

#获取最后一次上传时间
def writeLogs(str,showTime = False ):
    global log_file
    if log_file=='':
        return
    if showTime:
        str=time.strftime('%Y-%m-%d %H:%M:%S')+'  '+str+'\n'
    f=open(log_file,'a+')
    f.write(str)
    f.close()
#print getSvnFiles()    
 
 
lastTime=getLastTime();


#初始化 FTP 链接
if ftp_ssl:
    ftp = FTPS()  
    print  'connect ',ftp_host,':',ftp_port,' ftps'
    ftp.connect(ftp_host,ftp_port) # connect to host, default port
    try:
        
        ftp.login(ftp_user,ftp_passwd)
        ftp.prot_p()
    except Exception,e:#可能服务器不支持ssl,或者用户名密码不正确
        print e
        print 'Make sure the SSL is on ; Username and password are correct'
        exit()
      
else:
    ftp = FTP()   # connect to host, default port
    print  'connect ',ftp_host+':'+str(ftp_port),'ftp'
    ftp.connect(ftp_host,ftp_port)
    ftp.login(ftp_user,ftp_passwd)
    print 'login ok'
print ftp.getwelcome()
 

ftp.cwd(ftp_webroot) 

print 'current path :'+ftp.pwd()
 
bufsize=1024

filelist=getSvnFiles()
uploadNum=0#上传文件数量

writeLogs('\n\n开始\n')
for line in filelist:
    file=line['file'] 
    fullname=local_webroot+file
    file= file.replace('\\','/')
    if os.path.isfile(fullname):
        _st=os.stat(fullname)
        st_mtime = _st[stat.ST_MTIME]
        
        if st_mtime > lastTime:#如果从上次上传后，文件修改过
 
            uploadNum=uploadNum+1
            writeLogs(fullname,True)
            print file
            file_handler = open(fullname,'rb')
            try:
                ftp_file=ftp_webroot+file
                ftp.storbinary('STOR '+ftp_file,file_handler,bufsize) 
            except Exception,e:
                if automkdir== False:
                    print e
                    quit()
                else:
                    try:
                        ftp.mkd(os.path.dirname(ftp_file))
                        ftp.storbinary('STOR '+ftp_file,file_handler,bufsize) 
                    except Exception,e:
                        print e
                        quit()
            finally:        
                file_handler.close()
                
            

if  uploadNum >0:
    writeLogs('共上传'+str(uploadNum)+'个文件')
else:
    writeLogs('没有上传文件')
setLastTime()
ftp.quit()
print 'success';
time.sleep(2)



