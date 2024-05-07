#!/usr/bin/env python3

import sys
import json


def process_message(message):
    # Open a text file in append mode
    with open("messages_log.txt", "a") as file:
        # Write the message to the file, converting it to a string if necessary
        file.write(str(message) + "\n")  # Add a newline character to separate entries

    if message:
        # Fetch emails and prepare the response
        response = {"emails": ["email1", "email2", "email3"]}
        return response
    else:
        return {"error": "Invalid action"}


while True:
    message_length_bytes = sys.stdin.buffer.read(4)
    if len(message_length_bytes) == 0:
        break
    message_length = int.from_bytes(message_length_bytes, byteorder="little")
    message_data = sys.stdin.buffer.read(message_length).decode("utf-8")
    # message = json.loads(message_data)

    response = process_message(message_data)

    response_data = json.dumps(response).encode("utf-8")
    response_length_bytes = len(response_data).to_bytes(4, byteorder="little")
    sys.stdout.buffer.write(response_length_bytes)
    sys.stdout.buffer.write(response_data)
    sys.stdout.buffer.flush()
