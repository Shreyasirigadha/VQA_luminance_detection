# datasets/HDR_dataset.py
import os
from videolib import standards

dataset_name = 'HDR-VDC_dataset'
dataset_dir = '/content/drive/MyDrive/HDR-VDC/'
ref_dir = os.path.join(dataset_dir, 'ref_yuv')
dis_dir = os.path.join(dataset_dir, 'test_yuv')

# HDR-aware color space (modify if you use HDR10, HLG, etc.)
ref_standard = standards.sRGB
dis_standard = standards.sRGB

# Keep None when clips have mixed resolutions/framerates
width = None
height = None

# ---- Reference clips ----
ref_videos = {
    1: {'content_name': 'TrafficLight', 'path': os.path.join(ref_dir, 'TrafficLight.yuv')},
    2: {'content_name': 'SolLevante_p2',       'path': os.path.join(ref_dir, 'SolLevante_p2.yuv')},
    3: {'content_name': 'SolLevante_p1','path': os.path.join(ref_dir, 'SolLevante_p1.yuv')},
    4: {'content_name': 'SmithHammering',      'path': os.path.join(ref_dir, 'SmithHammering.yuv')},
    5: {'content_name': 'Showgirl01',    'path': os.path.join(ref_dir, 'Showgirl01.yuv')},
    6: {'content_name': 'Bonfire',    'path': os.path.join(ref_dir, 'Bonfire.yuv')},
    7: {'content_name': 'FishingCloseshot',    'path': os.path.join(ref_dir, 'FishingCloseshot.yuv')},
}

# ---- Distorted clips ----
dis_videos = {
    # TrafficLight
    1:  {'content_id': 1, 'score': 93.8042217423819, 'path': os.path.join(dis_dir, 'TrafficLight_M_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    2:  {'content_id': 1, 'score': 90.5533006928712, 'path': os.path.join(dis_dir, 'TrafficLight_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    3:  {'content_id': 1, 'score': 84.2968390243238, 'path': os.path.join(dis_dir, 'TrafficLight_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    4:  {'content_id': 1, 'score': 92.6392201979661, 'path': os.path.join(dis_dir, 'TrafficLight_L_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    5:  {'content_id': 1, 'score': 84.1623681205041, 'path': os.path.join(dis_dir, 'TrafficLight_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    6:  {'content_id': 1, 'score': 67.4139334582177, 'path': os.path.join(dis_dir, 'TrafficLight_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    7:  {'content_id': 1, 'score': 96.5065293686084, 'path': os.path.join(dis_dir, 'TrafficLight_H_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    8:  {'content_id': 1, 'score': 90.8609909576453, 'path': os.path.join(dis_dir, 'TrafficLight_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},

    # SolLevante_p2
    9: {'content_id': 2, 'score': 88.8667133248947, 'path': os.path.join(dis_dir, 'SolLevante_p2_M_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    10: {'content_id': 2, 'score': 70.0198812589021, 'path': os.path.join(dis_dir, 'SolLevante_p2_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    11: {'content_id': 2, 'score': 53.6401730442698, 'path': os.path.join(dis_dir, 'SolLevante_p2_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    12: {'content_id': 2, 'score': 66.9930998455056, 'path': os.path.join(dis_dir, 'SolLevante_p2_L_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    13: {'content_id': 2, 'score': 44.67542694303, 'path': os.path.join(dis_dir, 'SolLevante_p2_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    14: {'content_id': 2, 'score': 22.7277306767653, 'path': os.path.join(dis_dir, 'SolLevante_p2_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    15: {'content_id': 2, 'score': 87.5672951758223, 'path': os.path.join(dis_dir, 'SolLevante_p2_H_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    16: {'content_id': 2, 'score': 74.0185307133439, 'path': os.path.join(dis_dir, 'SolLevante_p2_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},

    # SolLevante_p1
    17: {'content_id': 3, 'score': 92.5025510836347, 'path': os.path.join(dis_dir, 'SolLevante_p1_M_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    18: {'content_id': 3, 'score': 87.7767518304, 'path': os.path.join(dis_dir, 'SolLevante_p1_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    19: {'content_id': 3, 'score': 81.1890350650512, 'path': os.path.join(dis_dir, 'SolLevante_p1_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    20: {'content_id': 3, 'score': 83.6588393291709, 'path': os.path.join(dis_dir, 'SolLevante_p1_L_3840x2160.yuv'), 'width': 3840 , 'height' : 2160},
    21: {'content_id': 3, 'score': 59.9170588299554, 'path': os.path.join(dis_dir, 'SolLevante_p1_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    22: {'content_id': 3, 'score': 49.9219682253726, 'path': os.path.join(dis_dir, 'SolLevante_p1_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    23: {'content_id': 3, 'score': 93.0577463074693, 'path': os.path.join(dis_dir, 'SolLevante_p1_H_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    24: {'content_id': 3, 'score': 90.5872248479745, 'path': os.path.join(dis_dir, 'SolLevante_p1_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},

    # SmithHammering
    25: {'content_id': 4, 'score': 84.2935928234298, 'path': os.path.join(dis_dir, 'SmithHammering_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    26: {'content_id': 4, 'score': 72.7510854412921, 'path': os.path.join(dis_dir, 'SmithHammering_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    27: {'content_id': 4, 'score': 41.6630188292838, 'path': os.path.join(dis_dir, 'SmithHammering_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    28: {'content_id': 4, 'score': 25.990737121732, 'path': os.path.join(dis_dir, 'SmithHammering_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    29: {'content_id': 4, 'score': 86.3862996796531, 'path': os.path.join(dis_dir, 'SmithHammering_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},

    #Showgirl01
    30: {'content_id': 5, 'score': 92.0325169923576, 'path': os.path.join(dis_dir, 'Showgirl01_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    31: {'content_id': 5, 'score': 84.5350274210869, 'path': os.path.join(dis_dir, 'Showgirl01_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    32: {'content_id': 5, 'score': 75.2041790891663, 'path': os.path.join(dis_dir, 'Showgirl01_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    33: {'content_id': 5, 'score': 60.6767573474493, 'path': os.path.join(dis_dir, 'Showgirl01_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    34: {'content_id': 5, 'score': 90.4658362260727, 'path': os.path.join(dis_dir, 'Showgirl01_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    
    #Bonfire
    35: {'content_id': 6, 'score': 89.1434201686069, 'path': os.path.join(dis_dir, 'Bonfire_M_3840x2160.yuv'), 'width': 1920 , 'height' : 1080},
    36: {'content_id': 6, 'score': 79.4205778137645, 'path': os.path.join(dis_dir, 'Bonfire_M_1920x1080.yuv'), 'width': 1280 , 'height' : 720},
    37: {'content_id': 6, 'score': 71.7062938981685, 'path': os.path.join(dis_dir, 'Bonfire_M_1280x720.yuv'), 'width': 1920 , 'height' : 1080},
    38: {'content_id': 6, 'score': 66.3231584667284, 'path': os.path.join(dis_dir, 'Bonfire_L_3840x2160.yuv'), 'width': 1280 , 'height' : 720},
    39: {'content_id': 6, 'score': 47.2122391834586, 'path': os.path.join(dis_dir, 'Bonfire_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    40: {'content_id': 6, 'score': 31.2648854028496, 'path': os.path.join(dis_dir, 'Bonfire_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    41: {'content_id': 6, 'score': 93.3327084763599, 'path': os.path.join(dis_dir, 'Bonfire_H_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    42: {'content_id': 6, 'score': 92.782087801487, 'path': os.path.join(dis_dir, 'Bonfire_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},

    #FishingCloseshot
    43: {'content_id': 7, 'score': 71.5423841020564, 'path': os.path.join(dis_dir, 'FishingCloseshot_M_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    44: {'content_id': 7, 'score': 64.9364042632672, 'path': os.path.join(dis_dir, 'FishingCloseshot_M_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    45: {'content_id': 7, 'score': 23.2011643951214, 'path': os.path.join(dis_dir, 'FishingCloseshot_L_1920x1080.yuv'), 'width': 1920 , 'height' : 1080},
    46: {'content_id': 7, 'score': 20.3616644657135, 'path': os.path.join(dis_dir, 'FishingCloseshot_L_1280x720.yuv'), 'width': 1280 , 'height' : 720},
    47: {'content_id': 7, 'score': 86.9215566373378, 'path': os.path.join(dis_dir, 'FishingCloseshot_H_1280x720.yuv'), 'width': 1280 , 'height' : 720},
}