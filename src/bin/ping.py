import sys
sys.path.append('../lib')
import ad_utils as ad
import backend_utils as u

config=u.read_config('../etc/config.conf')
ad.set_config(config)
## test connection
ad.test_conn()