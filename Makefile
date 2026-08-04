.PHONY: clean clean-forecasts-dl

clean-forecasts-dl:
	@echo "Cleaning forecasts dl"
	@rm -rf data/forecasts/dl/*.csv

clean: clean-forecasts-dl
