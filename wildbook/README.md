* Initialize a WildookAPI instance
``` python
from wildbookAPI import WildbookAPI
wapi = WildbookAPI('http://mydomain.com')
```

* Run a complete identification 
``` python
all_gid_list = wapi.get_all_gids()
wapi.run_complete_identification_pipeline(all_gid_list, 'zebra_plains', 0.7)
```

n