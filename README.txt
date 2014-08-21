 ``` wlister ``` is a web application firewall (WAF) allowing web application protection based on whitelisting and attacks signature. The former is used to quickly validating an authorized and well formed request. The latter is used to detect known attacks patterns into HTTP requests. 
 
Using ```wlister``` it is possible to apply both methods and to combine them at will. 

 ```wlister``` allows to describe interactions between the web application and the client, using each piece of a HTTP request and their combination as a potential validation point (URI, parameters, headers, content, method, protocol, ...).


# How it works

Each incoming request is analyzed using a set of rules. A rule has pre-conditions that must be fulfilled to be applied against the request. If pre-conditions are satisfied (reps. not satisfied), rule is applied (resp. next rule is used). "Rule is applied" means pattern matching is executed against some part of the request. 

Depending on the matching results (match or mismatch), actions can be specified. For now, there are 3 actions:
 
- tagging/untagging the request for next rule analysis
- whitelisting 
- blacklisting

Whitelisting and blacklisting terminate the request analysis. Tagging/untagging is useful to build smart pre-conditions, avoiding rules being applied whereas they are not related at all (*e.g.* HTTP request for static content must not be checked by rules dedicated to the authentication process nor any other rule). 

Rule configuration file used for unit test use all available features. 

# Requirements

## Librairies

 ```wlister``` is using [ ```jsonschema``` ](https://pypi.python.org/pypi/jsonschema) library to match JSON content in HTTP requests and to validate the whole ruleset.
It is expressed in ```requirements.txt``` and is installable using pypi.


## Software

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


# Pros

```wlister``` allows can analyze any part of a HTTP request, headers and body, in a handy way, focusing only on the interesting part. 

Rule pre-conditions, tagging and action if (mis)match imply only necessary rules are applied and decision is done quickly; allowed or denied. 

```wlister``` try and use lazy evaluation to avoid transforming data that may never be used (but this is local optimization and must be measured). 

# Cons

 ```wlister``` is based on ```mod_python``` and Apache. This is not bad *per se* but because it is a Python application. Surely not fast enough although no benchmark have been done so far.
 
 ```wlister``` is based on ```mod_python``` and Apache, so it can not be used within another web server/proxy. 

# What is missing ?

**Documentation** There are some stuff in ```doc/```. Rules documentation is outdated for sure. But what is implemented is tested so there are readable examples from  ```conf/rules.conf``` and ```tests/*.py```.

**Logging** It exists but it is not nice enough. It can be very useful to have logging format used for advanced debug/configuration and logging format to raise an alert. Another format to... whatever. Logging facilities with formatting has to be implemented. 

**Attack signatures** No signature here, but I guess mod_security signatures database can help.

**Documentation** Rules file used for unit tests can really help, but all rule directives must be documented at some point.

**Code review** One dev, one dev. But there are tests (see ```tests/*.py```)

**Refactoring** Matching directives are hard coded. Having a new one means developing it and binding stuff through the code which is error prone. Someone will want a new one, so it'd better be easy.

**Learning module** Inferring patterns, finding invariants/constants, ...

# Licensing

Copyright (c) 2014, Elvis Tombini <elvis_at_mapom.me>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

