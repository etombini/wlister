# Configuration


```
PythonPostReadRequestHandler 	       /path/to/python/wlister.py::handler
```

```
PythonOption wlister.key               ComplicatedTextUsableAsAHTTPHeaderValue
```

```
PythonOption wlister.log_prefix        [wlister]
```

```
PythonOption wlister.log_level         DEBUG
```


```
PythonOption wlister.404               /home/elvis/mod_python_waf/pages/404.html
```

```
PythonOption wlister.conf       	   /path/to/your/rules.conf
```

```
PythonOption wlister.default_action    block
```

```
PythonOption wlister.max_post_read	   65536
```
