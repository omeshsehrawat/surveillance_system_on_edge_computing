#!/usr/bin/env python3

import gi
import configparser
import re
import sys

gi.require_version('Gst', '1.0')
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GLib, GstRtspServer

class MultiCameraRTSPPlayer:
    """
    This class handles the functionality to:
    - Access multiple RTSP cameras.
    - Composite the feeds into a grid layout.
    - Display the composited video locally.
    - Re-stream the composited video over RTSP.
    """

    def __init__(
        self,
        cameras,
        rows,
        columns,
        rtsp_host,
        rtsp_port,
        mount_point,
        udp_port,
        tile_width,
        tile_height,
        encoding_bitrate
    ):
        # Initialize GStreamer
        Gst.init(None)

        # Store configuration parameters
        self.rows = rows
        self.columns = columns
        self.cameras = cameras

        # Assign the streaming configuration values
        self.rtsp_host = rtsp_host
        self.rtsp_port = rtsp_port
        self.mount_point = mount_point
        self.udp_port = udp_port
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.encoding_bitrate = encoding_bitrate

        # Build the GStreamer pipeline description string
        self.pipeline_str = self.build_pipeline()
        print(f"[DEBUG] GStreamer pipeline:\n{self.pipeline_str}\n")

        # Parse and create the GStreamer pipeline
        self.pipeline = Gst.parse_launch(self.pipeline_str)
        if not self.pipeline:
            sys.stderr.write("Failed to create pipeline from the string.\n")
            sys.exit(1)

        # Set up the GStreamer bus to listen for messages (errors, EOS, etc.)
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

        # Set up the internal RTSP server
        self.setup_rtsp_server()

    def build_pipeline(self):
        """
        Constructs a GStreamer pipeline string to:
        - Create N camera sources (RTSP streams).
        - Composite them into a grid using nvcompositor.
        - Tee the output for local display and RTSP re-streaming.
        
        Returns:
            str: The GStreamer pipeline string.
        """

        sources = ""  # Holds the source pipeline for each camera
        sinks_positions = ""  # Specifies the compositor sink positions for each camera

        # Determine the total number of cameras to fit in the grid
        camera_count = self.rows * self.columns

        for i in range(camera_count):
            if i >= len(self.cameras):
                break

            # Parse camera info (username, password, and IP address)
            camera_url = self.cameras[i]
            username, password, ip_address = self.parse_camera_url(camera_url)
            rtsp_url = f"rtsp://{username}:{password}@{ip_address}"

            # Build the pipeline segment for this camera
            sources += (
                f'rtspsrc location="{rtsp_url}" latency=50 ! '
                f'rtph265depay ! h265parse ! nvv4l2decoder ! nvvideoconvert ! '
                f'textoverlay text="Camera {i+1} - {ip_address}" '
                f'valignment=top halignment=left font-desc="Sans, 24" ! '
                f'nvvideoconvert ! comp.sink_{i} '
            )

            # Define the grid position (x, y, width, height) for this camera
            xpos = (i % self.columns) * self.tile_width
            ypos = (i // self.columns) * self.tile_height
            sinks_positions += (
                f'sink_{i}::xpos={xpos} '
                f'sink_{i}::ypos={ypos} '
                f'sink_{i}::width={self.tile_width} '
                f'sink_{i}::height={self.tile_height} '
            )

        # Combine sources and sinks into the full pipeline string
        pipeline_str = f"""
            {sources}
            nvcompositor name=comp {sinks_positions} !
            nvvideoconvert ! tee name=t

            t. ! queue !
                 nvvideoconvert !
                 nv3dsink

            t. ! queue max-size-buffers=1 leaky=downstream !
                 nvvideoconvert !
                 video/x-raw(memory:NVMM), format=NV12 !
                 nvv4l2h265enc bitrate={self.encoding_bitrate} iframeinterval=30 insert-sps-pps=1 preset-level=1 !
                 rtph265pay !
                 udpsink host=127.0.0.1 port={self.udp_port} sync=false async=false
        """

        # Remove excess whitespace and newlines for better readability
        pipeline_str = " ".join(pipeline_str.split())
        return pipeline_str

    def parse_camera_url(self, url):
        """
        Parses an RTSP URL to extract the username, password, and IP address.

        Args:
            url (str): RTSP URL of the camera.

        Returns:
            tuple: (username, password, ip_address)
        """
        pattern = r"rtsp://([^:]+):([^@]+)@([^\s/]+)"
        match = re.match(pattern, url)
        if match:
            username = match.group(1)
            password = match.group(2)
            ip_address = match.group(3)
            return username, password, ip_address
        else:
            raise ValueError(f"Invalid camera URL format: {url}")

    def setup_rtsp_server(self):
        """
        Sets up an internal RTSP server to publish the composited video stream.
        """
        self.server = GstRtspServer.RTSPServer.new()
        self.server.set_address(self.rtsp_host)
        self.server.set_service(str(self.rtsp_port))
        self.server.attach(None)

        # Configure the RTSP media factory
        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(
            f"( udpsrc name=pay0 port={self.udp_port} buffer-size=524288 "
            f"caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=H265, payload=96\" )"
        )
        factory.set_shared(True)
        factory.set_eos_shutdown(False)  # Prevent shutdown on client disconnection

        # Add the factory to the RTSP server's mount points
        mount_points = self.server.get_mount_points()
        mount_points.add_factory(self.mount_point, factory)

        print(f"[INFO] RTSP server launched at rtsp://{self.rtsp_host}:{self.rtsp_port}{self.mount_point}")

    def on_message(self, bus, message):
        """
        Handles GStreamer bus messages for error and end-of-stream events.

        Args:
            bus (Gst.Bus): The GStreamer bus.
            message (Gst.Message): The received message.
        """
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            print("[INFO] End-of-stream (EOS) received. Shutting down...")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()
        elif msg_type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"[ERROR] {err}, Debug info: {debug_info}")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()

    def start(self):
        """
        Starts the GStreamer pipeline and runs the GLib main loop.
        """
        self.pipeline.set_state(Gst.State.PLAYING)
        print("[INFO] Pipeline started. Press Ctrl+C to stop...\n")

        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Stopping...")
            self.quit_main_loop()

    def quit_main_loop(self):
        """
        Stops the GLib main loop and resets the pipeline state.
        """
        if hasattr(self, 'loop'):
            self.loop.quit()
        self.pipeline.set_state(Gst.State.NULL)
        print("[INFO] Pipeline stopped and GLib main loop exited.")


def read_config(file_path):
    """
    Reads camera URLs, grid configuration, and streaming parameters from a config.ini file.

    Args:
        file_path (str): Path to the config file.

    Returns:
        tuple: Configuration parameters needed for the player.
    """
    config = configparser.ConfigParser()
    cameras = []
    rows = 0
    columns = 0

    # Default values for streaming settings if not provided in the config
    rtsp_host = "127.0.0.1"
    rtsp_port = 8554
    mount_point = "/multicam"
    udp_port = 5400
    tile_width = 320
    tile_height = 180
    encoding_bitrate = 1000000

    try:
        config.read(file_path)

        # -- [resources] section (camera URLs) --
        if 'resources' in config:
            for key in config['resources']:
                cameras.append(config['resources'][key])

        # -- [grid] section (rows/columns) --
        if 'grid' in config:
            rows = int(config['grid'].get('rows', 1))
            columns = int(config['grid'].get('columns', 1))

        # -- [stream] section (network & pipeline params) --
        if 'stream' in config:
            rtsp_host = config['stream'].get('rtsp_host', rtsp_host)
            rtsp_port = config['stream'].getint('rtsp_port', rtsp_port)
            mount_point = config['stream'].get('mount_point', mount_point)
            udp_port = config['stream'].getint('udp_port', udp_port)
            tile_width = config['stream'].getint('tile_width', tile_width)
            tile_height = config['stream'].getint('tile_height', tile_height)
            encoding_bitrate = config['stream'].getint('encoding_bitrate', encoding_bitrate)

    except Exception as e:
        print(f"[ERROR] Error reading config file: {e}")

    # Return everything needed for the player
    return (
        cameras,
        rows,
        columns,
        rtsp_host,
        rtsp_port,
        mount_point,
        udp_port,
        tile_width,
        tile_height,
        encoding_bitrate
    )


if __name__ == "__main__":
    # Path to the configuration file
    config_file_path = "config.ini"

    # Read configuration from the config file
    (
        cameras,
        rows,
        columns,
        rtsp_host,
        rtsp_port,
        mount_point,
        udp_port,
        tile_width,
        tile_height,
        encoding_bitrate
    ) = read_config(config_file_path)

    if not cameras:
        print("[WARN] No cameras found in the config.ini file.")
    else:
        print(f"[INFO] Starting composited stream for {len(cameras)} camera(s) in a {rows}x{columns} grid...")
        player = MultiCameraRTSPPlayer(
            cameras,
            rows,
            columns,
            rtsp_host,
            rtsp_port,
            mount_point,
            udp_port,
            tile_width,
            tile_height,
            encoding_bitrate
        )
        player.start()
