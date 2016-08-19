import ims.common.config as config

config.load()

import ims.picasso.rest as rest

rest.setup_rpc()

from ims.picasso.rest import app as application