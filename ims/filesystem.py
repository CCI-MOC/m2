import abc

class FileSystem:

    __metaclass__ = abc.ABCMeta

    def list_images(self):
        pass

    def clone(self):
        pass

    def remove(self):
        pass

    def create_snapshot(self):
        pass

    def list_snapshots(self):
        pass

    def remove_snapshot(self):
        pass

    def create_image(self):
        pass

    def get_image(self):
        pass
