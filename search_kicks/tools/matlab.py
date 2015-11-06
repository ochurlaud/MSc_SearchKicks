#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions to load/save particular files structures from/in .mat format.
"""

import numpy as np
import scipy.io


def load_timeanalys(filename):
    data = scipy.io.loadmat(filename)

    sample_nb = data['difforbitX'].shape[1]
    BPMx_nb = data['difforbitX'][0, 0].shape[0]
    BPMy_nb = data['difforbitY'][0, 0].shape[0]
    CMx_nb = data['CMx'][0, 0].shape[0]
    CMy_nb = data['CMy'][0, 0].shape[0]

    BPMx = np.zeros((BPMx_nb, sample_nb))
    BPMy = np.zeros((BPMy_nb, sample_nb))
    CMx = np.zeros((CMx_nb, sample_nb))
    CMy = np.zeros((CMy_nb, sample_nb))

    for i in range(sample_nb):
        for j in range(BPMx_nb):
            BPMx[j, i] = data['difforbitX'][0, i][j, 0]
        for j in range(BPMy_nb):
            BPMy[j, i] = data['difforbitY'][0, i][j, 0]
        for j in range(CMx_nb):
            CMx[j, i] = data['CMx'][0, i][j, 0]
        for j in range(CMy_nb):
            CMy[j, i] = data['CMy'][0, i][j, 0]

    return BPMx, BPMy, CMx, CMy


def save_timeanalys(filename, BPMx, BPMy, CMx, CMy):

    sample_nb = BPMx.shape[1]

    data = {'difforbitX': np.empty((1, sample_nb), dtype=object),
            'difforbitY': np.empty((1, sample_nb), dtype=object),
            'CMx': np.empty((1, sample_nb), dtype=object),
            'CMy': np.empty((1, sample_nb), dtype=object)
            }
    for i in range(sample_nb):
        data['difforbitX'][0, i] = BPMx[:, i, np.newaxis]
        data['difforbitY'][0, i] = BPMy[:, i, np.newaxis]
        data['CMx'][0, i] = CMx[:, i, np.newaxis]
        data['CMy'][0, i] = CMy[:, i, np.newaxis]

    print(filename)
    scipy.io.savemat(filename, data)

    return True


def load_orbit(filename):
    data = scipy.io.loadmat(filename)
    return data['orbit']


def save_orbit(filename, orbit):
    scipy.io.savemat(filename, {'orbit': orbit})
    return True