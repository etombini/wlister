# Rules

Wlister uses a set of (so called) signatures or rules to determine if a request is to be whitelisted or not. 


Signatures are a JSON formatted file. A signature is composed of prerequisites, match, action to perform is match is ok, action to perform if match is not ok. 

``` 
#! Javascript
[
	{
		"prerequisite": {
			"has_tag": ["wl.method.get"]
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

## Prerequisite

Gathers all preconditions that has to be fullfiled to start using the signature/rule. 


```
{
  "prerequisite": {
    "has_tag": ["wl.method.get"]
  }
}
```

**Note**: a prerequisite not fullfilled do not activate `action_if_mismatch` directive. 



## Match

## Action if Match

## Action if Mismatch

## Tags

## Whitelisting

## Blacklisting

## Prerequisites

## Match
Try and match something in the request

* uri : matching the request URI. In http://www.example.com/some/file.php?id=0987654321 **/some/file.php** is the URI. 
 * test test test

## Action if Match

## Action if Mismatch
