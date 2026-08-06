.PHONY: clean clean-forecasts-dl clean-measurements-dl version up-major up-minor up-patch print-version

clean-forecasts-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/forecasts/dl/*.csv

clean-measurements-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/measurements/dl/*.csv

clean: clean-forecasts-dl clean-measurements-dl


version:
	@uv version #| awk '{print $2}'

up-major:  # Upgrading X in X.Y.Z
	@echo "Upgrading major tag from version"
	@uv version --bump=major
	$(MAKE) print-version

up-minor:  # Upgrading Y in X.Y.Z
	@echo "Upgrading minor tag from version"
	@uv version --bump=minor
	$(MAKE) print-version

up-patch:  # Upgrading Z in X.Y.Z
	@echo "Upgrading patch tag from version"
	@uv version --bump=patch
	$(MAKE) print-version

print-version:
	@echo "Printing version to .project-version"
	@uv version | awk '{print $$2}' > .project-version
