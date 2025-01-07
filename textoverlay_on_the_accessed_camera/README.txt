------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
README: Multi-Camera RTSP Player with GStreamer and Apply TextOverlay
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Overview :->

The MultiCameraRTSPPlayer application streams and displays multiple RTSP camera feeds in a dynamic grid layout using GStreamer. It provides a flexible way to monitor multiple camera feeds on a single screen. Each feed includes an overlay showing its camera number and IP address.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
############################################################################################################################################################################################
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Features:->

   1. Dynamic RTSP Stream Handling: Supports multiple camera feeds with configurable RTSP URLs.
   
   2. Grid Layout: Automatically arranges streams in a grid layout based on user-defined rows and columns.
   
   3. Configurable via INI File: Camera URLs and grid dimensions are easily configurable in a config.ini file.
   
   4. Error Handling: Displays error messages for invalid RTSP URLs or connection issues.
   
   5. GLib Main Loop: Keeps the application running for continuous streaming.
   
   6. Text Overlay: Displays camera information on the video feed.
    
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
############################################################################################################################################################################################
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Prerequisites:->

    1. Python 3.x
    2. GStreamer: Installed with necessary plugins for RTSP and video rendering.
    3. Required Python Libraries:
        	gi (GObject Introspection)
        	configparser
        	re

Configuration File: 

Create a config.ini file in the same directory as the script with the following structure:

[resources]
camera1 = rtsp://username:password@192.168.1.101
camera2 = rtsp://username:password@192.168.1.102

[grid]
rows = 2
columns = 2

    1. Under [resources], add your RTSP camera URLs.
    2. Under [grid], define the number of rows and columns for the grid layout.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
############################################################################################################################################################################################
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Run the Script: 

Execute the script from the command line:
    $ python multi_camera_rtsp_player.py

How It Works
    1. Configuration:
        The read_config function reads the RTSP URLs and grid dimensions from config.ini.

    2. Dynamic Pipeline Creation:
        The GStreamer pipeline is dynamically built using the RTSP URLs and arranged in a grid layout.

    3. Streaming:
        Each RTSP stream is processed through GStreamer plugins for decoding and rendering.
        Streams are displayed in the grid with text overlays indicating the camera number and IP address.

    4. Error Handling:
        Errors such as invalid URLs or connection issues are logged, and the pipeline gracefully shuts down.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
############################################################################################################################################################################################
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Key Classes and Functions:->

    1. MultiCameraRTSPPlayer:
           Main class that handles streaming and grid layout.
    2. build_pipeline:
           Dynamically constructs the GStreamer pipeline for multiple RTSP feeds.
    3. parse_camera_url:
           Parses RTSP URLs into username, password, and IP address.
    4. read_config:
           Reads the config.ini file to retrieve camera URLs and grid dimensions.
       
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Configuration Options:

1. Camera Resources:
     Add RTSP URLs under the [resources] section in the config.ini.
     Example:

    	[resources]
    	camera1 = rtsp://admin:password@192.168.1.101

2. Grid Dimensions:

    Set the number of rows and columns in the [grid] section.
    Example:

	[grid]
	rows = 2
	columns = 3

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################################################################################################################################################################
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
