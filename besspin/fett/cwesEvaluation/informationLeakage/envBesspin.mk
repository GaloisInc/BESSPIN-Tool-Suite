## Parse the name containg the main invocation to figure out which variants
## to use for the test script, store, interpreter. With exception of nonstandard tests

GENERIC_SRC = $(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
ifeq ($(VARIANT_NAMES),)
	VARIANT_SRC	:= 
	GENERIC_SRC += $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils/*.c)
else
	VARIANT_SRC	= $(addprefix $(INC_BESSPIN_TOOL_SUITE)/,$(VARIANT_NAMES))
	GENERIC_SRC += $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/control/*.c)   \
	              $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/*.c)
endif

$(info VARIANT_NAMES=$(VARIANT_NAMES))
$(info VARIANT_SRC=$(VARIANT_SRC))
$(info GENERIC_SRC=$(GENERIC_SRC))

CFLAGS += -DBESSPIN_TOOL_SUITE -DtestgenOnFreeRTOS
WERROR = 

ifeq ($(BSP),qemu)
	CFLAGS += -DtestgenQEMU
	APP_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include/parameters
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)

	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_BESSPIN_TOOL_SUITE) \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/control \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/interpreters \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils
else
	CFLAGS += -DtestgenFPGA
	DEMO_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include/parameters
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
endif

ifeq ($(BSP),awsf1)
	CFLAGS += -DBESSPIN_AWS
endif
