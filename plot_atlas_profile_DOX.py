#!/usr/bin/python3

# raw2netCDF
# Copyright (C) 2019 Peter Jansen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import matplotlib.markers
from netCDF4 import Dataset, num2date
import sys
import numpy as np
import oceansdb
import datetime
import matplotlib.pyplot as plt

def get_data():
    base = datetime.datetime(2000, 1, 1)
    date_list = [base + datetime.timedelta(days=x*30) for x in range(12)]

    doy = [(x - datetime.datetime(x.year, 1, 1)).total_seconds()/3600/24 for x in date_list]
    depth = np.arange(0.5, 5000, 10) # WOA only goes to 2000m (?), WOA-18 goes to full ocean, need to check oceansdb


    #print (depth)

    db = oceansdb.WOA(dbname='WOA18')

    o_std = np.zeros([len(doy), len(depth)])
    o_mean = np.zeros([len(doy), len(depth)])
    o_dd = np.zeros([len(doy), len(depth)])
    o_se = np.zeros([len(doy), len(depth)])


    i = 0
    for doy in date_list:
        o = db['dissolved_oxygen'].extract(doy=doy, depth=depth, lat=-47, lon=142.5)

        #print(o)
        o_mean[i][:] = o['o_mn']
        o_std[i][:] = o['o_sd']
        o_dd[i][:] = o['o_dd']
        o_se[i][:] = o['o_se']

        i += 1
    return o_mean, o_std, depth #o_dd, o_se,

def plot():
    o_mean, o_std, depth = get_data()
    msk = o_mean>1000
    o_mean[o_mean>1000] = np.nan
    o_std[o_std>1000] = np.nan

    #fig = plt.figure()
    plt.plot(np.max(o_mean, axis=0) + 3*np.max(o_std, axis=0), depth, linewidth=4,
         linestyle=(0, (5, 2, 1, 2)), dash_capstyle='round', color='b')
    plt.plot(np.min(o_mean, axis=0) - 3*np.max(o_std, axis=0), depth, linewidth=4,
         linestyle=(0, (5, 2, 1, 2)), dash_capstyle='round',color = 'r')
    #plt.gca().set_ylabel('Depth')
    #plt.gca().set_xlabel('Dissolved oxygen uM/kg')
    #leg = ['Maximum mean + 3 * STD', 'Minimum mean - 3 * STD']
    #plt.legend(leg, loc='best', fontsize='x-small')
    #plt.gca().invert_yaxis()
    #plt.show()


def plot_mean():
    o_mean, o_std, depth = get_data()
    msk = o_mean > 1000
    o_mean[o_mean > 1000] = np.nan
    o_std[o_std > 1000] = np.nan

    fig = plt.figure()
    ax1 = fig.add_axes([0.15, 0.6, 0.7, 0.4])
    ax2 = fig.add_axes([0.15, 0.1, 0.7, 0.4])

    ax1.plot(np.max(o_mean, axis=0), depth)
    ax1.set_xlabel('Max mean dissolved oxygen uM/kg')
    ax1.set_ylabel('Depth')
    ax1.invert_yaxis()
    ax1.grid(True)

    ax2.plot(np.min(o_mean, axis=0), depth)
    ax2.set_xlabel('Min mean dissolved oxygen uM/kg')
    ax2.set_ylabel('Depth')
    ax2.invert_yaxis()
    ax2.grid(True)

    # ax2.plot(np.mean(o_mean, axis=0), depth)
    # ax2.set_xlabel('Mean dissolved oxygen uM/kg')
    # ax2.set_ylabel('Depth')
    # ax2.invert_yaxis()


if __name__ == "__main__":
    fig = plt.figure()
    plot()

    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.show()
