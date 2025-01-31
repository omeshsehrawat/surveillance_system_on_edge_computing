------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
README: Multi-Camera RTSP Streaming with GStreamer Using Config File
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Overview :->

This Python program streams RTSP feeds from multiple cameras simultaneously and displays them in a customizable grid layout using GStreamer. Camera details (username, password, IP address) are read from a configuration file, and the program ensures NVIDIA hardware-accelerated 
decoding for optimal performance.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Features:->

    1. Multi-Camera RTSP Streaming:
        - Streams RTSP feeds concurrently.
        - Configurable grid layout for displaying streams.

    2. Config File Integration:
        - Reads camera details (username, password, IP address) and grid configuration from a `config.ini` file.

    3. Error Handling:
        - Detects and handles GStreamer errors, such as invalid streams or connection issues.
        - Ensures the program stops gracefully on end-of-stream (EOS) events or interruptions.

    4. Efficient Hardware Acceleration:
        - Utilizes NVIDIA hardware for decoding and rendering.
        
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Usage Instructions:->

Prepare the Configuration File: Create a `config.ini` file in the same directory. 
The file should have the following format:->

[resources]
camera1 = rtsp://admin:pass123@192.168.1.10
camera2 = rtsp://admin:pass123@192.168.1.20
camera3 = rtsp://admin:pass123@192.168.1.30
camera4 = rtsp://admin:pass123@192.168.1.40

[grid]
rows = 2
columns = 2


    -> [resources]: RTSP camera URLs.
    -> [grid]: Grid configuration for rows and columns.

Run the Program:->

Execute the script:
	$python3 script_name.py

Stream Display:- The program will stream feeds from all cameras in the specified grid layout. 
		- Each stream is placed in a corresponding quadrant of the grid.
Stop the Program: - Press Ctrl+C to terminate the program gracefully.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Code Structure:->

    1. MultiCameraRTSPPlayer Class: - Handles RTSP streaming for cameras. - Constructs a GStreamer pipeline to display the streams in a grid.

    2. build_pipeline Method: - Dynamically builds the GStreamer pipeline based on the camera details. - Configures a grid layout using the nvcompositor element.

    3. on_message Method: - Handles GStreamer bus messages such as errors or end-of-stream events.

    4. parse_camera_url Method: - Parses the RTSP URLs into username, password, and IP address.

    5. read_config Function: - Reads camera details and grid configuration from a config.ini file.

    6. Main Function: - Reads the camera details and grid configuration from the config.ini file. - Starts the RTSP streams using MultiCameraRTSPPlayer.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Customizations:->

    1. Adjust the Number of Cameras: - Modify the grid configuration in the config.ini file to change the number of rows and columns.

    2. Change Video Decoding Format: - The current pipeline supports H.265 streams. 
    				       - To support other formats (e.g., H.264), modify the pipeline in the build_pipeline method:->
     							rtph264depay ! h264parse ! nvv4l2decoder

    3. Grid Layout Customization: - Adjust the positioning of streams in the build_pipeline method by modifying the xpos, ypos, width, and height parameters.

    4. Error Logging: - Extend the on_message method to log errors to a file for debugging.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

GStreamer Pipeline:->

Pipeline Elements:

    1. rtspsrc: Reads RTSP streams from the camera.
    2. rtph265depay: Depayloads H.265 RTP packets.
    3. h265parse: Parses the H.265 video stream.
    4. nvv4l2decoder: Decodes the video using NVIDIA hardware acceleration.
    5. videoconvert: Converts video formats for compatibility.
    6. nvcompositor: Composites multiple video streams into a single output.
    7. nv3dsink: Displays the video on the screen.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Error Handling:->

1. Configuration File Not Found: If the config.ini file is missing or unreadable, the program outputs:
     $ Error reading config file: [Error details]

2. RTSP Stream Issues:
    If an RTSP stream fails (e.g., invalid credentials or IP address), an error message is displayed:
    	$ Error: [Error message], Debug info: [Debug details]

3. End-of-Stream (EOS):
    If a camera stream ends, the program stops gracefully:
    	$ End-of-stream (EOS) received. Shutting down...

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Example Output :->

Starting stream for 4 cameras... Pipeline: rtspsrc location="rtsp://admin:pass123@192.168.1.10" latency=200 ! rtph265depay ! h265parse ! nvv4l2decoder ! videoconvert ! comp.sink_0 ... Pipeline started, playing the RTSP streams...
Error: Connection refused, Debug info: [RTSP debug details] Pipeline stopped and GLib main loop exited.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


