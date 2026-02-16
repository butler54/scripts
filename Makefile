SCRIPTS := $(wildcard bin/*)
TARGETS := $(addprefix $(HOME)/bin/,$(notdir $(SCRIPTS)))

.PHONY: install uninstall

install: $(TARGETS)

$(HOME)/bin/%: bin/%
	@mkdir -p $(HOME)/bin
	ln -sf $(abspath $<) $@

uninstall:
	@for f in $(notdir $(SCRIPTS)); do rm -f $(HOME)/bin/$$f; done
