
KVERSION=$(shell uname -r)
KROOT=/lib/modules/$(KVERSION)/build

all:
	$(Q)$(MAKE) -C $(KROOT) M=$(CURDIR) modules

obj-m += pcieportal.o
obj-m += portalmem.o

pcieportal-objs := portal.o libxdma.o xdma_cdev.o cdev_ctrl.o cdev_events.o cdev_sgdma.o cdev_xvc.o cdev_bypass.o xdma_mod.o
pcieportal.ko: driverversion.h

driverversion.h:
	echo "#define DRIVER_VERSION \"20.06.4\"" > driverversion.h
