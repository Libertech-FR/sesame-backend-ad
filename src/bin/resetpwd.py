#!/usr/bin/python3 -u
import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='Debug mode', default="")
args = parser.parse_args()

if args.debug == "1" :
  ad.__DEBUG__=1
entity=u.readjsoninput()
config=u.read_config('../etc/config.conf')
ad.set_config(config)
if u.is_backend_concerned(entity):
  r=ad.reset_password(entity)
  exit(r)
else:
  print(u.returncode(0,"not concerned"))