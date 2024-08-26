#!/usr/bin/python3 -u
import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u

entity=u.readjsoninput()
config=u.read_config('../etc/config.conf')
ad.set_config(config)
if u.is_backend_concerned(entity):
  ad.ad_exec_script(entity,'upsertidentity.template')
else:
  u.returcode(0,"not concerned")