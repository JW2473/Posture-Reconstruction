# Posture-Reconstruction
## oriTrakHAR-master
Yuhui's project
## python-code
Python code translated from oriTrakHAR-master:
#### *left and right Dict_yzx*: 
Dictionary in json mapping wrist euler to elbow euler
#### *processData.processRow(files, timeSeries)*: 
Read quaternions from files, interpolated at times specified by timeSeries
#### *processStream.processRow(files, timeSeries)*: 
Read quaternions from named pipes, interpolated at times specified by timeSeries
#### *visualization*:
Visualize quaternions loaded from either files or pipes, determined by the source of processRow
#### *transformations*:
Utility functions for handling quaternions
## data_collection:
Receive data from WiFi modules and save as csv files
## hotspot_to_client:
Switch rpi between WiFi hotspot and client; Need a reboot to make those changes
