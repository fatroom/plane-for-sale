PROJECT = plane-for-sale
FUNCTION = $(PROJECT)

build: clean
	mkdir -p build/site-packages
	pip install -t ./build/site-packages -r requirements.txt
	(cd build/site-packages && zip -r ../$(FUNCTION).zip .)
	zip -g build/$(FUNCTION).zip lambda_function.py
	zip -r -g build/$(FUNCTION).zip templates

clean:
	rm -rf build

localdeps:
	pip install -r requirements.txt
	pip install boto3
