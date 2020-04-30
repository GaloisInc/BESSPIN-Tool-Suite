# This file has the necessary includes to run Fett on FreeRTOS

WOLFSSL_SOURCE_DIR = $(FREERTOS_PLUS_SOURCE_DIR)/WolfSSL_Galois
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

CFLAGS += -DmainDEMO_TYPE=12 
CFLAGS += -DtestgenOnFreeRTOS -DtestgenFPGA
DEMO_SRC = main.c \
	$(wildcard $(INC_TESTGEN)/*.c) \
	$(wildcard $(INC_TESTGEN)/lib/*.c)
INCLUDES += -I$(INC_TESTGEN)/lib
INCLUDES += -I$(INC_TESTGEN)
CFLAGS := $(filter-out -Werror,$(CFLAGS))

#CFLAGS += -I$(FREERTOS_IP_INCLUDE)
#CFLAGS += -I$(WOLFSSL_SOURCE_DIR)
#FREERTOS_SRC += $(FREERTOS_IP_SRC)
#DEMO_SRC += $(FREERTOS_IP_DEMO_SRC)
#DEMO_SRC += $(WOLFSSL_SRC)
#INCLUDES += -I$(WOLFSSL_SOURCE_DIR)

include $(INC_TESTGEN)/envApp.mk
