## Parse the name containg the main invocation to figure out which variants
## to use for the test script, store, interpreter
VARIANT_NAMES = $(shell $(INC_FETT_APPS)/build_source.py $(CWE_TEST))
VARIANT_SRC	  = $(addprefix $(INC_FETT_APPS)/,$(VARIANT_NAMES))

$(info VARIANT_NAMES=$(VARIANT_NAMES))
$(info VARIANT_SRC=$(VARIANT_SRC))


GENERIC_SRC = $(wildcard $(INC_FETT_APPS)/informationLeakage/control/*.c)   \
              $(wildcard $(INC_FETT_APPS)/informationLeakage/functions/*.c) \
              $(INC_FETT_APPS)/$(CWE_TEST).c         \
              $(INC_FETT_APPS)/main_$(CWE_TEST).c

$(info GENERIC_SRC=$(GENERIC_SRC))

ifeq ($(BSP),aws)
	CFLAGS += -DmainDEMO_TYPE=12
	CFLAGS += -DFETT_APPS -DFETT_AWS -DtestgenOnFreeRTOS -DtestgenFPGA

	DEMO_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

$(info DEMO_SRC = $(DEMO_SRC))

	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include
	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include/parameters
  INCLUDES += -I$(INC_FETT_APPS)

	CFLAGS := $(filter-out -Werror,$(CFLAGS))
else
ifeq ($(BSP),fpga)
	CFLAGS += -DmainDEMO_TYPE=12
	CFLAGS += -DFETT_APPS -DtestgenOnFreeRTOS -DtestgenFPGA

	DEMO_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

$(info DEMO_SRC = $(DEMO_SRC))

	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include
	INCLUDES += -I$(INC_FETT_APPS)/informationLeakage/include/parameters
  INCLUDES += -I$(INC_FETT_APPS)

	CFLAGS := $(filter-out -Werror,$(CFLAGS))
else
ifeq ($(TESTGEN_BACKEND),qemu)
CFLAGS += -DtestgenOnFreeRTOS -DtestgenQEMU
APP_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

$(info APP_SRC = $(APP_SRC))

VPATH += \
  $(APP_SRC_DIR) \
  $(APP_SRC_DIR)/full_demo \
  $(INC_FETT_APPS) \
  $(INC_FETT_APPS)/functions \
  $(INC_FETT_APPS)/control \
  $(INC_FETT_APPS)/stores \
  $(INC_FETT_APPS)/interpreters \
  $(INC_FETT_APPS)/tests

APP_INCLUDES += -I$(INC_FETT_APPS)/include -I$(INC_FETT_APPS)/include/parameters
endif
endif
endif
