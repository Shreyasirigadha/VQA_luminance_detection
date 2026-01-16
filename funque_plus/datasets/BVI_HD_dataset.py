
import os
from videolib import standards

dataset_name = 'BVI_HD_tiny'
dataset_dir = '/content/drive/MyDrive/BVI_HD_Dataset'
ref_dir = os.path.join(dataset_dir, 'ORIG_YUV')
dis_dir = os.path.join(dataset_dir, 'HEVC_YUV')

ref_standard = standards.sRGB
dis_standard = standards.sRGB
width = 1920
height = 1080

ref_videos = {
    2: {'content_name': 'Boxing', 'path': ref_dir + '/Boxing_1920x1080_30fps.yuv'},
    13:{'content_name': 'Grass',  'path': ref_dir + '/Grass_1920x1080_60fps.yuv'},
}

dis_videos = {
    # Boxing (content_id 2)
    13:{'content_id': 2, 'score': 1.6111111111111112,
        'path': dis_dir + '/Boxing_1920x1080_30fps_HEVC_QP27.yuv'},
    16:{'content_id': 2, 'score': 38.666666666666664,
        'path': dis_dir + '/Boxing_1920x1080_30fps_HEVC_QP42.yuv'},

    # Grass (content_id 13)
    79:{'content_id': 13, 'score': 5.444444444444445,
        'path': dis_dir + '/Grass_1920x1080_60fps_HEVC_QP27.yuv'},
    82:{'content_id': 13, 'score': 30.88888888888889,
        'path': dis_dir + '/Grass_1920x1080_60fps_HEVC_QP47.yuv'},
}