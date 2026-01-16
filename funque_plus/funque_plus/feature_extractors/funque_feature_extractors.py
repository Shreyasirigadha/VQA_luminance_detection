from typing import Dict, Any, Optional
from videolib import Video
from qualitylib.feature_extractor import FeatureExtractor
from qualitylib.result import Result
import numpy as np
import cv2
import copy

from ..features.funque_atoms import pyr_features, vif_utils, filter_utils
from ..features.funque_atoms.hdr_clip_test import detect_brightness_clipping_video


class FunqueFeatureExtractor(FeatureExtractor):
    """
    A feature extractor that implements FUNQUE (HDR version, crossval safe).
    """
    NAME = 'FUNQUE_fex'
    VERSION = '1.0'

    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 1
        self.vif_extra_levels = 1
        self.csf = 'ngan_spat'
        self.wavelet = 'haar'

        self.feat_names = (
            [f'ssim_cov_channel_y_levels_{self.wavelet_levels}',
             f'dlm_channel_y_scale_{self.wavelet_levels}',
             f'motion_channel_y_scale_{self.wavelet_levels}'] +
            [f'vif_approx_scalar_channel_y_scale_{scale+1}' for scale in range(self.wavelet_levels + self.vif_extra_levels)] +
            ['clip_area_ratio_mean', 'clip_area_ratio_p95', 'clip_frames_over_thresh',
             'clip_severity_mean', 'clip_severity_p95']
        )

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}
        channel_name = 'y'
        channel_ind = 0

        try:
            with Video(
                asset_dict['ref_path'], mode='r',
                standard=asset_dict['ref_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_ref, Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:

                w_crop = (v_ref.width >> (self.wavelet_levels + self.vif_extra_levels + 1)) << (self.wavelet_levels + self.vif_extra_levels)
                h_crop = (v_ref.height >> (self.wavelet_levels + self.vif_extra_levels + 1)) << (self.wavelet_levels + self.vif_extra_levels)
                prev_pyr_ref = None

                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    # Y channel
                    y_ref = cv2.resize(frame_ref.yuv[..., 0].astype(v_ref.standard.dtype),
                                       (frame_ref.width // 2, frame_ref.height // 2),
                                       interpolation=cv2.INTER_CUBIC).astype('float64') / asset_dict['ref_standard'].range
                    y_dis = cv2.resize(frame_dis.yuv[..., 0].astype(v_dis.standard.dtype),
                                       (frame_dis.width // 2, frame_dis.height // 2),
                                       interpolation=cv2.INTER_CUBIC).astype('float64') / asset_dict['dis_standard'].range
                    y_ref, y_dis = y_ref[:h_crop, :w_crop], y_dis[:h_crop, :w_crop]

                    # Filtering
                    channel_ref, channel_dis = [
                        filter_utils.filter_img(c, self.csf, self.wavelet, channel=channel_ind)
                        for c in (y_ref, y_dis)
                    ]

                    vif_pyr_ref, vif_pyr_dis = [
                        pyr_features.custom_wavedec2(c, self.wavelet, 'periodization',
                                                     self.wavelet_levels + self.vif_extra_levels)
                        for c in (channel_ref, channel_dis)
                    ]
                    pyr_ref = tuple([p[:1] for p in vif_pyr_ref])
                    pyr_dis = tuple([p[:1] for p in vif_pyr_dis])

                    if frame_ind % sample_interval:
                        prev_pyr_ref = copy.deepcopy(pyr_ref)
                        continue

                    # SSIM
                    ssim_cov = pyr_features.ssim_pyr(pyr_ref, pyr_dis, pool='cov')
                    feats_dict[f'ssim_cov_channel_{channel_name}_levels_1'].append(ssim_cov)

                    # VIF
                    vif_approx_scales = [
                        vif_utils.vif_spatial(a_ref, a_dis, sigma_nsq=5, k=9, full=False)
                        for a_ref, a_dis in zip(vif_pyr_ref[0], vif_pyr_dis[0])
                    ]
                    for lev, val in enumerate(vif_approx_scales):
                        feats_dict[f'vif_approx_scalar_channel_{channel_name}_scale_{lev + 1}'].append(val)

                    # DLM
                    dlm_val = pyr_features.dlm_pyr(pyr_ref, pyr_dis, csf=None)
                    feats_dict[f'dlm_channel_{channel_name}_scale_1'].append(dlm_val)

                    # Motion
                    motion_val = 0 if frame_ind == 0 or prev_pyr_ref is None else np.mean(
                        np.abs(pyr_ref[0][0] - prev_pyr_ref[0][0])
                    )
                    feats_dict[f'motion_channel_{channel_name}_scale_1'].append(motion_val)
                    prev_pyr_ref = copy.deepcopy(pyr_ref)

                # --- Luminance clipping features (run once) ---
                try:
                    clip_result = detect_brightness_clipping_video(
                        path=asset_dict['dis_path'],
                        input_type="p010",
                        width=asset_dict['width'],
                        height=asset_dict['height'],
                        frame_stride=1,
                        is_pq_10bit=True,
                    )
                    if isinstance(clip_result, dict):
                        clip_area_mean = float(clip_result.get("clip_area_ratio_mean", 0.0))
                        clip_area_p95 = float(clip_result.get("clip_area_ratio_p95", 0.0))
                        clip_frames_over = float(clip_result.get("clip_frames_over_thresh", 0.0))
                        clip_severity_mean = float(clip_result.get("clip_severity_mean", 0.0))
                        clip_severity_p95 = float(clip_result.get("clip_severity_p95", 0.0))
                    else:
                        clip_area_mean = clip_area_p95 = clip_frames_over = clip_severity_mean = clip_severity_p95 = float(clip_result)
                except Exception as e:
                    print(f"⚠️ Luminance clipping failed for {asset_dict['dis_path']}: {e}")
                    clip_area_mean = clip_area_p95 = clip_frames_over = clip_severity_mean = clip_severity_p95 = 0.0

                feats_dict['clip_area_ratio_mean'].append(clip_area_mean)
                feats_dict['clip_area_ratio_p95'].append(clip_area_p95)
                feats_dict['clip_frames_over_thresh'].append(clip_frames_over)
                feats_dict['clip_severity_mean'].append(clip_severity_mean)
                feats_dict['clip_severity_p95'].append(clip_severity_p95)

        except Exception as e:
            print(f"❌ Error processing {asset_dict['dis_path']}: {e}")
            feats_dict = {k: [0.0] for k in self.feat_names}

        # --- Clean and align ---
        for k in feats_dict:
            clean_vals = []
            for v in feats_dict[k]:
                if isinstance(v, (list, np.ndarray)):
                    v = np.mean(v)
                try:
                    clean_vals.append(float(v))
                except Exception:
                    clean_vals.append(0.0)
            feats_dict[k] = clean_vals

        max_len = max(len(v) for v in feats_dict.values())
        for k in feats_dict:
            if len(feats_dict[k]) < max_len:
                feats_dict[k] += [feats_dict[k][-1]] * (max_len - len(feats_dict[k]))

        feats = np.array([feats_dict[k] for k in self.feat_names], dtype=np.float64).T

        print(f"Processed {asset_dict['dis_path']}, shape={feats.shape}, dtype={feats.dtype}")
        return self._to_result(asset_dict, feats, self.feat_names)