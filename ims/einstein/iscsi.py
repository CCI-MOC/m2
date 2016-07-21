import subprocess

class IET:

    def __init__(self):
        pass

    def create_mapping(self,ceph_img_name):
        pass

    def delete_mapping(self,ceph_img_name):
        pass

    def show_mappings(self):
        pass

    def __execute_map(self):
        pass

    def __execute_unmap(self):
        pass

    def execute_showmapped(self):
        p = subprocess.Popen('rbd showmapped',shell=True)
        str = p.communicate()
        print str


if __name__ == '__main__':
    iet = IET()
    iet.execute_showmapped()
