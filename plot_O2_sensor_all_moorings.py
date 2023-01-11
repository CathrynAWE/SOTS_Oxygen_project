from netCDF4 import Dataset
from netCDF4 import num2date
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt

def get_data():
    location = 'C:/Users/cawynn/cloudstor/Shared/sots-Oxygen (2) (2)'

    #mooring_name = ['SOFS-9-2020', 'SOFS-8-2019', 'SOFS-7.5-2018', 'SOFS-6-2017', 'SOFS-5-2015', 'SOFS-4-2013', 'FluxPulse-1-2016']
    mooring_name = ['SOFS-9-2020', 'SOFS-8-2019', 'SOFS-7.5-2018', 'SOFS-7-2018', 'SOFS-6-2017', 'SOFS-5-2015',
                    'SOFS-4-2013', 'SOFS-3-2012', 'SOFS-2-2011', 'SOFS-1-2010', 'FluxPulse-1-2016', 'Pulse-11-2015',
                    'Pulse-10-2013', 'Pulse-9-2012', 'Pulse-8-2011', 'Pulse-7-2010', 'Pulse-6-2009']

    #mooring_name = ['SOFS-9-2020']  # , 'SOFS-8-2019']

    files_to_plot = []
    for m in mooring_name:
        # create the list of files to plot, first add the optode files

        #files_to_plot = []
        folder = location + '/' + m + '/optode/netCDF'
        for i in os.listdir(folder):
            if i.endswith('.nc'):
                fn = folder + '/' + i
                files_to_plot += [fn]
                #print(i)

        # next add the SBE-ODO sensors for comparison to the list
        try:
            folder = location + '/' + m + '/SBE37-ODO'
            for i in os.listdir(folder):
                if i.endswith('.nc'):
                    fn = folder + '/' + i
                    files_to_plot += [fn]
                    #print(i)
        except FileNotFoundError:
            pass
    return files_to_plot

def plot_sensor_O2(depth_lim, plotvar):

    # create the figure to which to add all the sensors

    files_to_plot = get_data()

    for f in files_to_plot:
        print(f)
        nc = Dataset(f)

        # get time variable
        nctime = nc.variables['TIME'][:]
        t_unit = nc.variables['TIME'].units  # get unit  "days since 1950-01-01T00:00:00Z"

        try:
            t_cal = nc.variables['TIME'].calendar
        except AttributeError:  # Attribute doesn't exist
            t_cal = u"gregorian"  # or standard

        dt_time = [num2date(t, units=t_unit, calendar=t_cal, only_use_cftime_datetimes=False) for t in nctime]
        # dt_time = [num2date(t, units=t_unit, calendar=t_cal) for t in nctime]

        # different names were used for nominal depth
        var=[]
        if 'DOX2' in nc.variables:
            var = nc.variables['DOX2']
            if 'NOMINAL_DEPTH' in nc.variables:
                depth = nc.variables['NOMINAL_DEPTH'][:]

            elif 'DEPTH' in nc.variables:
                depth = nc.variables['DEPTH'][:]

            elif 'DEPTH_DOX2' in nc.variables:
                depth = nc.variables['DEPTH_DOX2'][:]

            # the netCDF files that have multiple sensors in one file have the depth as attribute in the sensor, I'm
            # just giving those the dummy depth = 0 for now so that the code proceeds.
            else:
                depth = int(0)
        elif 'DOX2_1' in nc.variables:
            varlist = ['DOX2_1', 'DOX2_2']
            # var = nc.variables['DOX2_1']
            # depth = nc.variables['DOX2_1'].getattr('sensor_depth')

        # show me where you are up to
        print('var is ', var)
        print('var dimension is ', var.ndim)
        print('sensor depth is', depth)
        print('var shape is ', var.shape)

        # change depth if desired
        if depth <= depth_lim:
            # the current format for netCDF files is, ONE file per sensor
            if var.datatype == 'float32':
                if var.ndim == 1:
                    if plotvar == 'time':
                        plt.plot(dt_time, var)

                    elif plotvar == 'depth':
                        plotDepth = np.full((var.size, 1), depth)
                        plt.plot(var, plotDepth, linewidth = 1)

                # for older netCDF files multiple sensor data was combined into one variable, with multiple dimensions (time and the
                # associated sensor depth)
                else:
                    sensor_depth = var.getncattr('sensor_depth')
                    if var.shape[0]>10:
                        if plotvar == 'time':
                            print(sensor_depth)
                            plt.plot(dt_time, var[:,0])
                        elif plotvar == 'depth':
                            plotDepth = np.full((var.size, 1), depth)
                            plt.plot(var, plotDepth, linewidth = 1)

                    elif var.shape[1]>10:
                        if plotvar == 'time':
                            print(sensor_depth)
                            plt.plot(dt_time, var[0,:], linewidth = 1)

                        elif plotvar == 'depth':
                            plotDepth = np.full((1, var.size), depth)
                            plt.plot(var, plotDepth, linewidth = 1)
            else:
                for i in range(0, varlist.__len__()):
                    var = nc.variables[i]
                    depth = nc.variables[i].getattr('sensor_depth')
                    if plotvar == 'time':
                        plt.plot(dt_time, var, linewidth = 1)

                    elif plotvar == 'depth':
                        plotDepth = np.full((var.size, 1), depth)
                        plt.plot(var, plotDepth, linewidth = 1)

        nc.close()


if __name__ == "__main__":
    fig = plt.figure()
   #leg = []
    depth_lim = int(input('depth limit'))
    plotvar = input('which y variable to plot? depth or time')
    plot_sensor_O2(depth_lim, plotvar)

    if plotvar == 'depth':
        plt.gca().invert_yaxis()
        plt.gca().set_yscale('log')
        plt.xlim([0, 800])
        plt.gca().set_xlabel('Dissolved oxygen in umol/kg')
        plt.gca().set_ylabel('Depth - log scale')
    else:
        plt.ylim([0, 400])
        plt.getca().set_xlabel('Time')
        plt.getca().set_ylabel('Dissolved oxygen in umol/kg')


    plt.grid(True)
    plt.show()

