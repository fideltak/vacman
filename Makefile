LINE_NOTIFY_WEB_IMAGE_NAME = line-notify-web
VACCINE_CHECKER_IMAGE_NAME = vaccine-checker
CONTAINER_REGISTRY=docker.io/fideltak

build:
	@echo "Build container images"; \
	$(eval VERSION=$(shell sh -c "git describe --tags --abbrev=0")) \
	cd ./${LINE_NOTIFY_WEB_IMAGE_NAME}; \
	docker build -t ${CONTAINER_REGISTRY}/${LINE_NOTIFY_WEB_IMAGE_NAME}:${VERSION} .; \
	cd ../${VACCINE_CHECKER_IMAGE_NAME}; \
	docker build -t ${CONTAINER_REGISTRY}/${VACCINE_CHECKER_IMAGE_NAME}:${VERSION} .; \

push:
	@echo "Push container images"; \
	$(eval VERSION=$(shell sh -c "git describe --tags --abbrev=0")) \
	cd ./${LINE_NOTIFY_WEB_IMAGE_NAME}; \
	docker push ${CONTAINER_REGISTRY}/${LINE_NOTIFY_WEB_IMAGE_NAME}:${VERSION}; \
	cd ../${VACCINE_CHECKER_IMAGE_NAME}; \
	docker push ${CONTAINER_REGISTRY}/${VACCINE_CHECKER_IMAGE_NAME}:${VERSION}; \