#!/usr/bin/python3 -u
import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='config file', default="../etc/config.conf")
args = parser.parse_args()
config=u.read_config(args.config)
ad.set_config(config)
## test connection
exitCode=ad.test_conn()
if exitCode == 0:
    print(u.returncode(0, "I m alive"))
    exit(0)
else:
    print(u.returncode(1, "Can't connect"))
    exit(1)