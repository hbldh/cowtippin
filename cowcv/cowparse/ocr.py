#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ocr
-----------

:copyright: 2016-09-29 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import hashlib
import pathlib
import pickle

import numpy as np
from PIL import Image
import cv2

from cowcv.cowparse.utils import BoundingBox

SAVE_IMAGES = True


def detect_digits_in_roi(cowface, roi_bb):
    cowface_gray = cv2.cvtColor(cowface[:, :, ::-1], cv2.COLOR_BGR2GRAY)
    roi, roi_map = roi_bb(cowface), roi_bb.active_region
    roi_gray = cv2.cvtColor(roi[:, :, ::-1], cv2.COLOR_BGR2GRAY)

    mser = cv2.MSER_create()
    regions = mser.detectRegions(roi_gray, None)
    mser_bbs = [BoundingBox.create_from_coordinates(
        r, relative_to=roi_bb) for r in regions]

    digits = []
    for possible_digit_region in mser_bbs:
        digit = _classify(possible_digit_region(cowface_gray),
                          possible_digit_region)
        if digit is not None:
            digits.append((digit, possible_digit_region))

    return digits


def _classify(img, bb):
    if SAVE_IMAGES:
        with io.BytesIO() as bio:
            Image.fromarray(img).save(bio, format='png')
            bio.seek(0)
            img_md5 = hashlib.md5(bio.read())
            bio.seek(0)
        data_dir_path = pathlib.Path(
            __file__).resolve().parent.parent.joinpath('data', 'ocr')
        with open(str(data_dir_path.joinpath(str(img_md5) + '.png'))) as f:
            f.write(bio.read())
        with open(str(data_dir_path.joinpath(str(img_md5) + '.pkl'))) as f:
            pickle.dump(f, bb)

    return None

