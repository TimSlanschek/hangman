# Contents for Python Makefile 
PY = python3

all: server client

# make sure TAs can make server/client/clean
server:
client:
clean:

run-server: server_single.py
	$(PY) $< 127.0.0.1 9012
run-client: client_single.py
	$(PY) $< 127.0.0.1 9012
run-server-multi: server_multi.py
	$(PY) $< 127.0.0.1 9012
run-client-multi: client_multi.py
	$(PY) $< 127.0.0.1 9012