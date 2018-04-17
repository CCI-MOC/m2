
Generally BMI images are centos, we may be requested for Ubuntu at which point we will need to create BMI ubuntu image as follows.

1. Download latest requested (Ubuntu) cloud image or server image.

2. Install dracut 
```
      sudo apt install dracut-core
```

3. Modify dracut.conf to ensure hostonly=“no” . This ensure that the image is generic, if not the image created would contain only dracut modules/filesystems which are needed to boot the current specific machine. Fracut configuration file may be found in below path in ubuntu case.

```
 /etc/dracut.conf.d/10-debian.conf
 ```

 4. If the image is cloud image, disable cloud.init as follows (this ensures cloud based customizations that take longer boot time are disabled), if not skip this step

 ```

 		echo 'datasource_list: [ None ]' | sudo -s tee /etc/cloud/cloud.cfg.d/90_dpkg.cfg
		sudo apt-get purge cloud-init
		sudo rm -rf /etc/cloud/; sudo rm -rf /var/lib/cloud/
		reboot

```

5. Create image by following command

```
		Dracut —force
```

6. Next add Intel 10 Gig NICs. The following link contains the steps for the same (ubuntu).

```
		http://ask.xmodulo.com/download-install-ixgbe-driver-ubuntu-debian.html
```



