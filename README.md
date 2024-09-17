# TunneLink Service

TunneLink Service provides a server registration and pairing service for TunneLink server that allows TunneLink clients to retrieve server details based on a unique `pairing_code`. It supports features like server registration, heartbeat updates, and status retrieval.

## Features

- **Server Registration:** Register a server with its SSH public key, SSH user, SSH tunnel, and a tunnel for receiving public keys.
- **Heartbeat Mechanism:** Servers send heartbeats to indicate they are still online.
- **Server Status:** Clients can query the server's online/offline status and retrieve its details.
- **Pairing Code Retrieval:** Clients can request server details (SSH public key, SSH user, etc.) using a unique 4-digit pairing code.

## Installation

### Prerequisites

- Python 3.x
- Flask (`pip install flask`)

### Install Dependencies

```bash
pip install flask
```

### Running the Application

1. Clone the repository.

```bash
git clone https://github.com/TunneLink/service
```

2. Navigate to the project directory.

```bash
cd service
```

3. Run the Flask application.

```bash
python app.py
```

The service will start and listen on `http://localhost:3555`.

## API Endpoints

### 1. Register Server

**Endpoint:** `/register_server`
**Method:** `POST`

**Description:** Registers a server and returns a unique 4-digit pairing code.

**Request Body:**

```json
{
    "ssh_pubkey": "<server SSH public key>",
    "ssh_user": "<SSH username>",
    "ssh_tunnel": 3522,
    "listen_pubkey_tunnel": 3533
}
```

**Response:**

```json
{
    "pairing_code": 1234
}
```

### 2. Server Status (Heartbeat & Status Retrieval)

**Endpoint:** `/server_status`
**Method:** `POST`

**Description:** Handles server heartbeat updates or returns the server's status.

#### Heartbeat

The server sends periodic heartbeat requests to indicate it is still online. Heartbeat updates will **only occur if the server is currently marked as online**.

If a server is not marked as online (e.g., it has been offline for a while), heartbeats will not be processed until the server is re-registered.

**Request Body for Heartbeat:**

```json
{
    "ssh_pubkey": "<server SSH public key>",
    "action": "heartbeat"
}
```

**Response for Heartbeat:**

```json
{
    "online": true,
    "last_heartbeat": 1668612781.123456
}
```

If the server is offline, the response will indicate:

```json
{
    "error": "Server is offline. Heartbeat not updated."
}
```

#### Get Server Status

Clients can also query the server's status to check if it's online and get the timestamp of the last heartbeat.

**Request Body for Status Retrieval:**

```json
{
    "ssh_pubkey": "<server SSH public key>",
    "action": "get_server_status"
}
```

**Response for Server Status:**

```json
{
    "online": true,
    "last_heartbeat": 1668612781.123456
}
```

If the server is not found, the response will indicate:

```json
{
    "error": "Server not registered"
}
```

### 3. Retrieve Server Details by Pairing Code

**Endpoint:** `/get_server_details`
**Method:** `POST`

**Description:** Retrieves server details (SSH public key, SSH user, etc.) by using the provided pairing code.

**Request Body:**

```json
{
    "pairing_code": 1234
}
```

**Response:**

```json
{
    "ssh_pubkey": "AAAAB3NzaC1yc2EAAAABIwAAAQEArlNeGm...",
    "ssh_user": "server_user",
    "ssh_tunnel": 3522,
    "listen_pubkey_tunnel": 3533
}
```

### Error Handling

- Missing keys or invalid requests will return `HTTP 400 Bad Request`.
- If the server is not found, the response will return `HTTP 404 Not Found`.
- For internal server errors, the response will return `HTTP 500 Internal Server Error`.

## Logging

The application uses basic logging to track actions like server registration, heartbeat updates, and errors. Logs are output to the console with different log levels (`INFO`, `WARNING`, `ERROR`).

## License

TunneLink Service is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.