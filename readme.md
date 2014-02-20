# Introduction

 ``` wlister ``` is an attempt to build a web application firewall (WAF) allowing web application developper to take full control on the security (at least from the HTTP interaction point of view), not (only) relying on third party WAF and their obscure signature schema.  

It allows to describe interactions between the web application and the client, using each piece of a HTTP request and their combination as a potential validation point (URI, parameters, headers, body, method, protocol, ...). 

The main feature is the usage of tags when rules applies to the incoming request. Using tags combination can tell if a request has to be whitelisted or not. 

**Overview**   
Each incoming request is analyzed using a set of rules. In the process, if some rule declares the request is whitelisted (resp. blacklisted), the analysis is stopped and the request is allowed (resp. is not allowed) to reach the web server.  If the analysis can not tell if the request is allowed or not, the global behaviour (defined by configuration) applies.

**Example**  
Let say we have a search URL in our website, implemented as follows: 

```
http://mywebsite.com/service/search/[keywords]
```

where ```[keywords]``` are plain text words (meaning letters, digits, spaces).

If someone is looking for "web application firewall", we would have the following request: 

```
http://mywebsite.com/service/search/web+application+firewall
```

Our web application handle this request with HTTP methods ```GET``` and ```HEAD```

We can build rules that whitelist requests when ```GET``` or ```HEAD``` is used, and ```URL``` is matched by the regular expression ```^/service/search/[a-zA-Z0-9\s]{1,100}```

Not perfect, so far, but no escaping caracter nor HTML tag can get into this. 


