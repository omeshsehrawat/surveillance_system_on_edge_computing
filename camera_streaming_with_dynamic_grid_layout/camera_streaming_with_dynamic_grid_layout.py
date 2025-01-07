import gi
import csv

# Ensure the correct version of GStreamer is used
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class MultiCameraRTSPPlayer:
    """
    A class to handle multiple RTSP camera streams and display them in a grid layout using GStreamer.
    """
    def __init__(self, cameras, rows, columns):
        """
        Initialize the MultiCameraRTSPPlayer.

        :param cameras: List of tuples containing (username, password, ip_address) for each camera.
        :param rows: Number of rows in the grid layout.
        :param columns: Number of columns in the grid layout.
        """
        # Initialize GStreamer
        Gst.init(None)

        self.rows = rows
        self.columns = columns
        self.cameras = cameras

        # Build the GStreamer pipeline string based on the number of cameras and grid layout
        pipeline_str = self.build_pipeline()
        print(f"Pipeline: {pipeline_str}")

        # Create the GStreamer pipeline from the pipeline string
        self.pipeline = Gst.parse_launch(pipeline_str)

        # Set up the bus to listen for messages from the pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

    def build_pipeline(self):
        """
        Constructs the GStreamer pipeline string based on the provided cameras and grid layout.

        :return: A string representing the GStreamer pipeline.
        """
        sources = ""  # String to hold all source elements
        sinks = ""    # String to hold all sink elements

        # Calculate the maximum number of cameras based on the grid size (rows * columns)
        camera_count = self.rows * self.columns

        for i in range(camera_count):
            if i >= len(self.cameras):
                # Stop adding sources if there are not enough cameras
                break

            # Extract camera credentials and IP address
            username, password, ip_address = self.cameras[i]
            rtsp_url = f"rtsp://{username}:{password}@{ip_address}"

            # Append the RTSP source pipeline for each camera
            sources += (
                f'rtspsrc location="{rtsp_url}" latency=200 ! '
                f'rtph265depay ! h265parse ! nvv4l2decoder ! videoconvert ! '
                f'comp.sink_{i} '
            )

            # Calculate the position of each video in the grid
            xpos = (i % self.columns) * 640  # Horizontal position based on column
            ypos = (i // self.columns) * 360  # Vertical position based on row

            # Define sink properties for positioning and sizing
            sinks += (
                f'sink_{i}::xpos={xpos} sink_{i}::ypos={ypos} '
                f'sink_{i}::width=640 sink_{i}::height=360 '
            )

        # Complete the pipeline by adding a compositor and the final video sink
        pipeline_str = f'{sources}nvcompositor name=comp {sinks}! nv3dsink'
        return pipeline_str

    def on_message(self, bus, message):
        """
        Handle messages from the GStreamer bus.

        :param bus: The GStreamer bus.
        :param message: The message from the bus.
        """
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            # Handle End-of-Stream message
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
        Start the GStreamer pipeline and the GLib main loop to begin streaming.
        """
        # Set the pipeline to the PLAYING state to start processing
        self.pipeline.set_state(Gst.State.PLAYING)
        print("Pipeline started, playing the RTSP streams...")

        # Initialize and run the GLib main loop to keep the application active
        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            # Handle user interruption (e.g., Ctrl+C)
            print("\nKeyboard interrupt received, stopping the pipeline...")
            self.quit_main_loop()

    def quit_main_loop(self):
        """
        Stop the GLib main loop and set the GStreamer pipeline to NULL state.
        """
        if hasattr(self, 'loop'):
            self.loop.quit()
        self.pipeline.set_state(Gst.State.NULL)
        print("Pipeline stopped and GLib main loop exited.")

def read_camera_from_csv(file_path):
    """
    Reads camera details from a CSV file.

    :param file_path: Path to the CSV file containing camera details.
    :return: A list of tuples with (username, password, ip_address) for each camera.
    """
    cameras = []
    try:
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                username = row['username']
                password = row['password']
                ip_address = row['ip_address']
                cameras.append((username, password, ip_address))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return cameras

if __name__ == "__main__":
    # Path to the CSV file containing camera details
    csv_file_path = 'cameras.csv'

    # Read the list of cameras from the CSV file
    cameras = read_camera_from_csv(csv_file_path)

    if not cameras:
        print("No cameras found in the CSV file.")
    else:
        # Prompt the user to input the number of rows and columns for the grid layout
        try:
            rows = int(input("Enter the number of rows (n): "))
            columns = int(input("Enter the number of columns (m): "))
        except ValueError:
            print("Invalid input for rows or columns. Please enter integers.")
            exit(1)

        # Calculate the total number of cameras needed based on grid size
        total_needed_cameras = rows * columns
        if total_needed_cameras > len(cameras):
            print(f"Warning: Only {len(cameras)} cameras available, but {total_needed_cameras} are needed.")

        # Inform the user about the streaming setup
        print(f"\nStarting stream for {total_needed_cameras} cameras in a {rows}x{columns} grid...")

        # Create an instance of MultiCameraRTSPPlayer and start streaming
        player = MultiCameraRTSPPlayer(cameras, rows, columns)
        player.start()
