# Surveillance System on Edge Computing

This repository contains various Python-based implementations and GStreamer pipelines for creating surveillance systems on edge computing devices. These projects are designed to efficiently manage and process camera streams, providing features like dynamic layouts, text overlays, and RTSP re-streaming.

## Folder Descriptions

### 1. **accessing_4_camera_at_a_time_from_csv_file**
   - **Description**: This project demonstrates how to access and display streams from four cameras simultaneously. The camera details (like IP addresses) are read from a CSV file.

---

### 2. **camera_streaming_with_dynamic_grid_layout**
   - **Description**: A dynamic grid layout for displaying multiple camera streams. The layout adjusts based on the user input grid size.

---

### 3. **camera_streaming_with_dynamic_grid_layout_using_config_file**
   - **Description**: Similar to the dynamic grid layout project, but the configuration (e.g., camera details and layout) is read from a configuration file.

---

### 4. **re-stream_of_rtsp_camera_using_GstRtspServer**
   - **Description**: This project re-streams RTSP camera feeds using the GstRtspServer module in GStreamer. It is useful for redistributing streams to other devices or applications.

---

### 5. **sequentially_access_camera_from_csv_file**
   - **Description**: Accesses and displays camera streams sequentially, one at a time, based on the order specified in a CSV file.

---

### 6. **textoverlay_on_the_accessed_camera**
   - **Description**: Adds text overlays to camera streams, such as timestamps, camera names, or custom messages, using GStreamer elements.

---

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/surveillance_system_on_edge_computing.git
