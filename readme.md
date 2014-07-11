# Introduction

 ``` wlister ``` is a web application firewall (WAF) allowing web application protection based on whitelisting and attack signature. The former is used to quickly validating an authorized and well formed request. The latter is used to detect known attacks patterns into HTTP requests. 
 
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

# Pros

```wlister``` allows can analyze any part of a HTTP request, headers and body, in a handy way, focusing only on the interesting part. 

Rule pre-conditions, tagging and action if (mis)match imply only necessary rules are applied and decision is done quickly; allowed or denied. 

```wlister``` try and use lazy evaluation to avoid transforming data that may never be used (but this is local optimization and must be measured). 

# Cons

 ```wlister``` is based on ```mod_python``` and Apache. This is not bad *per se* but because it is a Python application. Surely not fast enough although no benchmark have been done so far.
 
 ```wlister``` is based on ```mod_python``` and Apache, so it can not be used within another web server/proxy. 

# What is missing ?

**Logging** It exists but it is not nice enough. It can be very useful to have logging format used for advanced debug/configuration and logging format to raise an alert. Another format to... whatever. Logging facilities with formatting has to be implemented. 

**Attack signatures** No signature here, but I guess mod_security signature database can help.

**Documentation** Rules file used for unit tests can really help, but all rule directives must be documented at some point.

**Code review** One dev, one dev. 

**Matching modules** Matching directives are hard coded. Having a new one means developing it and binding stuff through the code which is error prone. Someone will want a new one, so it'd better be easy. 

**Learning module** Inferring patterns, finding invariants/constants, HTTP requests parts that are involved.