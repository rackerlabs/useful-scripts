# Low_Disk

This disk usage script is designed to gather information on a Linux devices filesystem.
You can either run a breakdown of a filesystem `disk usage` or `inode usage`.

## Disk Usage Breadown Summary
- Filesystem Information Overview
- Largest Directories
- Largest Files
- Volume group space
- Large Open Files
- /home/rack usage

## Inode Usage Breakdown Summary
- Filesystem Information Overview
- Storage Device Behind Filesystem
- Top Inode Consumers
- Bytes Per Inode
- Disk space usage
- Elapsed Time (time taken to calculate breakdown)
- Server time as script completion


## Help
```
Usage: disk_usage_check.sh [-f] [-i] [-b] [-h]
           -i, --inode                    Display Inode breakdown
           -f, --filesystem <filesystem>  Specify a Filesystem
           -b, --bbcode                   Print with bbcode
           -h, --help                     Print help (usage)
```

## Disk Usage Breadown

```
$ ./disk_usage_check.sh

============================================================ 
 	 == / Filesystem Information == 
============================================================ 

Filesystem              Type  Size  Used Avail Use% Mounted on
/dev/mapper/fedora-root ext4  146G   59G   80G  43% /

Filesystem              Type  Inodes   IUsed   IFree IUse% Mounted on
/dev/mapper/fedora-root ext4 9732096 1346900 8385196   14% /

============================================================ 
 	 == Server Time at start == 
============================================================ 

Fri 11 Sep 12:23:57 BST 2020

============================================================ 
 	 == Largest Directories == 
============================================================ 

59G   /
30G   /var
25G   /var/lib
11G   /home
8.9G  /home/luke
8.7G  /usr
8.1G  /root
8.0G  /root/backups_desktop
4.2G  /var/log
3.4G  /usr/share

============================================================ 
 	 == Largest Files == 
============================================================ 

1061.86M  /home/luke/Downloads/Streetlight.Online.mp4
640.12M   /root/backups_desktop/error.log                                                                                                                           
535.58M   /root/backups_desktop/daily/test/home/luke/development/github/git_Luke/out-of-memory/messages                                               
535.58M   /home/luke/development/github/git_Luke/out-of-memory/messages                                                                               
505.55M   /root/backups_desktop/daily/desktop.2020-08-28-15:30:01.tar.gz.gpg                                                                                   
503.56M   /root/backups_desktop/daily/desktop.2020-08-29-15:30:01.tar.gz.gpg                                                                                   
467.61M   /root/backups_desktop/daily/desktop.2020-09-09-15:30:02.tar.gz.gpg                                                                                   
459.72M   /root/backups_desktop/daily/desktop.2020-09-08-15:30:01.tar.gz.gpg                                                                                   
457.75M   /root/backups_desktop/daily/desktop.2020-09-02-15:30:01.tar.gz.gpg                                                                                   
455.59M   /root/backups_desktop/daily/desktop.2020-09-01-15:30:01.tar.gz.gpg                                                                                   
455.38M   /root/backups_desktop/daily/desktop.2020-09-07-15:30:02.tar.gz.gpg                                                                                   
453.94M   /root/backups_desktop/weekly/desktop.2020-09-04-15:00:02.tar.gz.gpg                                                                                  
453.93M   /root/backups_desktop/daily/desktop.2020-09-04-15:30:01.tar.gz.gpg                                                                                   
453.27M   /root/backups_desktop/daily/desktop.2020-09-03-15:30:01.tar.gz.gpg                                                                                   
412.92M   /root/backups_desktop/daily/test/test.tar.gz                                                                                                              
300.00M   /root/backups_desktop/daily/test/home/luke/development/github/git_Luke/out-of-memory/oom_logs/large                                         
300.00M   /root/backups_desktop/daily/test/home/luke/development/github/git_Luke/oom_new_notgit/oom_logs/messages.verylarge                           
300.00M   /home/luke/development/github/git_Luke/out-of-memory/oom_logs/large                                                                         
300M      /home/luke/development/github/git_Luke/oom_new_notgit/oom_logs/messages.verylarge                                                           
230.55M   /usr/share/atom/resources/app.asar                                                                                                                        

============================================================ 
 	 == Volume Group Usage == 
============================================================ 

  VG     #PV #LV #SN Attr   VSize   VFree
  fedora   1   1   0 wz--n- 148.43g    0 

============================================================ 
 	 == OK Check List == 
============================================================ 

The following have been checked and are ok: 

[OK]      No open DELETED files over 500MB
[WARNING] /home/rack does not appear to exist

============================================================ 
 	 == Elapsed Time == 
============================================================ 

0h:0m:56s

============================================================ 
 	 == Server Time at completion == 
============================================================ 

Fri 11 Sep 12:24:53 BST 2020

============================================================
```
## Inode Usage Breadown
```
$ ./disk_usage_check.sh --inode


============================================================ 
 	 == / Filesystem Information == 
============================================================ 

Checking Inodes. Please note this could take a while to run...

============================================================ 
 	 == Server Time at start == 
============================================================ 

Fri 11 Sep 12:27:47 BST 2020

============================================================ 
 	 == Inode Information for [ / ] == 
============================================================ 

Filesystem               Type  Inodes   IUsed    IFree    IUse%  Mounted  on
/dev/mapper/fedora-root  ext4  9732096  1346902  8385194  14%    /        

============================================================ 
 	 == Storage device behind filesystem [ / ] == 
============================================================ 

/dev/mapper/fedora-root

============================================================ 
 	 == Top inode Consumers on [ / ] == 
============================================================ 

inode-Count 	 Path                          
    814,406 	 /var                          
    813,177 	 /var/lib                      
    808,320 	 /var/lib/docker               
    771,441 	 /var/lib/docker/overlay2      
    256,737 	 /home                         
    255,527 	 /usr                          
    179,418 	 /home/luke             
    146,649 	 /usr/share                    
     69,939 	 /home/luke/.cache      
     68,990 	 /usr/lib                      
     53,524 	 /root                         
     49,277 	 /root/backups_desktop         
     49,272 	 /root/backups_desktop/daily   
     49,262 	 /root/backups_desktop/daily/test
     49,233 	 /root/backups_desktop/daily/test/home
     42,162 	 /home/venv                    
     38,952 	 /home/luke/development 
     35,370 	 /usr/lib/python3.8            
     35,369 	 /usr/lib/python3.8/site-packages
     35,107 	 /home/luke/.cache/google-chrome

============================================================ 
 	 == Bytes per Inode format for [ / ] == 
============================================================ 

15.0 KB per inode!

============================================================ 
 	 == Disk space [ / ] == 
============================================================ 

Filesystem              Type  Size  Used Avail Use% Mounted on
/dev/mapper/fedora-root ext4  146G   59G   80G  43% /

Filesystem              Type  Inodes   IUsed   IFree IUse% Mounted on
/dev/mapper/fedora-root ext4 9732096 1346905 8385191   14% /

============================================================ 
 	 == Elapsed Time == 
============================================================ 

0h:1m:38s

============================================================ 
 	 == Server Time at completion == 
============================================================ 

Fri 11 Sep 12:29:25 BST 2020

============================================================
```
