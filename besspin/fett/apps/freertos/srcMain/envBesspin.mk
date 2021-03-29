# This file has the necessary includes to run Besspin on FreeRTOS

CFLAGS += -DBESSPIN_TOOL_SUITE

WOLFSSL_SOURCE_DIR = ./WolfSSL-BESSPIN
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

# BESSPIN Apps sources
DEMO_SRC = main.c \
	$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c) \
	$(wildcard $(INC_BESSPIN_TOOL_SUITE)/appLib/*.c)
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/appLib
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)

# Network
CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# WolfSSL
CFLAGS += -I$(WOLFSSL_SOURCE_DIR)
DEMO_SRC += $(WOLFSSL_SRC)
INCLUDES += -I$(WOLFSSL_SOURCE_DIR)

# FAT Filesystem
CFLAGS += -DFATFS_$(FATFS)

ifneq (,$(filter $(FATFS),DOSBLK RAMDISK))
	SD_SOURCE_DIR = ./FatFs/source
	DEMO_SRC += $(SD_SOURCE_DIR)/ff.c \
				$(SD_SOURCE_DIR)/ffsystem.c \
				$(SD_SOURCE_DIR)/ffunicode.c
	INCLUDES += -I$(SD_SOURCE_DIR)
endif

ifeq ($(FATFS),DOSBLK)
	DEMO_SRC += $(SD_SOURCE_DIR)/diskio.c
endif

ifeq ($(FATFS),RAMDISK)
	ifeq ($(RAMDISK_NUM_SECTORS),)
		$(error "RAMDISK_NUM_SECTORS not set even though FATFS=RAMDISK")
	endif
	CFLAGS += -DRAMDISK_NUM_SECTORS=$(RAMDISK_NUM_SECTORS)
	DEMO_SRC += $(SD_SOURCE_DIR)/diskio_ram.c
endif

ifeq ($(FATFS),SDCARD)
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

