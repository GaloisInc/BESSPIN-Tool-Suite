# This file has the necessary includes to run OTA tests on FreeRTOS

CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)
DEMO_SRC += $(FREERTOS_IP_DEMO_SRC)
