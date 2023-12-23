#!/usr/bin/env python3

import select

# Path to the file
file_path = 'test/data'

# Open the file in non-blocking read mode
with open(file_path, 'r') as file:
    fd = file.fileno()

    # Create a poll object
    poll = select.poll()

    # Register the file descriptor with the poll object
    poll.register(fd, select.POLLIN)

    # Continuously monitor the file for new data
    while True:
        # Timeout of 1000 milliseconds
        events = poll.poll(1000)
        for fileno, event in events:
            if fileno == fd and event & select.POLLIN:
                print(file.read(8))
