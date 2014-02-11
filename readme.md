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

where ```[keywords]``` are plain text words (meaning letters, digits, spaces, maybe punctuation marks).

If someone is looking for "web application firewall", we would have the following request: 

```
http://mywebsite.com/service/search/web+application+firewall
```

Our web application handle this request with HTTP methods ```GET``` and ```HEAD```

We can build rules that whitelist requests when ```GET``` or ```HEAD``` is used, and ```URL``` is matched by the regular expression ```^/service/search/[a-zA-Z0-9\s]{1,100}```

Not perfect, so far, but o escaping caracter nor HTML tag can get into this. 



# Welcome

Welcome to your wiki! This is the default page we've installed for your convenience. Go ahead and edit it.

## Wiki features

This wiki uses the [Markdown](http://daringfireball.net/projects/markdown/) syntax.

The wiki itself is actually a git repository, which means you can clone it, edit it locally/offline, add images or any other file type, and push it back to us. It will be live immediately.

Go ahead and try:

```
$ git clone https://etombini@bitbucket.org/etombini/mod_python_waf.git/wiki
```

Wiki pages are normal files, with the .md extension. You can edit them locally, as well as creating new ones.

## Syntax highlighting


You can also highlight snippets of text (we use the excellent [Pygments][] library).

[Pygments]: http://www.pygments.org/


Here's an example of some Python code:

```
#!python

def wiki_rocks(text):
    formatter = lambda t: "funky"+t
    return formatter(text)
```


You can check out the source of this page to see how that's done, and make sure to bookmark [the vast library of Pygment lexers][lexers], we accept the 'short name' or the 'mimetype' of anything in there.
[lexers]: http://pygments.org/docs/lexers/


Have fun!

