ACL_STYLE_REPOSITORY := https://github.com/acl-org/acl-style-files.git
ACL_STYLE_COMMIT := d5adc823ff0f80f98c80405ca0ab66c68e684409
ACL_STYLE_DIR := .cache/acl-style-files

.PHONY: all clean

all: build/main.pdf

$(ACL_STYLE_DIR)/acl.sty:
	mkdir -p .cache
	git clone --quiet $(ACL_STYLE_REPOSITORY) $(ACL_STYLE_DIR)
	git -C $(ACL_STYLE_DIR) checkout --quiet $(ACL_STYLE_COMMIT)

build/main.pdf: main.tex sections/01-introduction.tex references.bib $(ACL_STYLE_DIR)/acl.sty
	mkdir -p build
	TEXINPUTS="$(CURDIR)/$(ACL_STYLE_DIR)//:" \
	BSTINPUTS="$(CURDIR)/$(ACL_STYLE_DIR)//:" \
	BIBINPUTS="$(CURDIR):" \
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

clean:
	rm -rf build
