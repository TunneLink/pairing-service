# SPDX-License-Identifier: Apache-2.0

from flask import Flask, request, jsonify
import random
import logging

from db import Database

app = Flask(__name__)
db = Database()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/register_server', methods=['POST'])
def register_server():
    """
    Registers a new server with the pairing service.
    Expects JSON with 'ssh_pubkey', 'ssh_user', 'ssh_tunnel', and 'listen_pubkey_tunnel'.
    """
    try:
        data = request.json
        server_pubkey: str = data["ssh_pubkey"]
        server_username: str = data["ssh_user"]
        server_ssh_tunnel: int = data["ssh_tunnel"]
        server_listen_pubkey_tunnel: int = data["listen_pubkey_tunnel"]

        server_pairing_code = random.randint(1000, 9999) # Generate 4 digit number
        db.add_server(pubkey=server_pubkey,
                      username=server_username,
                      ssh_tunnel=server_ssh_tunnel,
                      listen_pubkey_tunnel=server_listen_pubkey_tunnel,
                      pairing_code=server_pairing_code)

        return jsonify({"pairing_code": server_pairing_code}), 201  # HTTP 201 Created
    except KeyError as e:
        logging.error(f"Missing key in request: {e}")
        return jsonify({"error": f"Missing key: {e}"}), 400  # HTTP 400 Bad Request
    except Exception as e:
        logging.error(f"Error registering server: {e}")
        return jsonify({"error": "Internal server error"}), 500  # HTTP 500 Internal Server Error

@app.route('/get_server_details', methods=['POST'])
def get_server_details():
    """
    Retrieves the server details based on the provided pairing code.
    Expects JSON with 'pairing_code'.
    """
    try:
        data = request.json
        pairing_code: int = data["pairing_code"]

        server_details = db.get_server_by_pairing_code(pairing_code)

        # Check if the database returned an error and handle accordingly
        if "error" in server_details:
            logging.error(f"Error retrieving server details: {server_details['error']}")
            return jsonify(server_details), 404  # HTTP 404 Not Found if pairing code is not found
        else:
            return jsonify(server_details), 200  # HTTP 200 OK for successful retrieval
    except KeyError as e:
        logging.error(f"Missing key in request: {e}")
        return jsonify({"error": f"Missing key: {e}"}), 400  # HTTP 400 Bad Request
    except Exception as e:
        logging.error(f"Error retrieving server details: {e}")
        return jsonify({"error": "Internal server error"}), 500  # HTTP 500 Internal Server Error

@app.route('/server_status', methods=['POST'])
def server_status():
    """
    Handles heartbeat and status check actions for a server.
    Expects JSON with 'ssh_pubkey' and 'action' ('heartbeat' or 'get_server_status').
    """
    try:
        data = request.json
        server_pubkey: str = data["ssh_pubkey"]
        action: str = data["action"]

        if action == "heartbeat":
            server_state = db.update_server_heartbeat(server_pubkey)
        elif action == "get_server_status":
            server_state = db.get_server_state(server_pubkey)
        else:
            logging.error(f"Invalid action: {action}")
            return jsonify({"error": "Invalid action"}), 400  # HTTP 400 Bad Request

        # Check if the database returned an error and handle accordingly
        if "error" in server_state:
            logging.error(f"Error in server status: {server_state['error']}")
            return jsonify(server_state), 404  # HTTP 404 Not Found for missing servers
        else:
            return jsonify(server_state), 200  # HTTP 200 OK
    except KeyError as e:
        logging.error(f"Missing key in request: {e}")
        return jsonify({"error": f"Missing key: {e}"}), 400  # HTTP 400 Bad Request
    except Exception as e:
        logging.error(f"Error in server status: {e}")
        return jsonify({"error": "Internal server error"}), 500  # HTTP 500 Internal Server Error

if __name__ == '__main__':
    app.run(port=3555)
