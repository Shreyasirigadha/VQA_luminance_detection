## **VQA with Luminance Clipping Detection (FUNQUE+ Extension)**

This repository contains the implementation of a Full-Reference Video Quality Assessment (VQA) framework extended with HDR luminance / brightness clipping detection, built on top of the FUNQUE+ architecture.

The project enhances perceptual video quality modeling by explicitly detecting highlight saturation and clipping artifacts in HDR (PQ-encoded) content, which are often ignored by traditional VQA metrics.

# **Project Motivation**

Traditional VQA models such as SSIM, VMAF, and even FUNQUE+ primarily focus on structural fidelity and perceptual distortion, but do not explicitly capture HDR brightness clipping artifacts.

This project introduces:

- A dedicated HDR luminance clipping feature module

- PQ-domain luminance analysis

- Frame-level blob detection for saturated highlights

- Video-level aggregation of clipping severity

- The result is a more perceptually aligned quality representation for HDR content.


# **PROJECT_ANALYSIS**

*Key Features*

- Full-reference VQA pipeline (built on FUNQUE+ architecture)

- HDR luminance clipping detection (PQ / 10-bit aware)

- Supports MP4, YUV420 8-bit, and P010 10-bit formats

- Modular layered design (algorithm → video I/O → framework integration)

- Dataset-driven batch processing

- Cross-validation pipeline for evaluation

- Parallel feature extraction using multiprocessing

*Core HDR clipping design is layered as:*

Algorithm → Video Processing → Framework Wrapper

# Project Structure

```
VQA_final/
├── funque_plus/
│   ├── datasets/                     # Dataset definitions (HDR_VDC, BVI-HD, etc.)
│   ├── extract_features.py           # Extract features from one video pair
│   ├── extract_features_from_dataset.py
│   ├── crossval_features_on_dataset.py
│   │
│   └── funque_plus/
│       ├── feature_extractors/
│       │   └── funque_feature_extractors.py
│       │
│       └── features/
│           └── funque_atoms/
│               ├── hdr_clipping.py          # Core clipping algorithms
│               ├── hdr_clip_test.py         # Video-level processing
│               ├── hdr_clipping_fex.py      # Runner-compatible extractor
│               └── luminace_detection.py    # Dataset batch script
```


# **HDR Clipping Module Design**

The luminance detection module follows a clean layered architecture:

*1. Core Algorithm Layer (hdr_clipping.py)*

Implements:

- PQ EOTF (PQ → luminance in nits)

- Thresholding of saturated pixels

- Connected component detection (clipped blobs)

- Feature computation:

  - Clipped area ratio

  - Number of clipped regions

  - Largest region size

  - Flatness

  - Severity score

*2. Video Processing Layer (hdr_clip_test.py)*

Handles:

- MP4 / YUV / P010 reading

- Frame iteration

- Calls core algorithms per frame

- Aggregates into video-level features

*3. Framework Integration Layer (hdr_clipping_fex.py)*

Provides:

- HDRClippingFex class

- Compatible with qualitylib Runner interface

- Plug-and-play into FUNQUE+ pipeline

- This design ensures:

  - Reusability

  - Testability

  - Clean separation of concerns


# **HDR_CLIPPING_CONNECTIONS**

Example Clipping Features Produced

Per video, the system outputs metrics such as:

`{
  "clip_area_ratio_mean": 0.0213,
  "clip_area_ratio_p95": 0.0471,
  "clip_frames_over_thresh": 0.112,
  "clip_severity_mean": 0.338,
  "clip_severity_p95": 0.462
}`

These are automatically integrated into the final VQA feature vector.

# **Installation**

*Create a virtual environment:*

`python3 -m venv .venv
source .venv/bin/activate`

*Install dependencies:*

`pip install -r requirements.txt`

(If using Colab, install system dependencies such as ffmpeg as required.)

*Usage*
*Extract features for a single video pair*

`python3 extract_features.py \
  --ref_video path/to/reference.mp4 \
  --dis_video path/to/distorted.mp4 \
  --fex_name FUNQUE_fex`

*Extract features for a full dataset*

`python3 extract_features_from_dataset.py \
  --dataset datasets/dataset.py \
  --fex_name FUNQUE_fex \
  --processes 4`

*Cross-validation evaluation*

`python3 crossval_features_on_dataset.py \
  --dataset datasets/dataset.py \
  --fex_name FUNQUE_fex \
  --splits 100 \
  --processes 4`

# **Contributions Over Baseline FUNQUE+**

This project extends FUNQUE+ by adding:

- Explicit modeling of HDR clipping artifacts

- PQ luminance-domain analysis

- Blob-level spatial statistics

- Video-level clipping severity modeling

- Dataset-scale luminance batch analysis (luminace_detection.py)

- This improves perceptual alignment for HDR content, especially in scenes with:

  - Bright skies

  - Specular highlights

  - Fire, reflections, neon lights

  - Overexposed HDR grading

# **Overall Summary**

This project provides:

- A perceptually richer, HDR-aware, full-reference video quality framework by combining:

- FUNQUE+ efficiency

- Classical quality features

- Explicit luminance clipping modeling
