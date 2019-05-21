# Low_Disk

This disk usage script is designed to gather information on a Linux devices filesystem usage and report on:
- Filesystem Information (Space and Inode usage)
- Largest Directories
- Largest Files
- Volume group space
- Large Open Files
- /home/rack usage

Use the `-b` flag for output with bbcode tags

## Usage ##

```
Usage: disk_usage_check.sh [-f] [-b] [-h]
           -f filesystem        Specify a Filesystem
           -b                   Print with bbcode
           -h                   Print help (usage)
```

## Example Output ##


```
============================================================ 
 	 == / Filesystem Information == 
============================================================ 

Filesystem                         Type  Size  Used Avail Use% Mounted on
/dev/mapper/vglocal20170715-root00 ext4  130G  8.9G  121G   7% /

Filesystem                         Type  Inodes  IUsed   IFree IUse% Mounted on
/dev/mapper/vglocal20170715-root00 ext4 8634368 229822 8404546    3% /

============================================================ 
 	 == Largest Directories == 
============================================================ 

8.5G  /
3.6G  /var
3.4G  /usr
2.7G  /var/cache
1.4G  /opt
1.1G  /usr/local

============================================================ 
 	 == Largest Files == 
============================================================ 

253.23M  /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/gen/primary.xml.sqlite
250.77M  /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/gen/filelists.xml
220.10M  /var/cache/yum/x86_64/7Server/rhel-x86_64-server-optional-7/gen/filelists.xml
199.96M  /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/gen/primary.xml
162.35M  /var/cache/yum/x86_64/7Server/rhel_base/gen/primary_db.sqlite
157.98M  /var/lib/rpm/Packages
139.54M  /var/cache/yum/x86_64/7Server/rs-epel/gen/filelists.xml
137.99M  /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/gen/filelists.xml.sqlite
101.13M  /usr/lib/locale/locale-archive
100M     /var/lib/mysql/ib_logfile1
100M     /var/lib/mysql/ib_logfile0
90.38M   /var/cache/yum/x86_64/7Server/rhel-x86_64-server-optional-7/gen/filelists.xml.sqlite
68.21M   /opt/dell/srvadmin/sbin/lx32/invcol
63.64M   /var/cache/yum/x86_64/7Server/rs-epel/gen/filelists.xml.sqlite
63.02M   /opt/dell/srvadmin/lib64/openmanage/jre/lib/rt.jar
59.26M   /opt/dell/srvadmin/lib64/openmanage/jre/lib/amd64/libjfxwebkit.so
55.68M   /var/cache/yum/x86_64/7Server/rs-epel/gen/filelists_db.sqlite
43.55M   /opt/dell/srvadmin/sbin/lx64/invcol
42.85M   /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/packages/kernel-3.10.0-693.el7.x86_64.rpm
37.30M   /var/cache/yum/x86_64/7Server/rhel-x86_64-server-7/packages/kernel-3.10.0-514.26.2.el7.x86_64.rpm

============================================================ 
 	 == Volume Group Usage == 
============================================================ 

  VG              #PV #LV #SN Attr   VSize   VFree
  vglocal20170715   1   3   0 wz--n- 135.63g 4.00m

============================================================ 
 	 == OK Check List == 
============================================================

The following have been checked and are ok: 

[OK]      No deleted files over 1GB
[OK]      /home/rack smaller than 1GB: 58 MB

============================================================
```
