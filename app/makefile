
#
# @infos: recursively find files in a given dir
#
# @uses:
# $(call rwildcard,$(DIR),$(MATCH))
#
# @param <DIR>: directory to search in
# @param <MARCH>: file match (ex: *.c)
#
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))

python_tests = $(call rwildcard,./,*.test.py)
shell_tests = $(call rwildcard,./,*.test.sh)

.PHONY: tests
tests: $(python_tests) $(shell_tests)
	@echo "# All tests passed"

.PHONY: $(python_tests)
$(python_tests): %:
	@echo "# testing <$@>..."
	@python $@

.PHONY: $(shell_tests)
$(shell_tests): %:
	@echo "# testing <$@>"
	@sh $@

