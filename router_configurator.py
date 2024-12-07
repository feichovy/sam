import paramiko
import logging
from typing import List, Optional

class RouterConfigurator:
    def __init__(self, ip: str, username: str, password: str):
        """
        Initialize RouterConfigurator with connection details.
        
        :param ip: Router IP address
        :param username: SSH username
        :param password: SSH password
        """
        self.ip = ip
        self.username = username
        self.password = password
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='router_config.log'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> Optional[paramiko.SSHClient]:
        """
        Establish SSH connection to the router.
        
        :return: SSHClient object or None if connection fails
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password)
            self.logger.info(f"Successfully connected to router at {self.ip}")
            return ssh
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return None

    def configure_router(self, commands: List[str]) -> bool:
        """
        Configure router with provided commands.
        
        :param commands: List of configuration commands
        :return: Boolean indicating success or failure
        """
        ssh = self.connect()
        if not ssh:
            return False

        try:
            # Start interactive shell
            remote_conn = ssh.invoke_shell()
            remote_conn.send("terminal length 0\n")
            
            # Execute commands with logging
            for cmd in commands:
                remote_conn.send(cmd + "\n")
                self.logger.info(f"Executing: {cmd}")
                paramiko.invoke_shell.transport.recv_exit_status()

            # Save running configuration
            remote_conn.send("do write memory\n")
            
            # Retrieve and save configuration
            remote_conn.send("show running-config\n")
            output = remote_conn.recv(65535).decode('utf-8')
            
            with open("router_config_backup.txt", "w") as file:
                file.write(output)
            
            self.logger.info("Router configuration completed successfully")
            ssh.close()
            return True

        except Exception as e:
            self.logger.error(f"Configuration error: {e}")
            return False

    @staticmethod
    def get_default_commands() -> List[str]:
        """
        Provide default router configuration commands.
        
        :return: List of default configuration commands
        """
        return [
            "configure terminal",
            "interface loopback0",
            "ip address 192.168.1.1 255.255.255.255",
            "no shutdown",
            "exit",
            "interface gigabitEthernet0/1",
            "ip address 192.168.2.1 255.255.255.0",
            "no shutdown",
            "exit",
            "router ospf 1",
            "network 192.168.1.1 0.0.0.0 area 0",
            "network 192.168.2.0 0.0.0.255 area 0",
            "exit",
            "access-list 100 permit tcp any any eq 22",
            "access-list 100 deny ip any any",
            "ip access-group 100 in",
            "do write memory"
        ]

# Example usage
if __name__ == "__main__":
    router = RouterConfigurator(
        ip="192.168.2.1", 
        username="admin", 
        password="admin"
    )
    success = router.configure_router(router.get_default_commands())
    print("Configuration successful" if success else "Configuration failed")