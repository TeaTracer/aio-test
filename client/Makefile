install:
	npm install

build: static
	npm run build

dev: static
	npm run dev

static:
	@if [ ! -f "dist/index.html" ]; then \
	   	mkdir -p "dist" && cp "src/index.html" "dist/index.html" && echo "Copy static files"; \
	fi

clean:
	rm -rf dist/*

uninstall:
	rm -rf node_modules dist
