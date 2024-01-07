# UDP Communicator

## Overview
UDP Communicator is a Python-based application facilitating communication over a local Ethernet network using a custom protocol atop UDP (User Datagram Protocol). It allows two participants to exchange text messages, files, images, etc.


## Key Features
- **Dual Roles**: Users can choose to be either a sender or a receiver.
- **Custom Header Implementation**: For efficient communication analysis.
- **Data Transmission**: Supports sending messages, files, and images.
- **Role Switching**: Mid-session role switching is possible, allowing dynamic changes between sender and receiver.
- **Error Handling**: Implements error checking and retransmission requests for faulty fragments.

## How It Works
The UDP Communicator operates by establishing a UDP-based connection between two computers on a local network. Upon starting the program, the user can choose to be either a sender or a receiver, which determines the role they will play in the communication process. The application uses a custom protocol header to manage communication, ensuring efficient and organized data transfer. This header allows for the tracking and analysis of the communication session, enhancing error handling and data integrity.
- Start the program and select to be a sender or receiver.
- Define the IP address and port for communication.
- Send or receive messages, files, images, etc.
- Initiate a role switch if needed.

## Requirements
- Python 3.x
- `os.path`: For interacting with the file system, particularly for file operations.
- `socket`: Essential for creating and managing network connections using the UDP protocol.
- `zlib.crc32`: Utilized for generating checksums to ensure data integrity during communication.

Ensure these libraries are available in your Python environment to run the UDP Communicator effectively.

## Usage
1. **Initial Setup**: Launch the application and select your role (sender or receiver). Input the necessary network information, including the IP address and port number.
2. **Communication Session**: As a sender, you can send text messages, files, or images to the receiver. As a receiver, you will receive these data types from the sender.
3. **Role Switching**: At any point, either participant can initiate a role switch, allowing the sender to become the receiver and vice versa. This feature adds flexibility to the communication process.
4. **Session Termination**: When the communication is complete, or if you wish to end the session, follow the steps to safely terminate the connection.

---

For a more detailed description of the UDP Communicator's functionalities, setup, and usage, please refer to the accompanying documentation file `PKS_zadanie2_dokumentacia_klusak.pdf`.

---
