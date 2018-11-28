# coding: utf-8

import os
import argparse
from multiprocessing import Pool, current_process

def calc_tvl1_flow(vid_item):
    vid_path = vid_item[0]
    vid_name = os.path.basename(vid_path).split('.')[0]
    vid_idx = vid_item[1]

    cur_out_dir = os.path.join(OUT_DIR, vid_name)
    if not os.path.exists(cur_out_dir):
        os.makedirs(cur_out_dir)

    cur_img_path = os.path.join(cur_out_dir, 'img')
    cur_flow_x_path = os.path.join(cur_out_dir, 'flow_x')
    cur_flow_y_path = os.path.join(cur_out_dir, 'flow_y')

    current = current_process()
    dev_id = (int(current._identity[0]) - 1) % NUM_GPU

    flow_mode_dict = {'tvl1': 'extract_gpu', 'warp_tvl1': 'extract_warp_gpu'}

    if OUT_FMT == 'zip':
        command = '{} -f {} -x {} -y {} -i {} -b 20 -t 1 -s {} -d {} -w {} -h {} -o {}'.format(
            flow_mode_dict[FLOW_TYPE], vid_path, cur_flow_x_path, cur_flow_y_path, cur_img_path if KEEP_FRAMES else '/dev/null', STEP, dev_id, WIDTH, HEIGHT, OUT_FMT
        )
    else:
        if not os.path.exists(cur_img_path):
            os.makedirs(cur_img_path)
        if not os.path.exists(cur_flow_x_path):
            os.makedirs(cur_flow_x_path)
        if not os.path.exists(cur_flow_y_path):
            os.makedirs(cur_flow_y_path)
        command = '{} -f {} -x {} -y {} -i {} -b 20 -t 1 -s {} -d {} -w {} -h {} -o {}'.format(
            flow_mode_dict[FLOW_TYPE], vid_path, cur_flow_x_path+'/flow_x', cur_flow_y_path+'/flow_y', cur_img_path+'/img' if KEEP_FRAMES else '/dev/null', STEP, dev_id, WIDTH, HEIGHT, OUT_FMT
        )

    os.system(command)
    print '{}/{} {} finished!'.format(vid_idx, VID_NUM, vid_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract optical flows with multi-gpu support.")
    parser.add_argument("vid_txt_path", type=str, help='Input txt files containing video paths')
    parser.add_argument("out_dir", type=str, help='Destination directory to store flow results')

    parser.add_argument("--flow_type", type=str, default='tvl1', choices=['tvl1', 'warp_tvl1'], help='Optical flow type.')
    parser.add_argument("--out_fmt", type=str, default='dir', choices=['dir','zip'], help='Output file format.')
    parser.add_argument("--num_gpu", type=int, default=4, help='Number of GPUs')
    parser.add_argument("--step", type=int, default=1, help='Specify the step for frame sampling')
    parser.add_argument("--keep_frames", type=lambda x: (str(x).lower() == 'true'), default=False, help='Whether to save frame data.')
    parser.add_argument("--width", type=int, default=0, help='Resize image width.')
    parser.add_argument("--height", type=int, default=0, help='Resize image height.')

    args = parser.parse_args()
    f = open(args.vid_txt_path, 'r').readlines()
    vid_paths = [line.strip() for line in f]
    VID_NUM = len(vid_paths)
    NUM_GPU = args.num_gpu
    FLOW_TYPE = args.flow_type
    OUT_DIR = args.out_dir
    OUT_FMT = args.out_fmt
    KEEP_FRAMES = args.keep_frames
    STEP = args.step
    WIDTH = args.width
    HEIGHT = args.height

    if (WIDTH == 0 and HEIGHT != 0) or (WIDTH != 0 and HEIGHT == 0):
        print '*****' * 20
        print 'WARNING: width and height must be both specified to take effect. Now image will not be resized!'
        print '*****' * 20

    pool = Pool(NUM_GPU)
    pool.map(calc_tvl1_flow, zip(vid_paths, xrange(VID_NUM)))
    pool.close()
