#!/bin/bash

# --- Configuration ---
# Set the name of the Docker image to run
CONTAINER='starfish'

# Set the path to the Xauthority file for authentication
XAUTH_FILE=~/.Xauthority


# --- Preparation ---
# Ensure the .Xauthority file exists on the host.
# This prevents Docker from creating an empty directory if the file is missing.
echo "Ensuring authentication file exists at ${XAUTH_FILE}..."
touch "${XAUTH_FILE}"


# --- Run the Container ---
echo "Starting container '${CONTAINER}' using the host's network..."
docker run -ti --rm \
    --network=host \
    -e _JAVA_OPTIONS='-Dawt.useSystemAAFontSettings=lcd -Dswing.defaultlaf=com.sun.java.swing.plaf.gtk.GTKLookAndFeel' \
    -e DISPLAY=$DISPLAY \
    -e XAUTHORITY=/root/.Xauthority \
    -v "${XAUTH_FILE}":/root/.Xauthority:ro \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /usr/share/fonts:/usr/share/fonts:ro \
    "${CONTAINER}"

echo "Container exited."
