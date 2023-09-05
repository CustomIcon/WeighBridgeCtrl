.PHONY: build

# Define variables for the command and arguments
FLET_CMD := flet pack
ICON := .\assets\favicon.ico
APP_NAME := WBC
PRODUCT_NAME := WBC
FILE_VERSION := 0.1
COMPANY_NAME := WAMCO
MAIN_PY := .\main.py

# Define the target to build the application
build:
	$(FLET_CMD) --icon $(ICON) -n $(APP_NAME) --product-name $(PRODUCT_NAME) --file-version $(FILE_VERSION) --company-name $(COMPANY_NAME) $(MAIN_PY)