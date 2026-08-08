POSTAL_CODES_CSV_ZIP := https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz_2056.csv.zip
POSTAL_CODES_TEMP_ZIP := data/temp.zip

.PHONY: clean clean-forecasts-dl clean-measurements-dl version up-major up-minor up-patch print-version dl-postal-codes clean-postal-codes

clean-forecasts-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/forecasts/dl/*.csv

clean-measurements-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/measurements/dl/*.csv

clean: clean-forecasts-dl clean-measurements-dl clean-postal-codes


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

dl-postal-codes:
	@echo "Downloading postal codes list..."
	#@cd data/
	@wget $(POSTAL_CODES_CSV_ZIP) -O $(POSTAL_CODES_TEMP_ZIP)
	@unzip $(POSTAL_CODES_TEMP_ZIP) -d data/
	@mv data/AMTOVZ_CSV_LV95/AMTOVZ_CSV_LV95.csv data/postal_codes.csv
	@rmdir data/AMTOVZ_CSV_LV95
	@rm $(POSTAL_CODES_TEMP_ZIP)

clean-postal-codes:
	@echo "Cleaning postal codes"
	@rm -rf data/postal_codes.csv
