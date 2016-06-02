#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IO Module
=========

Load/Save time data from multiple supports and formats.

Note
----
It's better to use these function in a try/except structure as they raise
errors whenever something goes wrong.

@author: Olivier CHURLAUD <olivier.churlaud@helmholtz-berlin.de>
"""

import csv
from datetime import datetime, timedelta
import locale
import os

try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except:
    from urllib import urlopen, urlencode

import h5py
import numpy as np
import scipy.io

DATETIME_ISO = "%Y-%m-%dT%H:%M:%S.%f"


def load_orbit(*args):
    """ Load an orbit.

    This uses function only calls other functions based on the number and
    values of its arguments.

    Raises
    -------
    ValueError:
        If the arguments don't fit any known case.
    Exception:
        If underlying function return exceptions.
    """

    if len(args) == 1:  # can only be a file
        filename = args[0]
        ext = os.path.splitext(filename)[1]
        if ext == ".hdf5":
            try:
                return load_orbit_hdf5(filename)
            except Exception:
                raise
        elif ext == ".mat":
            try:
                return load_orbit_dump(filename)
            except Exception:
                raise
        elif ext == '.npy':
            try:
                return load_orbit_npy(filename)
            except Exception:
                raise
        else:
            raise ValueError("I don't know how to load this type of file '{}'."
                             .format(filename))
    elif len(args) == 2 or len(args) == 3:
        return load_orbit_from_archiver(*args)
    else:
        raise ValueError("This function has 1, 2 or 3 arguments.")


class OrbitData(object):
    """ Data container class that should be used in the programs.

    The users of this module should use this class to work in an abstract way
    with the data.

    If the object cannot be constructed, an exception is raised.

    """

    def __init__(self, BPMx=None, BPMy=None, CMx=None, CMy=None,
                 sampling_frequency=None, measure_date=None):

        sample_nb = 0

        def check_single_arrays(name, item):
            if item is not None:
                return

            if type(item) is not np.ndarray or type(item) is not np.ndarray:
                raise TypeError("{} type must be ndarrays, not {}."
                                .format(name, type(item)))
            if item.ndim != 2:
                raise ValueError("{} must be a 2-dimensional arrays."
                                 .format(name))

            if sample_nb and sample_nb != item.shape[1]:
                raise ValueError("All arrays must have the same number of "
                                 "samples, {} has {}, an other has {}."
                                 .format(name, item.shape[1], sample_nb))

        check_single_arrays('BPMx', BPMx)
        check_single_arrays('BPMy', BPMy)
        check_single_arrays('CMx', CMx)
        check_single_arrays('CMy', CMy)

        self.BPMx = BPMx
        self.BPMy = BPMy
        self.CMx = CMx
        self.CMy = CMy
        self.sampling_frequency = sampling_frequency
        self.sample_number = sample_nb
        self.measure_date = measure_date


def load_golden_orbit(filename):
    """ This should be in PyML
    """
    names = []
    orbitX = []
    orbitY = []
    try:
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f, delimiter='\t')

            for row in reader:
                names.append(row[0].replace(' ', ''))
                orbitX.append(float(row[1]))
                orbitY.append(float(row[2]))
    except Exception:
        raise
    else:
        return np.array(orbitX), np.array(orbitY), names


def load_orbit_npy(filename):

    try:
        data = np.load(filename)[0]
    except Exception:
        raise
    else:
        if '__version__' not in data:
            raise ValueError("Version of data not set")

        if data['__version__'] == '1.0':
            try:
                return OrbitData(
                    BPMx=data['BPMx'], BPMy=data['BPMy'],
                    CMx=data['CMx'], CMy=data['CMy'],
                    sampling_frequency=data['sampling_frequency'],
                    measure_date=datetime.strptime(data['measure_date'],
                                                   DATETIME_ISO)
                    )
            except Exception:
                raise
        else:
            raise NotImplementedError("The version {} is unknown to me, "
                                      "maybe you should teach it to me?"
                                      .format(data['__version__'])
                                      )


def save_orbit_npy(filename, obj):
    VERSION = '1.0'
    data = {
        'BPMx': obj.BPMx,
        'BPMy': obj.BPMy,
        'CMx': obj.CMx,
        'CMy': obj.CMy,
        'sampling_frequency': obj.sampling_frequency,
        'data_structure': "array[item, time_sample]",
        'measure_date': obj.measure_date.strftime(DATETIME_ISO),
        '__version__': VERSION,
    }
    np.save(filename, [data])


def load_orbit_hdf5(filename):

    try:
        with h5py.File(filename, 'r') as f:
            if '__version__' in f.attrs and f.attrs['__version__'] == '1.0':
                try:
                    return OrbitData(
                        BPMx=f['BPMx'], BPMy=f['BPMy'],
                        CMx=f['CMx'], CMy=f['CMy'],
                        sampling_frequency=f['sampling_frequency'],
                        measure_date=(f.attrs['measure_date'], DATETIME_ISO)
                        )
                except:
                    raise
            else:
                raise NotImplementedError("The version {} is unknown to me, "
                                          "maybe you should teach it to me?"
                                          .format(f.attrs['__version__']))
    except Exception:
        raise


def save_orbit_hdf5(filename, obj):
    """ Save data to hdf5
    """
    VERSION = '1.0'

    if os.path.splitext(filename) != '.hdf5':
        filename += '.hdf5'

    with h5py.File(filename, 'w') as f:
        f.create_dataset('BPMx', data=obj.BPMx)
        f.create_dataset('BPMy', data=obj.BPMy)
        f.create_dataset('CMx', data=obj.CMx)
        f.create_dataset('CMy', data=obj.CMy)
        f.create_dataset('sampling_frequency', data=obj.sampling_frequency)
        f.attrs['data_structure'] = "array[item, time_sample]"
        f.attrs['measure_date'] = obj.measure_date.strftime(DATETIME_ISO)
        f.attrs['creation_date'] = datetime.now().strftime(DATETIME_ISO)
        f.attrs['__version__'] = VERSION


def load_orbit_dump(filename):

    try:
        data = scipy.io.loadmat(filename)
    except:
        raise
    else:
        if '__version__' not in data:
            print("Unknown version, I might not understand your data.")

        if data['__version__'] == '1.0':
            pass
        else:
            raise NotImplementedError("The version {} is unknown to me, "
                                      "maybe you should teach it to me?"
                                      .format(data['__version__']))

        keys = ['difforbitX', 'difforbitY',
                'CMx', 'CMy',
                '__version__', '__header__',
                ]
        for key in keys:
            if key not in data:
                raise ValueError("Input file is not well formated, "
                                 "'{}' is key missing"
                                 .format(key))

        # data['header'] = 'MATLAB 5.0 MAT-file, Platform: GLNX86, Created on: Mon May 30 16:30:30 2016'
        loc = locale.getlocale()
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        creation_date = (data['__header__'].decode('utf8')
                                           .split('Created on: ')[1])
        creation_date = datetime.strptime(creation_date,
                                          '%a %b %d %H:%M:%S %Y')
        locale.setlocale(locale.LC_ALL, loc)

        _, sample_nb = data['difforbitX'].shape

        BPMx_nb, _ = data['difforbitX'][0, 0].shape
        BPMy_nb, _ = data['difforbitY'][0, 0].shape
        CMx_nb, _ = data['CMx'][0, 0].shape
        CMy_nb, _ = data['CMy'][0, 0].shape

        BPMx = np.zeros((BPMx_nb, sample_nb))
        BPMy = np.zeros((BPMy_nb, sample_nb))
        CMx = np.zeros((CMx_nb, sample_nb))
        CMy = np.zeros((CMy_nb, sample_nb))

        for i in range(sample_nb):
            BPMx[:, i] = data['difforbitX'][0, i][:, 0]
            BPMy[:, i] = data['difforbitY'][0, i][:, 0]
            CMx[:, i] = data['CMx'][0, i][:, 0]
            CMy[:, i] = data['CMy'][0, i][:, 0]

        orbit_data = OrbitData(
            BPMx=BPMx, BPMy=BPMy,
            CMx=CMx, CMy=CMy,
            sampling_frequency=150,
            measure_date=creation_date
            )

        return orbit_data


def load_orbit_from_archiver(t_start, t_end):
    a = Archiver()
    data = a.read('ddd', t_start, t_end)

    if not data:
        raise RuntimeError("No data returned...I'm confused... "
                           "This is unexpected.")

    return data


class Archiver(object):
    url = "http://archiver.bessy.de/archive/cgi/CGIExport.cgi"

    def filter_camonitor(self, data):
        values = dict()

        datalist = data.decode('utf8').split('\t\n')

        # create dict of values/time
        for line in datalist[:-1]:
            # last element is empty
            l = line.split()
            key = l[0]
            value = l[3]
            t = datetime.strptime(' '.join(l[1:3]),
                                  "%Y-%m-%d %H:%M:%S.%f")

            if key not in values:
                values[key] = {'value': [], 'time': []}

            values[key]['value'].append(value)
            values[key]['time'].append(t)

        # Change the values in ndarray
        for key in values:
            values[key]['value'] = np.array(values[key]['value'])

        return values

    def read(self, var, t0, t1=None):

        if t1 is None:
            t1 = t0

        if type(t0) is not datetime \
                or type(t1) is not datetime:
            raise TypeError("2nd and 3rd arguments must be datetime.datetime"
                            "types")
        if t0 > t1:
            raise ValueError("End time must be greater than endtime.")

        now = datetime.now()
        if t1 > now:
            raise ValueError("End time must be in the past. "
                             "I'm not Marty, Doc..")

        same_week = now.isocalendar()[1] == t0.isocalendar()[1]

        if same_week:
            index = "/opt/Archive/current_week/index"
        else:
            index = "/opt/Archive/master_index"

        if type(var) is list:
            var = '\n'.join(var)

        data_dict = {'INDEX': index,
                     'COMMAND': "camonitor",
                     'STRSTART': 1,
                     'STARTSTR': t0.strftime("%Y-%m-%d %H:%M:%S"),
                     'STREND': 1,
                     'ENDSTR': t1.strftime("%Y-%m-%d %H:%M:%S"),
                     'NAMES': var,
                     }

        data = urlencode(data_dict, encoding='utf8')
        full_url = self.url + '?' + data
        try:
            with urlopen(full_url) as response:
                return self.filter_camonitor(response.read())
        except Exception:
            raise


def load_Smat(filename):
    try:
        smat = scipy.io.loadmat(filename)
    except Exception:
        raise
    else:
        if 'Rmat' not in smat:
            raise ValueError("Cannot find Rmat structure. Check the file you "
                             "provided.")

        Smat_xx = smat['Rmat'][0, 0]['Data']
        Smat_yy = smat['Rmat'][1, 1]['Data']

        return Smat_xx, Smat_yy


if __name__ == "__main__":
    a = Archiver()
    t0 = datetime(2016, 5, 30, 16, 30, 29)
    t1 = t0 + timedelta(minutes=10)
    r = a.read(['BBQR:X:MAX1202:CH0', 'MDIZ3T5G:current'], t0, t1)
