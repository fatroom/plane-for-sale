build: 
	mkdir -p build/site-packages
	pip install -t ./build/site-packages -r requirements.txt
	(cd build/site-packages && zip -r ../plane-finder-package.zip .) 
	zip -g build/plane-finder-package.zip lambda_function.py
	zip -r -g build/plane-finder-package.zip templates

clean:
	rm -rf build

localdeps:
	pip install -r requirements.txt
