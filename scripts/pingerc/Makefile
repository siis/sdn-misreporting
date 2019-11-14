NAME=
AUTHOR=qkb5007
VERSION=1.0
LINK=gcc
LINKFLAGS= -Wall -g3 -std=gnu99 -lpcap -lpthread #-L. -L/opt/local/lib
LINKLIBS=
LIBFLAGS=
CC=gcc
CFLAGS= -Wall -g3 -std=gnu99 #-I. -I/opt/local/include
ARCHIVE=ar
OBJECTS=flooder.o
TARGETS=main
TEST_TARGETS=

all: $(TARGETS)

test: $(TEST_TARGETS)

main: $(OBJECTS)
	$(LINK) -o main $(OBJECTS) $(LINKFLAGS)

flooder.o: flooder.c
	$(CC) -c $(CFLAGS) flooder.c

clean:
	rm *.o main
