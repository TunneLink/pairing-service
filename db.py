# SPDX-License-Identifier: Apache-2.0

import time
import logging
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self):
        """
        Initializes the in-memory database for storing server information.
        """
        self.servers: Dict[str, dict] = {}

    def add_server(self, pubkey: str, username: str, ssh_tunnel: int, listen_pubkey_tunnel: int, pairing_code: int) -> None:
        """
        Adds a new server to the database.

        Args:
            pubkey (str): Server's SSH public key.
            username (str): SSH username.
            ssh_tunnel (int): Tunnel port for SSH.
            listen_pubkey_tunnel (int): Tunnel port for receiving public keys.
            pairing_code (int): Generated pairing code for the server.
        """
        self.servers[pubkey] = {
            "ssh_user": username,
            "ssh_tunnel": ssh_tunnel,
            "listen_pubkey_tunnel": listen_pubkey_tunnel,
            "pairing_code": pairing_code,
            "last_heartbeat": time.time(),
            "online": True
        }
        logging.info(f"Server added: {pubkey}")

    def get_server_by_pairing_code(self, pairing_code: int) -> Optional[Dict[str, Optional[str]]]:
        """
        Retrieves the server details by pairing code.

        Args:
            pairing_code (int): The pairing code to look up.

        Returns:
            dict: Server details (pubkey, username, ssh_tunnel, listen_pubkey_tunnel) or an error if the pairing code is not found.
        """
        for server_pubkey, server in self.servers.items():
            if server["pairing_code"] == pairing_code:
                logging.info(f"Found server with pairing code: {pairing_code}")
                return {
                    "ssh_pubkey": server_pubkey,
                    "ssh_user": server["ssh_user"],
                    "ssh_tunnel": server["ssh_tunnel"],
                    "listen_pubkey_tunnel": server["listen_pubkey_tunnel"]
                }
        logging.warning(f"Pairing code not found: {pairing_code}")
        return {"error": "Pairing code not found"}

    def is_server_registered(self, pubkey: str) -> bool:
        """
        Checks if the server is registered in the database.

        Args:
            pubkey (str): SSH public key of the server.

        Returns:
            bool: True if server is registered, False otherwise.
        """
        return pubkey in self.servers

    def update_server_heartbeat(self, pubkey: str) -> Optional[Dict[str, Optional[bool]]]:
        """
        Updates the heartbeat timestamp for a server only if it's online.

        Args:
            pubkey (str): SSH public key of the server.

        Returns:
            dict: Updated server state or an error message if the server is not registered or offline.
        """
        if self.is_server_registered(pubkey):
            server = self.servers[pubkey]
            if server["online"]:
                server["last_heartbeat"] = time.time()
                logging.info(f"Heartbeat updated for online server: {pubkey}")
                return {"error": "Server is offline. Heartbeat not updated."}
            else:
                logging.warning(f"Cannot update heartbeat, server is offline: {pubkey}")
            return self.get_server_state(pubkey)
        else:
            logging.warning(f"Attempted heartbeat update for unregistered server: {pubkey}")
            return {"error": "Server not registered"}

    def get_server_state(self, pubkey: str) -> Optional[Dict[str, Optional[bool]]]:
        """
        Retrieves the current state of a server.

        Args:
            pubkey (str): SSH public key of the server.

        Returns:
            dict: Current state (online and last_heartbeat) or an error message if the server is not found.
        """
        if self.is_server_registered(pubkey):
            server_state = {
                "online": self.servers[pubkey]["online"],
                "last_heartbeat": self.servers[pubkey]["last_heartbeat"]
            }
            logging.info(f"Retrieved server state for: {pubkey}")
            return server_state
        else:
            logging.warning(f"Attempted server state retrieval for unregistered server: {pubkey}")
            return {"error": "Server not registered"}
