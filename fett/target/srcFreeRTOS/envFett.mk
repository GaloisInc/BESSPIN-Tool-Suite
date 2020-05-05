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

DEMO_SRC = main.c \
	$(wildcard $(INC_FETT_APPS)/*.c) \
	$(wildcard $(INC_FETT_APPS)/appLib/*.c)
INCLUDES += -I$(INC_FETT_APPS)/appLib
INCLUDES += -I$(INC_FETT_APPS)
CFLAGS := $(filter-out -Werror,$(CFLAGS))

CFLAGS += -I$(FREERTOS_IP_INCLUDE)
CFLAGS += -I$(WOLFSSL_SOURCE_DIR)
FREERTOS_SRC += $(FREERTOS_IP_SRC)
DEMO_SRC += $(WOLFSSL_SRC)
INCLUDES += -I$(WOLFSSL_SOURCE_DIR)
