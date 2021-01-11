## Parse the name containg the main invocation to figure out which variants
## to use for the test script, store, interpreter. With exception of nonstandard tests

ifeq ($(VARIANT_NAMES),)
	VARIANT_SRC	:= 
else
	VARIANT_SRC	= $(addprefix $(INC_FETT_APPS)/,$(VARIANT_NAMES))
endif

$(info VARIANT_NAMES=$(VARIANT_NAMES))
$(info VARIANT_SRC=$(VARIANT_SRC))


GENERIC_SRC = $(wildcard $(INC_FETT_APPS)/informationLeakage/control/*.c)   \
              $(wildcard $(INC_FETT_APPS)/informationLeakage/functions/*.c) \
              $(wildcard $(INC_FETT_APPS)/*.c)

$(info GENERIC_SRC=$(GENERIC_SRC))

CFLAGS += -DFETT_APPS -DtestgenOnFreeRTOS

ifeq ($(BSP),qemu)
	CFLAGS += -DtestgenQEMU
	APP_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	APP_INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include
	APP_INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include/parameters
	APP_INCLUDES += -I$(INC_FETT_APPS)

	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_FETT_APPS) \
		$(INC_FETT_APPS)/informationLeakage \
		$(INC_FETT_APPS)/informationLeakage/functions \
		$(INC_FETT_APPS)/informationLeakage/control \
		$(INC_FETT_APPS)/informationLeakage/stores \
		$(INC_FETT_APPS)/informationLeakage/interpreters \
		$(INC_FETT_APPS)/informationLeakage/tests
else
	CFLAGS += -DtestgenFPGA
	DEMO_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include
	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include/parameters
	INCLUDES += -I$(INC_FETT_APPS)
endif

ifeq ($(BSP),awsf1)
	CFLAGS += -DFETT_AWS
endif
