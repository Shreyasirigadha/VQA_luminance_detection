# funque_plus/feature_extractors/hdr_clipping_fex.py
# ----------------------------------------------------
# Feature extractor that computes HDR brightness-clipping features
# for each distorted video and returns video-level aggregates.
#
# Works with:
#   • MP4/MOV (decoded via OpenCV → Y luma)
#   • Raw YUV420 (.yuv) if width/height are provided by the dataset/asset
#
# Usage with your runner:
#   python extract_features_from_dataset.py \
#       --dataset datasets/HDR_dataset.py \
#       --fex_name hdr_clipping \
#       --fex_version 1.0 \
#       --processes 2
#
# It expects dataset.py to provide ref_videos / dis_videos dicts.
# If using raw YUV, set dataset.width / dataset.height (or include width/height in each asset).
# ----------------------------------------------------

from __future__ import annotations
import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, Iterable, List, Union

# import the atom we wrote earlier
from ..funque_atoms.hdr_clipping import (
    brightness_clipping_features,
    aggregate_brightness_clipping,
)

# ---------- minimal interface expected by get_fex ----------
# get_fex("hdr_clipping", "1.0") should find this class.
NAME = "hdr_clipping"
VERSION = "1.0"

class HDRClippingFex:
    """
    Feature extractor for brightness clipping (HDR highlight saturation).
    Returns a dict of video-level features per asset.
    """

    name = NAME
    version = VERSION
    # Whether this extractor needs a reference path. We don't.
    requires_ref = False

    # You can pass optional kwargs via get_fex(..., fex_version=None) in some frameworks;
    # keeping signature flexible:
    def __init__(self, **kwargs) -> None:
        # Frame sampling: analyze every Nth frame to speed up 4K/8K.
        self.frame_stride = int(kwargs.get("frame_stride", 2))  # analyze every 2nd frame by default
        # If you know your content is PQ 10-bit raw YUV, set this True. For MP4 via OpenCV, keep False.
        self.is_pq_10bit = bool(kwargs.get("is_pq_10bit", False))
        # If you know display/master peak nits, set here; else None to infer per-frame robust peak.
        self.peak_nits = kwargs.get("peak_nits", None)  # e.g., 1000, 2000, 4000
        # Minimum blob area (pixels) for connected components
        self.area_min_px = int(kwargs.get("area_min_px", 64))
        # For MP4 decoded by OpenCV, we’re typically post-tone-map SDR domain → set is_hdr=False.
        self.treat_opencv_as_hdr = bool(kwargs.get("treat_opencv_as_hdr", False))

    # ---- main entry point (called by Runner) ----
    def __call__(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """
        asset is typically something like:
          {
            'asset_id': int,
            'content_id': int,
            'content_name': str,
            'path': '/abs/path/to/file',
            'width': optional,
            'height': optional,
            ...
          }
        """
        path = asset.get("path") if isinstance(asset, dict) else getattr(asset, "path", None)
        if not path or not os.path.exists(path):
            return {"error": f"missing_or_bad_path:{path}"}

        # choose a reader
        if path.lower().endswith(".yuv"):
            width = self._get_int(asset, "width")
            height = self._get_int(asset, "height")
            if not width or not height:
                return {"error": "yuv_requires_width_height"}
            frames = self._read_yuv420_frames(path, width, height, stride=self.frame_stride)
            is_hdr = self.is_pq_10bit  # you can toggle based on your pipeline
            per_frame = self._process_frames(
                frames, is_hdr=is_hdr, is_pq_10bit=self.is_pq_10bit
            )
        else:
            # MP4/MOV/etc. via OpenCV → returns 8-bit BGR in display domain
            per_frame = self._read_mp4_frames(path)
            if isinstance(per_frame, dict) and "error" in per_frame:
                return per_frame

        video_feats = aggregate_brightness_clipping(per_frame)

        # You can add additional metadata to help later analysis
        out = {"fex_name": self.name, "fex_version": self.version}
        out.update(video_feats)
        return out

    # --------------- helpers ---------------

    def _process_frames(
        self, frames: Iterable[np.ndarray], is_hdr: bool, is_pq_10bit: bool
    ) -> List[Dict[str, float]]:
        """Process frames through brightness clipping feature extraction."""
        per_frame = []
        for Y in frames:
            f = brightness_clipping_features(
                Y,
                is_hdr=is_hdr,
                is_pq_10bit=is_pq_10bit,
                peak_nits=self.peak_nits,
                area_min_px=self.area_min_px,
            )
            per_frame.append(f)
        return per_frame

    def _read_mp4_frames(self, path: str) -> Union[List[Dict[str, float]], Dict[str, str]]:
        """Read MP4/MOV frames via OpenCV and extract brightness clipping features."""
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return {"error": "opencv_open_failed"}
        
        try:
            per_frame = []
            is_hdr_for_opencv = self.treat_opencv_as_hdr  # usually False (already tone-mapped)
            
            # Optimize stride handling: avoid modulo check when stride == 1
            if self.frame_stride == 1:
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    # convert to Y (luma-like) for analysis
                    # Using Rec.601-ish luma from BGR; good enough for clipping geometry.
                    Y = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)[:, :, 0].astype(np.float32) / 255.0
                    f = brightness_clipping_features(
                        Y,
                        is_hdr=is_hdr_for_opencv,
                        is_pq_10bit=False,
                        peak_nits=self.peak_nits,
                        area_min_px=self.area_min_px,
                    )
                    per_frame.append(f)
            else:
                idx = 0
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    if (idx % self.frame_stride) == 0:
                        # convert to Y (luma-like) for analysis
                        # Using Rec.601-ish luma from BGR; good enough for clipping geometry.
                        Y = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)[:, :, 0].astype(np.float32) / 255.0
                        f = brightness_clipping_features(
                            Y,
                            is_hdr=is_hdr_for_opencv,
                            is_pq_10bit=False,
                            peak_nits=self.peak_nits,
                            area_min_px=self.area_min_px,
                        )
                        per_frame.append(f)
                    idx += 1
            return per_frame
        finally:
            cap.release()

    @staticmethod
    def _get_int(obj: Any, key: str) -> Optional[int]:
        if isinstance(obj, dict) and key in obj and obj[key] is not None:
            try:
                return int(obj[key])
            except Exception:
                return None
        if hasattr(obj, key):
            try:
                return int(getattr(obj, key))
            except Exception:
                return None
        return None

    def _read_yuv420_frames(
        self, path: str, width: int, height: int, stride: int = 1
    ) -> Iterable[np.ndarray]:
        """
        YUV420 planar (8-bit or 10-bit as packed into 8-bit LSB + MSB?).
        For brightness clipping we only need the Y plane.
        This reader assumes 8-bit YUV420 by default (common in many datasets).
        If you have 10-bit planar, adapt as noted below.
        """
        frame_size_y = width * height
        # Total per frame for 8-bit YUV420: Y + U/2 + V/2
        frame_size_uv = (width // 2) * (height // 2) * 2  # U/2 + V/2 for 4:2:0
        frame_size_total = frame_size_y + frame_size_uv

        # If you truly have 10-bit YUV420 planar (P010/YUV420P10),
        # you’ll need to adjust reading (2 bytes per sample), and extract 10-bit Y.
        # That change is straightforward—ping me if you need that variant.

        with open(path, "rb") as f:
            frame_idx = 0
            while True:
                # read Y plane
                y_bytes = f.read(frame_size_y)
                if len(y_bytes) < frame_size_y:
                    break
                # skip UV planes
                uv_bytes = f.read(frame_size_uv)
                if len(uv_bytes) < frame_size_uv:
                    break

                if (frame_idx % stride) == 0:
                    Y = np.frombuffer(y_bytes, dtype=np.uint8).reshape((height, width))
                    Yf = Y.astype(np.float32) / 255.0
                    yield Yf
                frame_idx += 1