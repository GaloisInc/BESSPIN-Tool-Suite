# This file has the necessary includes to run Fett on FreeRTOS in cwesEvaluation Mode for PPAC

CFLAGS += -DFETT_APPS -DFETT_AWS -DtestgenOnFreeRTOS -DtestgenFPGA

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
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/random.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/arc4.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/des3.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/rabbit.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/error.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/integer.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/aes.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/pwdbased.c \
			  $(WOLFSSL_SOURCE_DIR)/wolfcrypt/src/dh.c

DEMO_SRC = main.c \
    $(wildcard $(INC_FETT_APPS)/*.c) \
    $(wildcard $(INC_FETT_APPS)/lib_PPAC/*.c) \
    $(EXTRA_TEST_SOURCES)

INCLUDES += -I$(INC_FETT_APPS)
INCLUDES += -I$(INC_FETT_APPS)/lib_PPAC

# Network
CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# WolfSSL
CFLAGS += -I$(WOLFSSL_SOURCE_DIR)
DEMO_SRC += $(WOLFSSL_SRC)
INCLUDES += -I$(WOLFSSL_SOURCE_DIR)

