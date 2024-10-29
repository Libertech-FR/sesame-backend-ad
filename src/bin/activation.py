#!/usr/bin/python3 -u
import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--active', help='0 | 1', default="1")
parser.add_argument('--debug', help='0 | 1', default="0")
args = parser.parse_args()
if args.debug == "1":
    ad.__DEBUG__ = 1
entity = u.readjsoninput()
config = u.read_config('../etc/config.conf')
ad.set_config(config)
if u.is_backend_concerned(entity):
    template = "disable.template"
    if args.active == 1:
        template="enable.template"
    ad.ad_exec_script(entity, template)
else:
    print(u.returncode(0, "not concerned"))
