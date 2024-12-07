from netmiko import ConnectHandler
from typing import List
import logging


class RouterConfigurator:
    def __init__(self, ip: str, username: str, password: str, secret: str):
        """
        Initialize RouterConfigurator with connection details.

        :param ip: Router IP address
        :param username: SSH username
        :param password: SSH password
        :param secret: Router enable secret
        """
        self.device = {
            'device_type': 'cisco_ios',
            'host': ip,
            'username': username,
            'password': password,
            'secret': secret,
            'timeout': 100,
        }

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            filename="router_config.log",
        )
        self.logger = logging.getLogger(__name__)

    def configure_router(self, commands: List[str]) -> bool:
        """
        Configure router with provided commands.

        :param commands: List of configuration commands
        :return: Boolean indicating success or failure
        """
        try:
            connection = ConnectHandler(**self.device)
            self.logger.info(f"Connected to router at {self.device['host']}")

            # Enter enable mode
            if not connection.check_enable_mode():
                connection.enable()

            # Send configuration commands
            output = connection.send_config_set(commands)
            self.logger.info(f"Commands executed:\n{output}")

            # Save configuration
            connection.save_config()
            self.logger.info("Configuration saved successfully.")

            # Disconnect
            connection.disconnect()
            return True

        except Exception as e:
            self.logger.error(f"Configuration failed: {e}")
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
            "do write memory",
        ]
