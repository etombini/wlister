# Requirements

Current version is tested with ```Apache``` and ```mod_python``` on ```Ubuntu 12.04 LTS```.

```
$ sudo dpkg -l | grep apache2
ii  apache2                   2.2.22-1ubuntu1.4      Apache HTTP Server metapackage
ii  apache2-mpm-prefork       2.2.22-1ubuntu1.4      Apache HTTP Server - traditional non-threaded model
```

```
$ sudo dpkg -l | grep mod-python
ii  libapache2-mod-python     3.3.1-9ubuntu1         Python-embedding module for Apache 2
```

```
$ cat /etc/lsb-release 
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=12.04
DISTRIB_CODENAME=precise
DISTRIB_DESCRIPTION="Ubuntu 12.04.4 LTS"
```

 ```mod_python``` is supposed to be dead, but it is used for now (not as WSGI). Plus it seems to be not that dead, see:

* [mod_python - Home Page] (http://modpython.org/)
* [mod_python - The Long Story] (http://grisha.org/blog/2013/10/25/mod-python-the-long-story/)
