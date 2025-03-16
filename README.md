# RepairKinectRecordings README:

## Problem Definition

Smart-Cup is a Python program we have built to record data from multiple sensors in the living lab. It saves Kinect V2 sensor recordings in mkv file format and predicted human pose results in csv format.   

After completing data collection there were 2 bugs found in Smart-Cup: 

1. Frame rate of the recordings were inconsistent. Kinect pose estimates were being generated in real-time. So after each frame was captured, execution was held up trying to estimate pose. If this took too long, it would miss the next incoming frame/s. 

2. When more than one pose was captured, duplicates of the same pose would be saved multiple times and we've lost the other poses 

It should be possible to run the Kinect Body Tracking SDK on the mkv recordings to recover the lost pose. However, since the mkv files are corrupted, the SDK wont process them. **Is it possible to repair the mkv files so the SDK  can process them?**


## Setup
1. Install Kinect SDK v1.4.1 from here: [Download Azure Kinect SDK 1.4.1 from Official Microsoft Download Center](https://www.microsoft.com/en-us/download/details.aspx?id=101454)
2. Install Azure Kinect Body Tracking SDK v1.1.2 from here: [Download Azure Kinect Body Tracking SDK 1.1.2 from Official Microsoft Download Center](https://www.microsoft.com/en-us/download/details.aspx?id=104221)
3. Clone this repository and install how?
4. Test successful installation of Kinect Body Tracking SDK by running: `k4abt_simple_3d_viewer.exe OFFLINE stereo_test.mkv`. The `k4abt_simple_3d_viewer.exe` executable can be found in C:\Program Files\Azure Kinect Body Tracking SDK\tools. The `stereo_test.mkv` can be found in the shared living lab oneDrive `backup_data\kinect_tests\clean_recordings`
5. Install ffmpeg from here: [Download FFmpeg](https://ffmpeg.org/download.html)
6. Unzip Azure-Kinect-Sensor-SDK-develop.zip (this is the source code for the Kinect SDK taken from [this repo](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/tree/develop) and you can analyze it to try and understand the expected structure of mkv recordings)



## Attempting kinect pose estimation on corrupt vs uncorrupt mkv

Uncorrupt mkv files can be found in `backup_data\kinect_tests\clean_recordings` and were captured using `k4arecorder.exe output.mkv`. Corrupt recordings were captured using SmartCup, all of the official living lab and walking aids mkv data is corrupt. I have been using `backup_data\kinect_tests\clean_recordings\python_recording.mkv` for testing. It is the same as `backup_data\LivingLabBackups\kinect\subject_02_Micky_Bacic\Session-2023-December-06 12-40-07-744169\kinect_camera_recording.mkv` and is the shortest kinect recording from the dataset.

Running `k4abt_simple_3d_viewer` on a corrupt recording `k4abt_simple_3d_viewer.exe OFFLINE python_recording.mkv` results in the following output:

```
[2025-03-17 08:08:57.122] [error] [t=18108] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\record\internal\matroska_read.cpp (214): parse_mkv(). Recording file does not contain any frames!
[2025-03-17 08:08:57.128] [error] [t=18108] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\record\sdk\playback.cpp (45): parse_mkv(context) returned failure in k4a_playback_open()
Failed to open recording: C:\Users\GSBME\OneDrive - UNSW\fall_detection\backup_data\kinect_tests\corrupt_recordings\python_recording.mkv
```


When we run `python pose_from_mkv.py` and set `video_filename` to the path of an uncorrupted mkv file, then the program outputs xyz coordinates of pose keypoints. If we set `video_filename` to a corrupted mkv file, then the output is: 

```
[2025-03-17 08:35:25.045] [error] [t=29624] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\record\internal\matroska_read.cpp (214): parse_mkv(). Recording file does not contain any frames!
[2025-03-17 08:35:25.045] [error] [t=29624] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\record\sdk\playback.cpp (45): parse_mkv(context) returned failure in k4a_playback_open()
Failed to open recording!
  File "C:\Users\GSBME\SmartCupStudy\smart-cup-works-csvfix\pose_from_mkv.py", line 27, in <module>
    playback = pykinect.start_playback(video_filename)
  File "C:\Users\GSBME\SmartCupStudy\smart-cup-works-csvfix\pykinect_azure\pykinect.py", line 66, in start_playback
    return Playback(filepath)
  File "C:\Users\GSBME\SmartCupStudy\smart-cup-works-csvfix\pykinect_azure\k4arecord\playback.py", line 18, in __init__
    self.open(filepath)
  File "C:\Users\GSBME\SmartCupStudy\smart-cup-works-csvfix\pykinect_azure\k4arecord\playback.py", line 26, in open
    _k4arecord.VERIFY(_k4arecord.k4a_playback_open(filepath.encode('utf-8'),self._handle),"Failed to open recording!")
  File "C:\Users\GSBME\SmartCupStudy\smart-cup-works-csvfix\pykinect_azure\k4arecord\_k4arecord.py", line 425, in VERIFY
    traceback.print_stack()
[2025-03-17 08:35:25.048] [error] [t=29624] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\include\k4ainternal/matroska_read.h (143): k4a_playback_t_get_context(). Invalid k4a_playback_t 0000000000000000
[2025-03-17 08:35:25.048] [error] [t=29624] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\record\sdk\playback.cpp (658): Invalid argument to k4a_playback_close(). playback_handle (0000000000000000) is not a valid handle of type k4a_playback_t
```

I've started writing `examplePlaybackBodyTracker.py` to show a playback of the pose on the depth/RGB stream, though there are some bugs which need fixing.



## Probing the mkv file

Probing the MKV File 

From the ffmpeg command: 

`ffprobe -v error -show_entries stream=index,codec_name,codec_type,width,height,pix_fmt,r_frame_rate -of default=noprint_wrappers=1 "stereo_test.mkv"`

The output was: 

    index=0 
        codec_name=mjpeg 
        codec_type=video 
        width=1280 
        height=720 
        pix_fmt=yuvj422p 
        r_frame_rate=15/1 
    index=1 
        codec_name=rawvideo 
        codec_type=video 
        width=320 
        height=288 
        pix_fmt=gray16be 
        r_frame_rate=15/1 
    index=2 
        codec_name=rawvideo 
        codec_type=video 
        width=320 
        height=288 
        pix_fmt=gray16be 
        r_frame_rate=15/1 
    index=3 
        codec_name=unknown 
        codec_type=attachment 
        r_frame_rate=0/0 

The output indicated that the mkv file has the following tracks: 

* Track 0: MJPEG video 
* Track 1: Raw video 
* Track 2: Raw video 
* Track 3: Unknown attachment 


An ffmpeg command used to test the extraction of track 1 gave more details about the meta data: 

`ffmpeg -i kinect_camera_recording.mkv -map 0:1 -c copy track1.raw`
 
Part of the output was: 

Metadata: 
```
    K4A_DEPTH_DELAY_NS: 0 

    K4A_WIRED_SYNC_MODE: STANDALONE 

    K4A_COLOR_FIRMWARE_VERSION: 1.6.110 

    K4A_DEPTH_FIRMWARE_VERSION: 1.6.79 

    K4A_DEVICE_SERIAL_NUMBER: 000248795012 

  Duration: N/A, start: 0.000000, bitrate: N/A 

  Stream #0:0(eng): Video: mjpeg (Baseline) (MJPG / 0x47504A4D), yuvj422p(pc, bt470bg/unknown/unknown), 1280x720, SAR 1:1 DAR 16:9, 15 fps, 15 tbr, 1k tbn (default) 

      Metadata: 

        title           : COLOR 

        K4A_COLOR_TRACK : 774811655673491700 

        K4A_COLOR_MODE  : MJPG_720P 

  Stream #0:1(eng): Video: rawvideo (b16g / 0x67363162), gray16be, 320x288, SAR 1:1 DAR 10:9, 15 fps, 15 tbr, 1k tbn (default) 

      Metadata: 

        title           : DEPTH 

        K4A_DEPTH_TRACK : 593252017626741290 

        K4A_DEPTH_MODE  : NFOV_2X2BINNED 

  Stream #0:2(eng): Video: rawvideo (b16g / 0x67363162), gray16be, 320x288, SAR 1:1 DAR 10:9, 15 fps, 15 tbr, 1k tbn (default) 

      Metadata: 

        title           : IR 

        K4A_IR_TRACK    : 718068090411469125 

        K4A_IR_MODE     : ACTIVE 

  Stream #0:3: Attachment: none 

      Metadata: 

        filename        : calibration.json 

        mimetype        : application/octet-stream 

        K4A_CALIBRATION_FILE: calibration.json 

Stream mapping: 

  Stream #0:0 -> #0:0 (mjpeg (native) -> h264 (libx264)) 
```
 
This output indicated that it includes separate tracks for color, depth, and IR (infrared) video. Here's what the output means: 

* Stream #0:0: MJPEG video, titled "COLOR," representing the RGB video stream. 

* Stream #0:1: Raw video, titled "DEPTH," representing depth data in gray16be format. 

* Stream #0:2: Raw video, titled "IR," representing infrared data in gray16be format. 

* Stream #0:3: Attachment titled "calibration.json," which contains calibration data for the sensors.


## Repairing MKV

Here was my earlier attempt at repairing: https://chatgpt.com/share/67d4bf83-e608-8006-ae50-bd99881d92d6

clean_info.json comes from running the following command:

```
ffprobe -v error -print_format json -show_format -show_streams backup_data\kinect_tests\clean_recordings\stereo_test.mkv > clean_info.json
```

corrupt_info.json comes from running the following command:
```
ffprobe -v error -print_format json -show_format -show_streams backup_data\kinect_tests\corrupt_recordings\python_recording.mkv > corrupt_info.json
```

Maybe you could compare these json files to understand how to repair corrupt mkv.



## Useful documentation:
* [Official Azure Kinect Documentation](https://aus01.safelinks.protection.outlook.com/GetUrlReputation)
* [Kinect V2 Prep-processing report](https://unsw-my.sharepoint.com/:w:/g/personal/z5162987_ad_unsw_edu_au/ET-hvHNpYEhImUR3sb59Ps8BoSkFdJUgnnqhOXFTiFs3rA?e=A6SdfI)
  * (more details on our configs for the kinect recordings and use of ffmpeg to extract video)
* https://www.matroska.org/technical/basics.html
* https://learn.microsoft.com/en-us/previous-versions/azure/kinect-dk/record-file-format



# PyKinect README:

[![PyPI](https://img.shields.io/pypi/v/pykinect-azure?color=2BAF2B)](https://pypi.org/project/pykinect-azure/)
# pyKinectAzure

![Azure kinect color and depth combination](https://github.com/ibaiGorordo/pyKinectAzure/blob/master/doc/images/outputImage.jpg)

Python 3 library for the Azure Kinect DK sensor-SDK.

## Similar solutions
Part of the ideas in this repository are taken from following repositories:
* [pyk4a](https://github.com/etiennedub/pyk4a): Really nice and clean Python3 wrapper for the Kinect Azure SDK.

* [Azure-Kinect-Python](https://github.com/hexops/Azure-Kinect-Python): More complete library using ctypes as in this repository, however, examples about how to use the library are missing and the library is harder to use.

The objective of this repository is to combine the strong points of both repositories by creating a easy to use library that allows the use of most of the functions of the Kinect Azure. Also, to create sample programs to showcase the uses of the library

## Prerequisites
* [Azure-Kinect-Sensor-SDK](https://github.com/microsoft/Azure-Kinect-Sensor-SDK): required to build this library.
  To use the SDK, refer to the installation instructions [here](https://github.com/microsoft/Azure-Kinect-Sensor-SDK).
* **ctypes**: required to read the library.
* **numpy**: required for the matrix calculations
* **opencv-python**: Required for the image transformations and visualization.

## Installation
```commandline
pip install pykinect_azure
```

## How to use this library

* The library has **been tested in Windows 10 and Ubuntu 20.04** with the Kinect Azure SDK 1.4.0 and 1.4.1, it should also work with other operating systems.

  - **Windows:** When using the pyKinectAzure class, it requires the **path to the k4a.dll module**, make sure that the path is the correct one for your Kinect Azure SDK version. By default the path (**module_path**) is set to  ```C:\\Program Files\\Azure Kinect SDK v1.4.0\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll```.

  - **Linux:** When using the pyKinectAzure class, it requires the **path to the k4a.so module**, make sure that the path is the correct one for your Kinect Azure SDK version. When using Linux set **module_path** to  ```/usr/lib/x86_64-linux-gnu/libk4a.so```, please follow the [instruction](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md) from microsoft to install the right packages.
  
   - **Nvidia Jetson:** When using the pyKinectAzure class, it requires the **path to the k4a.so module**, make sure that the path is the correct one for your Kinect Azure SDK version. When using Nvidia Jetson set **module_path** to to  ```'/usr/lib/aarch64-linux-gnu/libk4a.so'```, please follow the [instruction](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md) from microsoft to install the right packages.

* The **pyKinectAzure** class is a wrapper around the **_k4a.py** module to make the library more understandable. However, the **pyKinectAzure** class still contains few methods from the Kinect Azure SDK

* The **_k4a.py** module already contains all the methods in the Kinect Azure SDK. So, for more advanced of the Kinect Azure SDK check the **_k4a.py** module.

## Examples

For an example on how to obtain and visualize the depth data from the Azure Kinect DK check the **exampleDepthImageOpenCV.py** script.
```
git clone https://github.com/ibaiGorordo/pyKinectAzure.git
cd pyKinectAzure/examples
python exampleDepthImageOpenCV.py
```

Also, there is an example to obtain and visualize the smooth depth from the Azure Kinect DK check the **exampleSmoothDepthImageOpenCV.py** script.
```
python exampleSmoothDepthImageOpenCV.py
```
> note: when you are dealing on the linux platform, please insure that the user have permission to the usb devices, or always execute under the root permission by adding `sudo` ahead.

![Azure kinect smoothed depth image comparison](https://github.com/ibaiGorordo/pyKinectAzure/blob/master/doc/images/Azure%20kinect%20smoothed%20depth%20image.png)


## Contribution

Feel free to send pull requests.

Bug reports are also appreciated. Please include as much details as possible.

## TODO:

### Wrappers for the Kinect Azure data
- [x] Create wrapper to read depth images.
- [x] Create wrapper to read Infrared images.
- [x] Create wrapper to read IMU data.
- [x] Create function to convert image buffer to image depending on the image type.
- [x] Create wrapper to transform depth image to color image.
- [x] Create wrapper to transform depth image to 3D point cloud.
- [x] Create funtion to visualize 3D point cloud.

### Create examples
- [x] Example to visualize depth images.
- [x] Example to visualize passive IR images.
- [x] Example to plot IMU data.
- [x] Example to visualize Depth as color image.
- [x] Example to overlay depth color with alpha over real image.
- [x] Example to visualize 3D point cloud

### Body tracking
- [x] Create library for the body tracking SDK similar the same way as the current library.
- [x] Combine image and skeleton data.
- [ ] Generate 3D skeleton visualization.

### Future ideas
- [ ] Run Deep Learning models on Kinect data (Openpose 3D skeleton, semantic segmentation with depth, monocular depth estimation validation)
- [ ] Track passive infrared marker for motion capture analysis
