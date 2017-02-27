/usr/local/bin/gunicorn \
    server:app \
    --bind localhost:8080 \
    --worker-class aiohttp.worker.GunicornWebWorker \
    --certfile /etc/ssl/server.crt \
    --keyfile /etc/ssl/server.key
