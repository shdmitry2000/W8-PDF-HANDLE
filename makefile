IMAGE_NAME = ubuntu-tesseract-python-pdf
IMAGE_NAME2 = UIW8Container

build:
	# docker build -t $(IMAGE_NAME) .
	docker compose build

run:
	docker compose up
clean:
	docker stop $$(docker ps -a -q) 2>/dev/null
	docker rm $$(docker ps -a -q) 2>/dev/null
	docker rmi $(IMAGE_NAME) 2>/dev/null
	docker rmi $(MAGE_NAME2) 2>/dev/null
# stop:
# 	docker stop $$(docker ps -a -q) 2>/dev/null

.PHONY: build run clean