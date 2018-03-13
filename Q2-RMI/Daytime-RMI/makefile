JAVAC=javac
sources = $(wildcard *.java)
classes = $(sources:.java=.class)

all: $(classes)

%.class : %.java
	$(JAVAC) $<

clean :
	rm -f *.class

