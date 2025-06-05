import paramiko
import os
import socket
from typing import Tuple
from .exceptions import SSHConnectionError

class SSHClient:
    def __init__(self, hostname: str, username: str, port: int = 22, key_filename: str = None):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.key_filename = key_filename
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, timeout: int = 10):
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                key_filename=self.key_filename,
                timeout=timeout
            )
        except (paramiko.AuthenticationException, paramiko.SSHException, socket.error) as e:
            raise SSHConnectionError(f"Failed to connect to {self.username}@{self.hostname}:{self.port} - {str(e)}")

    def exec_command(self, command: str, timeout: int = None) -> Tuple[int, str, str]:
        if not self.client.get_transport() or not self.client.get_transport().is_active():
            self.connect()
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            return exit_status, stdout.read().decode().strip(), stderr.read().decode().strip()
        except Exception as e:
            raise SSHConnectionError(f"Failed to execute command '{command}' - {str(e)}")

    def close(self):
        self.client.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
