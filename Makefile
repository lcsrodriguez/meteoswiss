.PHONY: clean clean-forecasts-dl clean-measurements-dl

clean-forecasts-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/forecasts/dl/*.csv

clean-measurements-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/measurements/dl/*.csv

clean: clean-forecasts-dl clean-measurements-dl
