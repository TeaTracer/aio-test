gunicorn \
    main:app \
    --bind localhost:8080 \
    --worker-class aiohttp.worker.GunicornWebWorker \
    --certfile /etc/ssl/server.crt \
    --keyfile /etc/ssl/server.key \
    --timeout 120
