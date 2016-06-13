# Should be used when changed to Flask

import ims.common.config as config

config.load()

import ims.picasso.flask_rest as rest
rest.app.run(host="192.168.122.34",port="8000")
