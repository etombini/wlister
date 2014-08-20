# Rules

 ```wlister``` uses a list of rules to determine if a request is to be whitelisted or not. Rules are a JSON formatted. A rule is composed of prerequisites, match functions and actions to perform if matching is ok/ko. 

``` 
[
	{
		"prerequisite": {
			"has_tag": ["http.method.get"]
		}
	},
    {   
        "match": {
            "uri": "^/$"
        }
     },  
     {
     	"action_if_match": {
            "whitelist": "True"
        }   
     },
     {
     	"action_if_mismatch": {
     		"set_tag": ["not_home_page"],
     		"unset_tag": ["easy_target"] 
     	}
     }
]
```

**Note**: Comments can be added to this configuration file. Any line beginning with ```#``` is considered a comment.

**Note**: If the content is not JSON compliant (except for the comments), a log entry is written saying: ```Rules format is not json compliant - /configuration/file/path - %message``` where ```%message``` is a debug information from JSON loader. 

## prerequisite

Gathers all preconditions that has to be fulfilled to start using the signature/rule (*i.e* start matching). 

### prerequisite - has_tag

 ```has_tag``` can be a list of string.
True if the request has the mentioned set of tags (all must be in).


### prerequisite - has_not_tag

 ```has_not_tag``` can be list of string.
True if the request has any of the mentioned set of tags.


**Example**

```
{
  "prerequisite": {
    "has_tag": ["method.get", "uri.home"],
    "has_not_tag": ["args"]
  },
  [...]
}
```

This prerequisite is satisfied if ```method.get``` and ```uri.home``` are set and if ```args``` tag is not set from a previous (mis)matching rule. 


Tags can be set/unset with ```action_if_match``` and ```action_if_mismatch``` directives.

***Note***: A tag can be any string. 

***Note***: a prerequisite not satisfied do not activate ```action_if_mismatch``` directive. 

## match

 ```match``` section sets up a group of matching directives altogether. To be true and be a matching rule, each and every matching directives (described below) must positively match the incoming requests. 

The first failing matching directive cancels all remaining matching directives and the rule processing for the current requests jumps to ```action_if_mismatch```.
If all directives return ```True```, the rule processing jumps to ```action_if_match```.

```
{   
    "prerequisite": {
        "has_tag": "POST",
        "has_not_tag": "Unexpected Tag" 
    },  
    "match": {
        "uri": "^/post/$",
        "method": "^(GET|HEAD)$",
        "protocol": "^HTTP/0\\.(1|0)$",
        "args": ".{1,256}",
        "parameters": [ ["var1", "^val1$"], ["var2", "^val2$"] ],
        "parameters_all_unique": "True"
        "parameter_list": [["var1", "var2", "var3"],
        "parameter_list_in": ["var1", "var2"],
        "content_url_encoded": [ ["var1", "^val1$"], ["var2", "^val2$"] ]
    },  
	[...]
}  
```

### match - ```order```

There is a non matching directive named ```order```. It forces the matching directives to be executed in a specific order. Without this directive, execution of matching directives can be executed in any arrangement. This directive must contain all matching directive in the related section, missing ones is not executed. 

```
[...]
	"match": {
		"order": ["uri", "args"],
		"uri": "^/very/complex/processing/$",
		"args": "some_cpu_consuming_regex"
	},
[...]
```

As the global matching depends on specific directives, the earlier it fails, the faster the analysis goes, avoiding unnecessary matching directives. 

### match - ```uri```

Use a regex to match the URI part of the HTTP request.

### match - ```method```

Use a regex to match the HTTP method used. 

### match - ```protocol```

Use a regex to match the HTTP protocol used (*i.e.* HTTP/1.1, HTTP/1.0 or HTTP/0.9).

### match - ```host```

Use a regex to match the host targeted by the HTTP request.

### match - ```args```

Use a regex to match HTTP request raw args (everything after the ```?```).

### match - ```parameters``` | ```headers``` |  ```content_url_encoded```
	
Use a list of tuples (parameter, regex) to match all the parameters in the HTTP request.

*Note*: all parameters must exist and match.

### match - ```parameters_unique``` | ```headers_unique``` |  ```content_url_encoded_unique```

List of parameters that must be unique in the HTTP request.

### match - ```parameters_all_unique``` | ```headers_all_unique``` |  ```content_url_encoded_all_unique```

All parameters must be unique in the HTTP request.

```
[...]
	"match": {
		"parameters_all_unique": "True"
	},
[...]
```


**Note** : HTTP headers must be considered with care. For example: 
```
Accept-Encoding: gzip, deflate, compress
```
means there are 3 instances of ```Accept-Encoding``` headers.


### match - ```parameters_in``` | ```headers_in``` |  ```content_url_encoded_in```
	
Use a list of tuples (parameter, regex) that must match parameters in the HTTP request.

### match - ```parameter_list``` | ```headers_list``` |  ```content_url_encoded_list```

List of all parameters that must be in the HTTP request.

*Note*: all parameters must exist.

### match - ```parameter_list_in``` | ```headers_list_in``` |  ```content_url_encoded_list_in```

List of parameters that must be in the HTTP request.

### match - ```content```

Use a regex to match the raw body of the HTTP request. 

*Note*: There can be limitation on the size of readable body, depending on the configuration set up. 

*Note*: There can be limitation on the size of readable body, depending on the configuration set up. 

## action_if_match

Actions triggered if all ```match``` directives return ```True```.


### action_if_match - set_tag

Associate a tag or a list of tags to the analyzed HTTP request. Such tags can be used by ```prerequisite.has_tag``` to decide if a rule has to be processed or not. 

```
{   
    "match": { "method": "GET" },  
    "action_if_match": { "set_tag": "GET" }   
}
```

### action_if_match - unset_tag

Unset a tag or a list of tags from the analyzed HTTP request.

### action_if_match - whitelist

Set the ```whitelist``` to ```True``` to decide if the request is OK thus ending the analysis (setting to ```False``` has no effect).

```
{   
	"prerequisite": { "has_tag": "GET"}
    "match": { "uri": "^/$" },  
    "action_if_match": { "whitelist": "True" }   
}
```

### action_if_match - blacklist

Set the ```blacklist``` to ```True``` to decide if the request is not OK thus ending the analysis (setting to ```False``` has no effect). Apache then return a ```404 - Page Not Found``` error.
 
```
{   
	"prerequisite": { "has_tag": "GET"}
    "match": { "uri": "^/$" },  
    "action_if_match": { "blacklistlist": "True" }   
}
```

### action_if_match - ```set_header```

Add a specific header to the incoming request, before it is sent to the backend. 

```
{	
	"prerequisite": { "has_tag": "GET"}
    "match": { "uri": "^/$" },  
    "action_if_match": { 
    	"set_header": ["x-wlister-fingerprint", "secret_fingeprint"] 
    } }
```

**Note** : if the header already exists in the request, it creates a duplicate. 

## action_if_mismatch

Actions triggered if any ```match``` directive returns ```False```.

 ```action_if_match``` directives have the very same behavior and apply into this context.
