# Project Title

Test web application with acyncio, aiohttp and aiopg. 

### Prerequisites

Ubuntu 16.04 LTS or Vagrant with VirtualBox
512 MB of RAM
Intel x86\_64 processor with 2+ cores
512 MB of available disk space
Python 3.6+

### Deployment

# Clone repository

```
git clone https://github.com/TeaTracer/aio-test.git
cd aio-test
```

# Physical server

```
make deploy

```

# or Vagrant

```
vagrant up
vagrant ssh
cd /vagrant
make deploy
```

### License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details
