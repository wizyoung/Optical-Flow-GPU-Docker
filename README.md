# Optical-Flow-GPU
Calculate dense optical flow using TV-L1 algorithm with NVIDIA GPU acceleration. The CPU version is also included. [Dockerhub link](https://hub.docker.com/r/wizyoung/optical-flow-gpu/)

Docker image environment: OpenCV 2.4, CUDA 8, cuDNN 5.

The dense flow C++ source code for building is from [yjxiong/dense_flow](https://github.com/yjxiong/dense_flow). The docker image is based on [willprice/opencv2-cuda8](https://hub.docker.com/r/willprice/opencv2-cuda8/). If you want to build opencv with cuda support yourself, you can refer to this [dockerfile](https://github.com/dl-container-registry/opencv2/blob/master/Dockerfile).

**Requirements**: docker, nvidia-docker. If you have libseccomp2 version conflict problems when installing docker on ubuntu, you can refer to this [solution](https://stackoverflow.com/a/53481527/6631854).

### Usage

#### 1. Directly use the prebuilt binaries (no multi gpu support)

```shell
extract_cpu [OPTION] ...  # using cpu
extract_gpu [OPTION] ...  # using gpu
extract_warp_gpu [OPTION] ...  # using gpu to extract warp flow
```

Avaliable options:

- `-f`: video path.
- `-x`: filename of flow x component.
- `-y`: filename of flow y component.
- `-i`: filename of extracted RGB image.
- `-b`: boundary to clip the flow value. For example, `-b 20` means clip the flow value beyond [-20, 20] and maps the [-20, 20] interval to [0, 255] in grayscale image space.
- `-t`: flow calculation method. 0: Brox, 1: TVL1. 
- `-s`: step for frame sampling. 1 means no skipping frame in calculation.
- `-d`: gpu id.
- `-w`, `-h`: resize the image **before** flow calculation. w = resized_width, h = resized_height. 0 means no resize. Note: If you want to resize the image, w and h must be both specified to take effect.
- `-o`: output format. 'dir' means saving the flow image data in directory format. 'zip' means saving the flow image data in zipped file format.

Example:

```shell
# first mount the folder containing videos to /data
nvidia-docker run -it -v path_to_mount:/data wizyoung/optical-flow-gpu bash 
mkdir /data/result
# RGB image data is abandoned here
extract_gpu -f /data/video.mp4 -x /data/result/flow_x -y /data/result/flow_y -i /dev/null -b 20 -t 1 -s 1 -d 0 -w 100 -h 100 -o zip
```

Result:

```shell
# path: /data/
.
├── result
│   ├── flow_x.zip
│   └── flow_y.zip
└── video.mp4
```

#### 2. Batch processing using python script with multi gpu support

I included the python wrapper script with multi gpu support in the `/src` path:

```shell
root@eca86f630747:/src# python multi_gpu_extract.py -h
usage: multi_gpu_extract.py [-h] [--flow_type {tvl1,warp_tvl1}]
                            [--out_fmt {dir,zip}] [--num_gpu NUM_GPU]
                            [--step STEP] [--keep_frames KEEP_FRAMES]
                            [--width WIDTH] [--height HEIGHT] [--log LOG]
                            vid_txt_path out_dir

Extract optical flows with multi-gpu support.

positional arguments:
  vid_txt_path          Input txt files containing video paths.
  out_dir               Destination directory to store flow results.

optional arguments:
  -h, --help            show this help message and exit
  --flow_type {tvl1,warp_tvl1}
                        Optical flow type. Default: tvl1
  --out_fmt {dir,zip}   Output file format. Default: zip
  --num_gpu NUM_GPU     Number of GPUs. Default: 4
  --step STEP           Specify the step for frame sampling. Default: 1
  --keep_frames KEEP_FRAMES
                        Whether to save RGB frame data. Default: False
  --width WIDTH         Resize image width. Default: 0 (no resize)
  --height HEIGHT       Resize image height. Default: 0 (no resize)
  --log LOG             Output log file path. Default: ./out.log
```

NOTE: 

(1) `vid_txt_path` should be a txt file each line containing a video path. 

Example:

```shell
# NOTE: /data/ is the mounting point rather than the actual path
# vid_txt_path: /data/video_list.txt
/data/videos/1.mp4
/data/videos/2.mp4
/data/videos/3.mp4
...
```

(2) `num_gpu` means using gpus from 0 to num_gpu - 1.

(3) The log file records the processing progress and error (likely corrupted videos) during processing. 

Example:

```
python multi_gpu_extract.py /data/video_list.txt /data/results --flow_type tvl1 --out_fmt zip --num_gpu 4 --step 1 --keep_frames True --width 100 --height 100 --log /data/log.log
```

