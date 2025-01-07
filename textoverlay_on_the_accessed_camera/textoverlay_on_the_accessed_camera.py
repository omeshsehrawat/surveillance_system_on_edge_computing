import gi
import configparser
import re

# Initialize GStreamer for multimedia processing
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class MultiCameraRTSPPlayer:
    """
    A class to dynamically stream and display RTSP camera feeds in a grid layout.
    """
    def __init__(self, cameras, rows, columns):
        """
        Initialize the MultiCameraRTSPPlayer.

        :param cameras: List of RTSP camera URLs.
        :param rows: Number of rows in the grid layout.
        :param columns: Number of columns in the grid layout.
        """
        # Initialize GStreamer
        Gst.init(None)

        self.rows = rows
        self.columns = columns
        self.cameras = cameras

        # Build the GStreamer pipeline
        pipeline_str = self.build_pipeline()
        print(f"Pipeline: {pipeline_str}")

        # Create the GStreamer pipeline from the pipeline string
        self.pipeline = Gst.parse_launch(pipeline_str)

        # Set up the GStreamer bus to listen for pipeline messages
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

    def build_pipeline(self):
        """
        Constructs the GStreamer pipeline string based on the cameras and grid layout.

        :return: GStreamer pipeline string.
        """
        sources = ""  # Holds source elements for all cameras
        sinks = ""    # Holds sink configuration for the grid layout

        # Calculate the total number of cameras based on the grid size
        camera_count = self.rows * self.columns

        for i in range(camera_count):
            if i >= len(self.cameras):  # Stop if the available cameras are less than needed
                break
            
            # Parse camera URL into username, password, and IP address
            camera_url = self.cameras[i]
            username, password, ip_address = self.parse_camera_url(camera_url)
            
            # Build individual camera source pipeline
            rtsp_url = f"rtsp://{username}:{password}@{ip_address}"
            sources += self.build_camera_source(rtsp_url, i, ip_address)
            
            # Calculate grid position for the current camera
            xpos = (i % self.columns) * 640  # Horizontal position
            ypos = (i // self.columns) * 360  # Vertical position

            # Define sink properties (position and size) for the current camera
            sinks += (
                f'sink_{i}::xpos={xpos} sink_{i}::ypos={ypos} '
                f'sink_{i}::width=640 sink_{i}::height=360 '
            )
        
        # Combine sources and sinks to create the full pipeline
        pipeline_str = f'{sources}nvcompositor name=comp {sinks}! nv3dsink'
        return pipeline_str

    def build_camera_source(self, rtsp_url, index, ip_address):
        """
        Builds the pipeline segment for a single camera source.

        :param rtsp_url: RTSP URL of the camera.
        :param index: Index of the camera in the grid.
        :param ip_address: IP address of the camera.
        :return: GStreamer pipeline string for the camera source.
        """
        return (f'rtspsrc location="{rtsp_url}" latency=200 ! '
                f'rtph265depay ! h265parse ! nvv4l2decoder ! nvvideoconvert ! '
                f'textoverlay text="Camera {index + 1} - {ip_address}" valignment=top halignment=left font-desc="Sans, 24" ! '
                f'nvvideoconvert ! comp.sink_{index} ')

    def parse_camera_url(self, url):
        """
        Parses an RTSP URL into username, password, and IP address.

        :param url: RTSP URL of the camera.
        :return: Tuple containing (username, password, ip_address).
        """
        # Regular expression to parse the RTSP URL
        pattern = r"rtsp://([^:]+):([^@]+)@([^\s/]+)"
        match = re.match(pattern, url)
        if match:
            username = match.group(1)
            password = match.group(2)
            ip_address = match.group(3)
            return username, password, ip_address
        else:
            raise ValueError(f"Invalid camera URL format: {url}")

    def on_message(self, bus, message):
        """
        Handles GStreamer bus messages, such as errors and end-of-stream events.

        :param bus: The GStreamer bus.
        :param message: Message received from the bus.
        """
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            # Handle End-of-Stream (EOS) event
            print("End-of-stream (EOS) received. Shutting down...")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()
        elif msg_type == Gst.MessageType.ERROR:
            # Handle error messages
            err, debug_info = message.parse_error()
            print(f"Error: {err}, Debug info: {debug_info}")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()

    def start(self):
        """
        Starts the GStreamer pipeline and runs the GLib main loop.
        """
        # Set pipeline to PLAYING state
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Pipeline started, playing the RTSP streams...")
        
        # Start GLib main loop to keep the application running
        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            # Handle Ctrl+C interruption gracefully
            print("\nKeyboard interrupt received, stopping the pipeline...")
            self.quit_main_loop()

    def quit_main_loop(self):
        """
        Stops the GLib main loop and resets the GStreamer pipeline to NULL state.
        """
        if hasattr(self, 'loop'):
            self.loop.quit()  # Quit the GLib main loop
        self.pipeline.set_state(Gst.State.NULL)  # Reset the pipeline
        print("Pipeline stopped and GLib main loop exited.")

def read_config(file_path):
    """
    Reads camera URLs and grid configuration from the config.ini file.

    :param file_path: Path to the config.ini file.
    :return: Tuple containing (camera URLs, number of rows, number of columns).
    """
    config = configparser.ConfigParser()
    cameras = []
    rows = 0
    columns = 0

    try:
        # Read the configuration file
        config.read(file_path)
        
        # Extract camera URLs from the [resources] section
        for key in config['resources']:
            cameras.append(config['resources'][key])
        
        # Extract grid configuration from the [grid] section
        rows = int(config['grid'].get('rows', 1))  # Default to 1 row
        columns = int(config['grid'].get('columns', 1))  # Default to 1 column
    
    except Exception as e:
        print(f"Error reading config file: {e}")
    
    return cameras, rows, columns

if __name__ == "__main__":
    """
    Main entry point of the program. Reads camera details and grid configuration
    from a config.ini file and starts streaming RTSP feeds in a grid layout.
    """
    # Path to the config.ini file
    config_file_path = 'config.ini'
    
    # Read cameras and grid configuration
    cameras, rows, columns = read_config(config_file_path)
    
    if not cameras:
        print("No cameras found in the config.ini file.")
    else:
        print(f"Starting stream for {len(cameras)} cameras in a {rows}x{columns} grid...")
        
        # Create and start the MultiCameraRTSPPlayer instance
        player = MultiCameraRTSPPlayer(cameras, rows, columns)
        player.start()
