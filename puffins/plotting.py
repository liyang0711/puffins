#! /usr/bin/env python
"""Helper functions for creating plots."""

from collections import namedtuple

from faceted import faceted
from matplotlib import pyplot as plt
import numpy as np

from .names import LAT_STR
from .nb_utils import sindeg

_DEGR = r'$^\circ$'
_DEGR_S = _DEGR + 'S'
_DEGR_N = _DEGR + 'N'


def _left_bottom_spines_only(ax, displace=False):
    """Don't plot top or right border."""
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if displace:
        ax.spines['left'].set_position(('outward', 20))
        ax.spines['bottom'].set_position(('outward', 20))
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')


def sinlat_xaxis(ax, start_lat=0, end_lat=90):
    """Make the x-axis be in sin of latitude."""
    ax.set_xlim([sindeg(start_lat), sindeg(end_lat)])
    ax.set_xticks(sindeg(np.arange(start_lat, end_lat + 1, 10)))
    if start_lat == 0 and end_lat == 90:
        ax.set_xticklabels(['EQ', '', '', r'30$^\circ$', '', '',
                            r'60$^\circ$', '', '', r'90$^\circ$'])
    elif start_lat == -90 and end_lat == 90:
        ax.set_xticklabels(['90' + _DEGR_S, '', '', '', '', '', '30' + _DEGR_S,
                            '', '', 'EQ', '', '', '30' + _DEGR_N, '', '', '',
                            '', '', '90' + _DEGR_N])


def lat_xaxis(ax, start_lat=-90, end_lat=90):
    """Make the x-axis be in sin of latitude."""
    ax.set_xlim([start_lat, end_lat])
    ax.set_xticks(np.arange(start_lat, end_lat + 1, 10))
    if start_lat == 0 and end_lat == 90:
        ax.set_xticklabels(['EQ', '', '', '30' + _DEGR, '', '',
                            '60' + _DEGR, '', '', '90' + _DEGR])
    elif start_lat == -90 and end_lat == 90:
        ax.set_xticklabels(['-90' + _DEGR, '', '', '-60' + _DEGR, '', '',
                            '-30' + _DEGR, '', '', 'EQ', '', '', '30' + _DEGR,
                            '', '', '60' + _DEGR, '', '', '90' + _DEGR])
    ax.set_xlabel(" ")


def lat_yaxis(ax, start_lat=-90, end_lat=90):
    """Make the y-axis be in sin of latitude."""
    ax.set_ylim([start_lat, end_lat])
    ax.set_yticks(np.arange(start_lat, end_lat + 1, 10))
    if start_lat == 0 and end_lat == 90:
        ax.set_yticklabels(['EQ', '', '', '30' + _DEGR, '', '',
                            '60' + _DEGR, '', '', '90' + _DEGR])
    elif start_lat == -90 and end_lat == 90:
        ax.set_yticklabels(['-90' + _DEGR, '', '', '-60' + _DEGR, '', '',
                            '-30' + _DEGR, '', '', 'EQ', '', '', '30' + _DEGR,
                            '', '', '60' + _DEGR, '', '', '90' + _DEGR])
    ax.set_ylabel(" ")


def facet_ax(width=4, cbar_mode=None, **kwargs):
    """Use faceted to create single panel figure."""
    if cbar_mode is None:
        fig, axarr = faceted(1, 1, width=width, **kwargs)
        return fig, axarr[0]
    else:
        fig, axarr, cax = faceted(1, 1, width=width,
                                  cbar_mode=cbar_mode, **kwargs)
        return fig, axarr[0], cax


def plot_lat_1d(arr, start_lat=-90, end_lat=90, sinlat=False,
                ax=None, lat_str=LAT_STR, ax_labels=False, **plot_kwargs):
    """Plot of the given array as a function of latitude."""
    arr_plot = arr.where((arr[lat_str] > start_lat) &
                         (arr[lat_str] < end_lat))
    if ax is None:
        ax = plt.gca()
    if sinlat:
        lat = sindeg(arr_plot[lat_str])
        sinlat_xaxis(ax, start_lat=start_lat, end_lat=end_lat)
    else:
        lat = arr_plot[lat_str]
        lat_xaxis(ax, start_lat=start_lat, end_lat=end_lat)

    handle = ax.plot(lat, arr_plot, **plot_kwargs)[0]

    _left_bottom_spines_only(ax, displace=False)

    if ax_labels:
        ax.set_xlabel(r'Latitude [$^\circ$]')
        if arr.name:
            ax.set_ylabel(arr.name)

    return handle


def _plot_cutoff_ends(lats, arr, ax=None, **kwargs):
    """Avoid finite-differencing artifacts at endpoints."""
    if ax is None:
        ax = plt.gca()
    ax.plot(lats[2:-2], arr[2:-2], **kwargs)


def panel_label(ax, panel_num, x=0.03, y=0.95, extra_text=None,
                **text_kwargs):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    label = '({})'.format(letters[panel_num])
    if extra_text is not None:
        label += ' {}'.format(extra_text)
    ax.text(x, y, label, transform=ax.transAxes, **text_kwargs)


PlotArr = namedtuple('PlotArr', ['func', 'label', 'plot_kwargs'])

if __name__ == '__main__':
    pass
