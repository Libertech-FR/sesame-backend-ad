import sys
sys.path.insert(0, '../lib')
import ad_utils as ad
import backend_utils as u

entity=u.readjsoninput()
config=u.read_config('../etc/config.conf')
ad.set_config(config)
## test connection