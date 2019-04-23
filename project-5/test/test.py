import socket

amazon_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the server on local computer

try:
    amazon_fd.connect(('vcm-8250.vm.duke.edu', 55555))
except (ConnectionRefusedError, ConnectionResetError,
        ConnectionError, ConnectionAbortedError) as error:
    print(error)