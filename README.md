# Create layer
run:
1. cd temporal_pkg
2. `pip install -r requirements.txt --platform=manylinux2014_x86_64 --only-binary=:all: --target ./python/lib/python3.11/site-packages/`
3. `zip -r layer.zip python`