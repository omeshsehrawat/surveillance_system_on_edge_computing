import gi
import csv

# Import GStreamer bindings for Python
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class RTSPPlayer:
    """
    A class to handle RTSP streaming using GStreamer.
    """
    def __init__(self, username, password, ip_address):
        """
        Initialize the RTSP player with camera credentials and IP address.

        :param username: Username for RTSP authentication
        :param password: Password for RTSP authentication
        :param ip_address: IP address of the RTSP camera
        """
        # Initialize GStreamer
        Gst.init(None)

        # Construct the GStreamer pipeline string using the camera details
        pipeline_str = (
            f"rtspsrc location=rtsp://{username}:{password}@{ip_address} ! "
            f"rtph265depay ! h265parse ! nvv4l2decoder ! videoconvert ! nv3dsink"
        )
        
        # Print the pipeline for debugging purposes
        print(f"Pipeline: {pipeline_str}")

        # Create the GStreamer pipeline
        self.pipeline = Gst.parse_launch(pipeline_str)

        # Set up the bus to listen for messages from the GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        """
        Handle messages from the GStreamer bus, such as errors and end-of-stream events.

        :param bus: The GStreamer bus
        :param message: The message received from the bus
        """
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            # End-of-stream received
            print("End-of-stream (EOS) received. Shutting down...")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()
        elif msg_type == Gst.MessageType.ERROR:
            # Handle errors in the pipeline
            err, debug_info = message.parse_error()
            print(f"Error: {err}, Debug info: {debug_info}")
            self.pipeline.set_state(Gst.State.NULL)
            self.quit_main_loop()

    def start(self):
        """
        Start the GStreamer pipeline and enter the GLib main loop to keep the application running.
        """
        # Set the pipeline to PLAYING state
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Pipeline started, playing the RTSP stream...")
        
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
    Reads the camera details from a CSV file and returns a list of tuples containing
    the username, password, and IP address for each camera.

    :param file_path: Path to the CSV file
    :return: List of tuples with camera details
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
    for each camera listed in the file.
    """
    # Path to the CSV file containing camera details
    csv_file_path = 'cameras.csv'
    
    # Read the list of cameras from the CSV file
    cameras = read_camera_from_csv(csv_file_path)
    
    if not cameras:
        # If no cameras are found, print an error message
        print("No cameras found in the CSV file.")
    else:
        # Loop through each camera and create a player for it
        for i, (username, password, ip_address) in enumerate(cameras, start=1):
            print(f"\nStarting stream for Camera {i} ({ip_address})...")
            player = RTSPPlayer(username, password, ip_address)
            player.start()
