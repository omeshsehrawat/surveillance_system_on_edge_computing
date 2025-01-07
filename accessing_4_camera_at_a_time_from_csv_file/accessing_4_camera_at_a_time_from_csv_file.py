import gi
import csv

# Import GStreamer bindings for Python
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class MultiCameraRTSPPlayer:
    """
    A class to handle RTSP streaming for multiple cameras using GStreamer.
    The class creates a 2x2 grid of video streams from 4 RTSP cameras.
    """
    def __init__(self, cameras):
        """
        Initialize the MultiCameraRTSPPlayer with camera details and set up the GStreamer pipeline.

        :param cameras: List of tuples containing (username, password, ip_address) for 4 cameras.
        """
        # Initialize GStreamer
        Gst.init(None)

        # Build the GStreamer pipeline for multiple cameras
        pipeline_str = self.build_pipeline(cameras)
        
        # Print the constructed pipeline string for debugging purposes
        print(f"Pipeline: {pipeline_str}")

        # Create the GStreamer pipeline
        self.pipeline = Gst.parse_launch(pipeline_str)

        # Set up the GStreamer bus to listen for messages from the pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

    def build_pipeline(self, cameras):
        """
        Build the GStreamer pipeline string to display multiple RTSP streams in a 2x2 grid.

        :param cameras: List of tuples containing (username, password, ip_address) for 4 cameras.
        :return: GStreamer pipeline string.
        """
        sources = ""  # Holds RTSP sources
        sinks = ""    # Holds compositor sink configurations
        
        # Loop through each camera and construct the source and sink elements
        for i, (username, password, ip_address) in enumerate(cameras):
            # Construct RTSP source URL
            rtsp_url = f"rtsp://{username}:{password}@{ip_address}"
            
            # Add RTSP source to the pipeline
            sources += f'rtspsrc location="{rtsp_url}" latency=200 ! rtph265depay ! h265parse ! nvv4l2decoder ! videoconvert ! comp.sink_{i} '
            
            # Calculate position for the 2x2 grid
            xpos = (i % 2) * 640  # Horizontal position: 0 or 640
            ypos = (i // 2) * 360  # Vertical position: 0 or 360
            
            # Configure compositor sink positions
            sinks += f'sink_{i}::xpos={xpos} sink_{i}::ypos={ypos} sink_{i}::width=640 sink_{i}::height=360 '
        
        # Combine sources and sinks to create the complete pipeline
        pipeline_str = f'{sources}nvcompositor name=comp {sinks}! nv3dsink'
        return pipeline_str

    def on_message(self, bus, message):
        """
        Handle messages from the GStreamer bus, such as errors and end-of-stream events.

        :param bus: The GStreamer bus
        :param message: The message received from the bus
        """
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            # Handle end-of-stream (EOS) message
            print("End-of-stream (EOS) received. Shutting down...")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()
        elif msg_type == Gst.MessageType.ERROR:
            # Handle pipeline errors
            err, debug_info = message.parse_error()
            print(f"Error: {err}, Debug info: {debug_info}")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()

    def start(self):
        """
        Start the GStreamer pipeline and enter the GLib main loop to keep the application running.
        """
        # Set the pipeline to the PLAYING state
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Pipeline started, playing the RTSP streams...")
        
        # Start the GLib main loop to keep the application running
        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C interruption
            print("\nKeyboard interrupt received, stopping the pipeline...")
            self.quit_main_loop()

    def quit_main_loop(self):
        """
        Stop the GLib main loop and reset the GStreamer pipeline to NULL state.
        """
        if hasattr(self, 'loop'):
            self.loop.quit()  # Quit the GLib main loop
        self.pipeline.set_state(Gst.State.NULL)  # Stop the GStreamer pipeline
        print("Pipeline stopped and GLib main loop exited.")

def read_camera_from_csv(file_path):
    """
    Reads camera details (username, password, IP address) from a CSV file.

    :param file_path: Path to the CSV file.
    :return: List of tuples with camera details.
    """
    cameras = []
    try:
        # Open the CSV file
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            # Read each row and extract camera details
            for row in reader:
                username = row['username']
                password = row['password']
                ip_address = row['ip_address']
                cameras.append((username, password, ip_address))
    except Exception as e:
        # Handle errors in reading the CSV file
        print(f"Error reading CSV file: {e}")
    return cameras

if __name__ == "__main__":
    """
    Main function to read camera details from a CSV file and start RTSP streaming
    for 4 cameras displayed in a 2x2 grid.
    """
    # Path to the CSV file containing camera details
    csv_file_path = 'cameras.csv'
    
    # Read the list of cameras from the CSV file
    cameras = read_camera_from_csv(csv_file_path)
    
    if not cameras:
        # If no cameras are found, print an error message
        print("No cameras found in the CSV file.")
    else:
        # Ensure we have exactly 4 cameras
        if len(cameras) != 4:
            print("Error: The CSV file must contain exactly 4 cameras.")
        else:
            # Create a MultiCameraRTSPPlayer instance to handle 4 cameras
            print("\nStarting stream for 4 cameras...")
            player = MultiCameraRTSPPlayer(cameras)
            player.start()
