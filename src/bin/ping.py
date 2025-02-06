#!/usr/bin/python3 -u
import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u

config=u.read_config('../etc/config.conf')
ad.set_config(config)
## test connection
exitCode=ad.test_conn()
if exitCode == 0:
    print(u.returncode(0, "I m alive"))
    exit(0)
else:
    print(u.returncode(1, "Can't connect"))
    exit(1)