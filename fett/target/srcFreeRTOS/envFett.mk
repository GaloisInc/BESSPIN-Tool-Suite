# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DFETT_APPS

WOLFSSL_SOURCE_DIR = $(FREERTOS_PLUS_SOURCE_DIR)/WolfSSL
WOLFSSL_SRC = $(WOLFSSL_SOURCE_DIR)/src/ssl.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/logging.c \
			  $(WOLFSSL_SOURCE_DIR)/src/tls.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/memory.c \
			  $(WOLFSSL_SOURCE_DIR)/src/internal.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/wc_port.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/asn.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/coding.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/rsa.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/hmac.c \
			  $(WOLFSSL_SOURCE_DIR)/src/io.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/md5.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/hash.c \
			  $(WOLFSSL_SOURCE_DIR)/src/keys.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/sha.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/sha256.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/sha512.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/random.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/error.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/integer.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/aes.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/pwdbased.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/fe_operations.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/ge_operations.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/curve25519.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/ed25519.c

# FETT Apps sources
DEMO_SRC = main.c \
	$(wildcard $(INC_FETT_APPS)/*.c) \
	$(wildcard $(INC_FETT_APPS)/appLib/*.c)
INCLUDES += -I$(INC_FETT_APPS)/appLib
INCLUDES += -I$(INC_FETT_APPS)

# Network
CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# WolfSSL
CFLAGS += -I$(WOLFSSL_SOURCE_DIR)
DEMO_SRC += $(WOLFSSL_SRC)
INCLUDES += -I$(WOLFSSL_SOURCE_DIR)

# Filesystem
ifeq ($(BSP),aws)
	# AWS & IceBlk driver
	CFLAGS += -DFETT_AWS
	SD_SOURCE_DIR = ./FatFs/source
	DEMO_SRC += $(SD_SOURCE_DIR)/ff.c \
				$(SD_SOURCE_DIR)/ffsystem.c \
				$(SD_SOURCE_DIR)/ffunicode.c
	INCLUDES += -I$(SD_SOURCE_DIR)

ifeq ($(FREERTOS_USE_RAMDISK),1)
	ifeq ($(RAMDISK_NUM_SECTORS),)
		$(error "RAMDISK_NUM_SECTORS not set even though FREERTOS_USE_RAMDISK=1")
        endif
	CFLAGS += -DFREERTOS_USE_RAMDISK
        CFLAGS += -DRAMDISK_NUM_SECTORS=$(RAMDISK_NUM_SECTORS)
	DEMO_SRC += $(SD_SOURCE_DIR)/diskio_ram.c
else
	DEMO_SRC += $(SD_SOURCE_DIR)/diskio.c
endif

else
	# FPGA & SD Lib
	SD_SOURCE_DIR = ./SD/src
	CPP_SRC += $(SD_SOURCE_DIR)/SD.cpp \
			   $(SD_SOURCE_DIR)/File.cpp \
			   $(SD_SOURCE_DIR)/utility/Sd2Card.cpp \
			   $(SD_SOURCE_DIR)/utility/SdFile.cpp \
			   $(SD_SOURCE_DIR)/utility/SdVolume.cpp \
			   $(SD_SOURCE_DIR)/SDLib.cpp
	INCLUDES += -I$(SD_SOURCE_DIR)
endif
