# Compile info for java compilation
JAVAC=javac
sources = $(wildcard *.java)
classes = $(sources:.java=.class)

# Compile info for rmic compilation. Added nowarn flag to avoid annoying
# deprecation message.
RMIC=rmic
RMIC_FLAGS=-nowarn
REMOTE_OBJS = CurrentDate

all: $(classes)

%.class : %.java
	$(JAVAC) $<

rmic:
	$(RMIC) $(RMIC_FLAGS) $(REMOTE_OBJS)

clean:
	rm -f *.class
