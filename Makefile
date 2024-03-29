#
# File          : Makefile
# Description   : Build file for CSE473 project 2


# Environment Setup
# Deafault: Linux
OS_NAME=$(shell uname -s)

LIBDIRS=-L. 
INCLUDES=-I.
CC=gcc 
CFLAGS=-c $(INCLUDES) -g -Wall -pthread
LINK=gcc -g -pthread
LDFLAGS=$(LIBDIRS)
AR=ar rc
RANLIB=ranlib

ifeq ($(OS_NAME),Darwin)  # Mac OS X
LIBDIRS=-L. 
INCLUDES=-I.
CC=gcc-5 
CFLAGS=-c $(INCLUDES) -g -Wall -pthread
LINK=gcc-5 -g -pthread
LDFLAGS=$(LIBDIRS)
AR=ar rc
RANLIB=ranlib
endif
# Suffix rules
.c.o :
	${CC} ${CFLAGS} $< -o $@

#
# Setup builds

PT-TARGETS=cse473-p2
CSE473LIB=
CSE473LIBOBJS=

# proj lib
LIBS=

#
# Project Protections

p3 : $(PT-TARGETS)

cse473-p2 : p2_main.o p2_thread_reader.o p2_thread_writer.o p2_locks.o p2_queue.o
	$(LINK) $(LDFLAGS) p2_main.o p2_thread_reader.o p2_thread_writer.o p2_locks.o p2_queue.o -o $@

lib$(CSE473LIB).a : $(CSE473LIBOBJS)
	$(AR) $@ $(CSE473LIBOBJS)
	$(RANLIB) $@

run:
	@cp ../test/2000010.txt ./test
	@cp ../test/ethics.txt ./test
	@cp ../test/gems.txt ./test
	./cse473-p2 ./test 2 > log.txt

runtest2:
	@cp ../test/2000010.txt ./test
	@cp ../test/ethics.txt ./test
	@cp ../test/gems.txt ./test
	@echo "=========== Before Scan ==========="
	@grep -r -E 'but|and|rat|and|far' ./test | wc -l
	./cse473-p2 ./test 2 > log.txt
	@echo "=========== After Scan ==========="
	@grep -r -E 'but|and|rat|and|far' ./test | wc -l
	python test.py -i log.txt
runtest3:
	@cp ../test/2000010.txt ./test
	@cp ../test/ethics.txt ./test
	@cp ../test/gems.txt ./test
	@echo "=========== Before Scan ==========="
	@grep -r -E 'but|and|rat|and|far' ./test | wc -l
	./cse473-p2 ./test 3 > log.txt
	@echo "=========== After Scan ==========="
	@grep -r -E 'but|and|rat|and|far' ./test | wc -l
	python test.py -i log.txt

refreshtest:
	@cp ../test/2000010.txt ./test
	@cp ../test/ethics.txt ./test
	@cp ../test/gems.txt ./test


clean:
	rm -f *.o *~ $(TARGETS) $(LIBOBJS) lib$(CSE473LIB).a 

BASENAME=p2
PSUID=938538712
tar: 
	tar cvfz $(PSUID).tgz -C ..\
	    $(BASENAME)/Makefile \
	    $(BASENAME)/p2_main.c \
	    $(BASENAME)/p2_main.h \
	    $(BASENAME)/p2_thread_reader.c \
	    $(BASENAME)/p2_thread_writer.c \
	    $(BASENAME)/p2_queue.c \
	    $(BASENAME)/p2_locks.c \
	    $(BASENAME)/README \
	    $(BASENAME)/test
