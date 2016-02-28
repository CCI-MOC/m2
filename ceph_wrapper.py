import rados
import rbd
import os


class CephBase(object):

	def __init__(self, rid, r_conf, pool, debug=None):
		if not rid or not r_conf or not pool:
			raise Exception("one or more arguments for ceph is incorrect")
		if not os.file.isfile(r_conf):
			raise Exception("invalid configuration file")
		if not self.client:
			raise Exception("invalid client, aborting ... ")
		self.rid = rid
		self.r_conf = r_conf
		self.pool = pool
		self.cluster = __init_cluster()
		self.ctx = __init_context(self)
		self.rbd = __init_rbd()	


#
# log in case of debug
#
		if debug:
			print self

	def __str__():
		return 'rid = {0}, conf_file = {1}, pool\
		 	= {2}, is_debug? {3}'.format(rid,   \
			 r_conf, pool, debug)		

	def __init_context(self):
		try:
			return  self.client.open_ioctx(self.\
				pool.encode('utf-8'))
		except Exception as e:
			raise e
	def __init_cluster(self):
		try:
			self.client = rados.Rados(self.rid, self.r_conf)
			return cluster.connect()
		except Exception as e:
			raise e

	def __init_rbd(self):
		try:
			return rbd.RBD() 
		except Exception as e:
			raise e


# define this function in the derivative class
# to be specific for the call.
	def run(self):
		pass

# this is the teardown section, we undo things here
	def __td_context(self):
		self.ctx.close()	

	def __td_rbd():
		self.rbd.close()

	def __td_cluster():
		self.cluster.shutdown()

	def tear_down(self):
		try:
			__td_rbd()
			__td_context()
			__td_cluster()
		except Exception as e:
			raise e



class RBDList(CephBase):
	def run():
		try:
			return self.rbd.list(self.ctx)
		except Exception as e:
			raise e
