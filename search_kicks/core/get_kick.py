# -*- coding: utf-8 -*-

from __future__ import division, print_function

import numpy as np
from numpy import cos, pi
import matplotlib.pyplot as plt

from search_kicks.tools.maths import fit_sine
from search_kicks.core import build_sine

def get_kick(orbit, phase, tune, plot=False, error_curves=False):
    """ Find the kick in the orbit.

        Parameters
        ----------
        orbit : np.array
            Orbit.
        phase : np.array
            Phase.
        tune : float
            The orbit tune.
        plot : bool, optional.
            If True, plot the orbit with the kick position, else don't.
            Default to False.

        Returns
        -------
        kick_phase : float
            The phase where the kick was found.
        cos_coefficients : [a, b]
            a and b so that the sine is a*cos(b+phase)

    """
    bpm_nb = orbit.size
    rms_tab = []
    best_rms = 0
    cos_coefficients = []

    # duplicate the signal to find the sine between the kick and its duplicate
    signal_exp = np.concatenate((orbit, orbit))
    phase_exp = np.concatenate((phase, phase + tune*2*pi))

    # shift the sine between each BPM and its duplicate and find the best
    # match
    for i in range(bpm_nb):
        signal_t = signal_exp[i:i+bpm_nb]
        phase_t = phase_exp[i:i+bpm_nb]
        _, b, c = fit_sine(signal_t, phase_t, False)
        cos_coefficients.append([b, c])

        y = b*cos(c + phase_t)

        # calculate the RMS. the best fit means that the kick is around
        # the ith BPMs
        rms = sum(pow(y-signal_t, 2))
        rms_tab.append(rms)
        if rms < best_rms or i == 0:
            best_rms = rms
            i_best = i

    b, c = cos_coefficients[i_best]
    apriori_phase = phase[i_best]
    k = int((apriori_phase + c)/np.pi + tune)
    solutions = -c - np.pi*tune + np.array([k, k+1])*np.pi
    idx = np.argmin(abs(solutions - apriori_phase))
    kick_phase = solutions[idx]

    if error_curves:
        transl = bpm_nb//2 - i_best
        rms_tab = np.roll(rms_tab, transl)
        cos_coef_tmp = np.array(np.roll(cos_coefficients, transl))

        offset = 2*pi
        n_lspace = 10000

        interval_rel = np.linspace(-offset, +offset, n_lspace)
        interval = interval_rel+phase_exp[i_best]

        plt.figure('skcore::get_kick -- Error curves [{}]'
                   .format(len(plt.get_fignums())))
        plt.subplot(211)
        plt.title('1- Sine Fit')
        idx_range = range(-len(rms_tab)//2, len(rms_tab)//2)
        plt.plot(idx_range, rms_tab, label='RMS')
        plt.plot(idx_range, cos_coef_tmp[:, 0]*100, label=r'Amplitude $\times 100$')
        plt.plot(idx_range, -cos_coef_tmp[:, 1]*1000/(2*pi), label=r'Phase $\times (-1000 / 2\pi)$')
        plt.legend(loc='best',fancybox=True, frameon=True)
        plt.ylabel('RMS')
        plt.xlabel('Distance from chosen one (in indexes), chosen one is {}'
                   .format(i_best))
        plt.grid()

        plt.subplot(212)
        plt.title('2- Find kick')
        plt.plot(interval_rel,
                 abs(b*cos(interval + c) - b*cos(interval+c+2*pi*tune)))
        tick_vals = []
        tick_labels = []
        amp_max = int(offset // pi)
        for x in range(-amp_max, amp_max+1):
            if x == 0:
                tick_labels.append('0')
                tick_vals.append(0)
            elif x == 1:
                tick_labels.append(r'$\pi$')
                tick_vals.append(pi)
            elif x == -1:
                tick_labels.append(r'$-\pi$')
                tick_vals.append(-pi)
            else:
                tick_labels.append(r'$'+str(x)+'\pi$')
                tick_vals.append(x*pi)

        plt.xticks(tick_vals, tick_labels)
        plt.ylabel('Size of curve jump')
        plt.xlabel('Position of kick (relative to initial one) ')
        plt.tight_layout()

    if plot:
        plt.figure('skcore::get_kick -- Orbit plot [{}]'
                   .format(len(plt.get_fignums())))
        plt.plot(phase/(2*pi), orbit, '.',  ms=10, label='Real orbit')
        sine_signal, phase_th = build_sine(kick_phase,
                                           tune,
                                           cos_coefficients[i_best % bpm_nb]
                                           )
        plt.plot(phase_th/(2*pi), sine_signal, label='Reconstructed sine')
        plt.axvline(kick_phase/(2*pi), -2, 2, color='red', label='Kick position')
        plt.xlabel(r'phase / $2 \pi$')
        plt.legend(fancybox=True, frameon=True)
    return kick_phase, cos_coefficients[i_best % bpm_nb]
