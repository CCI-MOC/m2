from abc import ABCMeta
from abc import abstractmethod


class FileSystem(object):
    """
    An abstract class for the filesystem that needs to be implemented by all
    filesystems used by BMI. This should have basic operations that all
    filesystems support. Some of the methods' arguments may be too much
    modelled on ceph. We can change them once we start supporting other
    filesystems.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_images(self):
        """
        Lists all the images available in filesystem.
        """

    @abstractmethod
    def remove_image(self, image):
        """
        Removes the given image from filesystem.
        """

    @abstractmethod
    def create_image(self, image, size):
        """
        Creates an image in the filesystem with given size.
        """

    @abstractmethod
    def snap_image(self, image, snapshot):
        """
        Creates a snapshot for the given image.
        """

    @abstractmethod
    def remove_snapshot(self, image, snap_name):
        """
        Removes the given snapshot for the image.
        """

    @abstractmethod
    def write(self, image, data, offset):
        """
        Writes the given data to image at given offset.
        """

    @abstractmethod
    def clone(self, parent_image, parent_snapshot, image):
        """
        Creates a clone of parent_image at parent_snapshot with image as name.
        """

    @abstractmethod
    def list_snapshots(self, image):
        """
        Lists all the snapshots for image.
        """

    @abstractmethod
    def remove_snapshot(self, image, snap_name):
        """
        Removes snapshot for given image.
        """
