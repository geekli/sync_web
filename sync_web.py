# coding=utf-8

"""
将本地的修改通过ftp一键同步到服务器上 ，非常适合维护一个网站并且经常改动代码的情况(监测文件变动依赖于svn)
usage: sync_web config.ini
author: ksc (http://blog.geekli.cn)
version: 2.0

"""
import os,time,sys
import stat
import string
import subprocess
from ftplib import FTP
from ftplib import FTP_TLS as FTPS
import ConfigParser
script_path=sys.argv[0]
if len(sys.argv)==2:
    config_file=sys.argv[1]
else:#use default test config file
    config_file='config.ini'
    
if os.path.isabs(config_file)==False:#若是相对路径，则转化为绝对的
    config_file=os.path.realpath(os.path.dirname(script_path)+os.sep+config_file)
    
if os.path.isfile(config_file)==False:
    print 'config file does not exist'
    exit()    

print 'config: ',config_file    

conf={}
cf = ConfigParser.ConfigParser()
try:
    cf.read(config_file)
    local_webroot =cf.get('local','local_webroot')
    conf['log_file'] = cf.get('local','log_file')
    conf['prompt'] = False #prompt before every sync
    if cf.has_option('local','prompt'):
        conf['prompt']=cf.getboolean('local','prompt')
    
except Exception,e:
    print 'Parse config file failed'
    print e
    exit()
    
#本地项目目录
local_webroot=os.path.realpath(local_webroot)+os.sep

#获取文件列表
def getSvnFiles():
    """
        Returns:
            file 文件的相对路径 ，op 目前没有用到
            example: [{'file': 'upload/images/a.jpg', 'op': '?'},...]
    """
    global local_webroot
    
    os.chdir(local_webroot)
    #导出修改的文件列表
    pipe=subprocess.Popen("svn st", shell=True,stdout=subprocess.PIPE)
    pipe.wait()
    if pipe.returncode > 0:
        exit()
    files=[]
    for line in pipe.stdout:
        line=line.rstrip()
        #print line
        files.append({'op':line[0:1],'file':line[8:]})
    return files

def writeLogs(str,showTime = False ):
    global conf
    if conf['log_file']=='':
        return
    if showTime:
        str=time.strftime('%Y-%m-%d %H:%M:%S')+'  '+str+'\n'
    f=open(conf['log_file'],'a+')
    f.write(str)
    f.close()

#遍历目录
def walk_path(top):
    """ 
    Args:
        top: 相对web根目录的相对路径 
    Returns:
        该目录下的所有文件列表的一个数组
        格式同 getSvnFiles()的返回值
        example:[{'file': 'upload/images/a.jpg', 'op': '?'},...]
    """
    global local_webroot
    os.chdir(local_webroot)
    flist=[]
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            f=os.path.join(root, name)
            flist.append({'op':'n','file':f})
    return flist        


#获取不依赖[版本控制]监测变动的文件列表
def getKcFiles():
    global cf
    if cf.has_option('local','paths')==False:
        return []
    flist=[]    
    paths=cf.get('local','paths')
    paths=string.split(paths,',')
    for path in paths:
        flist.extend(walk_path(path))
    return flist

def prompt_sync(filelist):
    print
    for f in filelist:
        print f['file']
    y=raw_input('start sync?[Y/n]\n')
    if y=='n':
        quit() 
        
class Ftp_sync:
    def __init__(self,ftp_name):
        global config_file,local_webroot,cf
        self.bufsize = 1024
        self.cf = cf
        self.config_file = config_file
        self.local_webroot = local_webroot
        self.ftp_name = ftp_name
        try:
            self.ftp_host    = cf.get(ftp_name,'host')
            self.ftp_port    = cf.get(ftp_name,'port')
            self.ftp_user    = cf.get(ftp_name,'user')
            self.ftp_passwd  = cf.get(ftp_name,'passwd')
            self.ftp_webroot = cf.get(ftp_name,'webroot')
            self.ftp_ssl     = cf.getboolean(ftp_name,'ssl')
            self.automkdir   = cf.getboolean(ftp_name,'automkdir')
        except Exception,e:
            print 'Parse config file failed in ['+ftp_name+']'
            print e
            exit()
        self.lastUploadTime=self.getLastTime()
        self.filelist=[]
    
    def setFileList(self,filelist):
        """ 设置需要同步的文件列表"""
        self.filelist=filelist
        
    def getLastTime(self):
        """返回最后一次同步的时间"""
        try:
            ltime= cf.getfloat('var','lasttime')
        except:
            return 0
        return ltime
        
    def setLastTime(self):
        """设置最后一次同步的时间"""
        self.cf.set("var", "lasttime", time.time())
        self.cf.write(open(self.config_file, "w"))
        
    def connect(self):
        #初始化 FTP 链接
        if self.ftp_ssl:
            ftp = FTPS()
        else:
            ftp = FTP()
        print  'connect',('ftps' if self.ftp_ssl else 'ftp')+'://'+self.ftp_host+':'+self.ftp_port
        try:
            ftp.connect(self.ftp_host,self.ftp_port)
        except Exception,e:
            print e
            print 'connect ftp server failed'
            exit()
        try:
            ftp.login(self.ftp_user,self.ftp_passwd)
            print 'login ok'    
        except Exception,e:#可能服务器不支持ssl,或者用户名密码不正确
            print e
            print 'Username or password are not correct'
            exit()        
        
        if self.ftp_ssl:
            try:    
                ftp.prot_p()
            except Exception,e:
                print e
                print 'Make sure the SSL is on ;'
            
        print ftp.getwelcome()
        ftp.cwd(self.ftp_webroot)
        print 'current path: '+ftp.pwd()
        
        self.ftp=ftp
    
    def sync(self):
        _uploadNum = 0
        _bufsize=1024
       
        writeLogs('\n\n'+'start sync '+self.ftp_name+'\n')
        for line in self.filelist:
            file=line['file'] 
            fullname=self.local_webroot+file
            file= file.replace('\\','/')
            if not os.path.isfile(fullname):
                continue
             
            _st=os.stat(fullname)
            st_mtime = _st[stat.ST_MTIME]
            
            if st_mtime > self.lastUploadTime:#如果从上次上传后，文件修改过
     
                _uploadNum=_uploadNum+1
                writeLogs(fullname,True)
                print file
                file_handler = open(fullname,'rb')
                ftp_file=self.ftp_webroot+file
                try:
                    self.ftp.storbinary('STOR '+ftp_file,file_handler,_bufsize) 
                except Exception,e:
                    #print e
                    if self.automkdir== False:
                        quit()
                    else:# make dir and try again
                        try:
                            print 'try mkdir: '+os.path.dirname(file)
                            ftpdirs=os.path.dirname(file).split('/')
                            for _ftpdir in ftpdirs:
                                try:
                                    self.ftp.mkd(_ftpdir)
                                except:
                                    pass #忽略创建目录的错误
                                self.ftp.cwd(_ftpdir)                               
                            self.ftp.cwd(self.ftp_webroot)
                            self.ftp.storbinary('STOR '+ftp_file,file_handler,_bufsize) 
                            print 'upload success'
                        except Exception,e:
                            print e
                            quit()
                finally:        
                    file_handler.close()
                        
        self.setLastTime()            
        self.ftp.quit()
        if  _uploadNum >0:
            writeLogs('共上传'+str(_uploadNum)+'个文件')
        else:
            writeLogs('没有上传文件')
        print 'success';
        
filelist=getSvnFiles()
filelist.extend(getKcFiles())
if conf['prompt']:
    prompt_sync(filelist)
    
sync=Ftp_sync('ftp')
sync.setFileList(filelist)
sync.connect()
sync.sync()

time.sleep(2)

