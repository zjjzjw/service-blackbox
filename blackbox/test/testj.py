# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import json

j = '[{"name":"val"}]'
print j

tmp = json.loads(j)
tmp[0]['age'] = 12

print tmp[0]['name']
print tmp[0]['age']

jsondata = json.dumps(tmp)

print jsondata

