##
##
##
STORE       ?= basic
INTERPRETER ?= basic
TEST        ?= test
PARAMETERS  ?= include/parameters

#STORE_SIZE ?= 3
#NDOMAINS   ?= 2
DEBUG      ?= 0

ifeq ($(DEBUG),1)
	override CFLAGS += -DDEBUG
	override CFLAGS += -g
endif

HEADERS = $(wildcard include/*.h) $(PARAMETERS)/parameters.h
SOURCES = $(wildcard functions/*.c) \
          stores/$(STORE).c \
          interpreters/$(INTERPRETER).c \
	        control/control.c \
	        tests/$(TEST).c

OBJS = $(SOURCES:.c=.o)

override CFLAGS += -I include
override CFLAGS += -I $(PARAMETERS)
## override CFLAGS += -DSTORE_SIZE=$(STORE_SIZE)
## override CFLAGS += -DNDOMAINS=$(NDOMAINS)

$(info BUILDING TEST:)
$(info STORE=$(STORE))
$(info INTERPRETER=$(INTERPRETER))
$(info TEST=$(TEST))

weakness: $(SOURCES) $(HEADERS) functions/functions.tab
	gcc $(CFLAGS) $(SOURCES) -o $(TEST).$(STORE).$(INTERPRETER).riscv

noweakness: $(SOURCES) $(HEADERS) functions/functions.tab
	gcc -DNO_WEAKNESS $(CFLAGS) $(SOURCES) -o $(TEST)

functions/functions.tab: functions
	cd functions && ./tablegen.py

clean:
	-rm -f $(OBJS) */*.o $(TEST) functions/functions.tab
	-rm -r -f *.dSYM
