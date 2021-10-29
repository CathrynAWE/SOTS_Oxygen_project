# For the purpose of QC of the oxygen data find the min and max (climatology) of all existing measurements
# starting with CTD measurements
# then all mooring measurements

import pandas as pd
import os
from netCDF4 import Dataset
import datetime as dt
import matplotlib.pyplot as plt
from netCDF4 import num2date
import numpy as np


# all the sensor data is located in
sensor_folder = 'C:/Users/cawynn/cloudstor/Shared/sots-Oxygen'

# compile all the necessary files
files = [os.path.join(root, name) for root, dirs, files in os.walk(sensor_folder) for name in files if name.endswith(('.nc'))]

print(files)

# dissolved oxygen umol/kg (dox2)
data_dox2 = []
for i in files:
    OX = Dataset(i, mode='r', format='NETCDF4')
    if 'deployment_code' in OX.ncattrs():
        deployment = OX.getncattr('deployment_code')
    else:
        sp = i.split('\\')
        deployment = sp[1]
# limit the data to only 'in-water' data points
    try:
        date_time_start = dt.datetime.strptime(OX.getncattr('time_deployment_start'), '%Y-%m-%dT%H:%M:%SZ')
        date_time_end = dt.datetime.strptime(OX.getncattr('time_deployment_end'), '%Y-%m-%dT%H:%M:%SZ')

    except AttributeError:

        try:
            date_time_start = dt.datetime.strptime(OX.getncattr('time_coverage_start'), '%Y-%m-%dT%H:%M:%SZ')
            date_time_end = dt.datetime.strptime(OX.getncattr('time_coverage_end'), '%Y-%m-%dT%H:%M:%SZ')
        except AttributeError:
            pass

    # get time variable
    nctime = OX.variables['TIME'][:]
    t_unit = OX.variables['TIME'].units  # get unit  "days since 1950-01-01T00:00:00Z"

    try:
        t_cal = OX.variables['TIME'].calendar
    except AttributeError:  # Attribute doesn't exist
        t_cal = u"gregorian"  # or standard

    dt_t = [num2date(t, units=t_unit, calendar=t_cal, only_use_cftime_datetimes=False) for t in nctime]
    dt_time = pd.DataFrame(dt_t)

    d_time_start = pd.DataFrame([], index=np.arange(len(dt_time)))
    d_time_start[0] = date_time_start
    d_time_end = pd.DataFrame([], index=np.arange(len(dt_time)))
    d_time_end[0] = date_time_end

    if 'DOX2' in OX.variables:
        DOX2 = OX.variables['DOX2']
        if DOX2.ndim == 1:
            msk = dt_time > d_time_start & dt_time < d_time_end
            DOX2 = OX.variables['DOX2'][msk]
            instrument = OX.getncattr('instrument')
            data_dox2.append([deployment, instrument, DOX2.min(), DOX2.max()])
        else:
            if DOX2.shape[0] > 10:
                for l in range(DOX2.shape[1]):
                    DOX2 = OX.variables['DOX2'][:, l]
                    ins = OX.variables['DOX2'].getncattr('sensor_name').split(';')
                    instrument = ins[l]
                    data_dox2.append([deployment, instrument, DOX2.min(), DOX2.max()])
            else:
                for l in range(DOX2.shape[0]):
                    DOX2 = OX.variables['DOX2'][l, :]
                    ins = OX.variables['DOX2'].getncattr('sensor_name').split(';')
                    instrument = ins[l]
                    data_dox2.append([deployment, instrument, DOX2.min(), DOX2.max()])

    else:
        data_dox2 = data_dox2

for i in files:
    OX = Dataset(i, mode='r', format='NETCDF4')
    if 'deployment_code' in OX.ncattrs():
        deployment = OX.getncattr('deployment_code')
    else:
        sp = i.split('\\')
        deployment = sp[1]
    if 'DOX2_1' in OX.variables:
        DOX2 = OX.variables['DOX2_1'][:]
        instrument = OX.variables['DOX2_1'].getncattr('sensor_name')
        data_dox2.append([deployment, instrument, DOX2.min(), DOX2.max()])
    elif 'DOX2_2' in OX.variables:
        DOX2 = OX.variables['DOX2_2'][:]
        instrument = OX.variables['DOX2_2'].getncattr('sensor_name')
        data_dox2.append([deployment, instrument, DOX2.min(), DOX2.max()])


# add this into a panda frame for later
column_names = ['mooring', 'instrument', 'DOX2_min', 'DOX2_max']
climatology_sensors_DOX2 = pd.DataFrame(data_dox2, columns=column_names)


# oxygen saturation

data_doxs = []
for i in files:
    OX = Dataset(i, mode='r', format='NETCDF4')
    if 'deployment_code' in OX.ncattrs():
        deployment = OX.getncattr('deployment_code')
    else:
        sp = i.split('\\')
        deployment = sp[1]
    if 'DOXS' in OX.variables:
        DOXS = OX.variables['DOXS']
        if DOXS.ndim == 1:
            DOXS = OX.variables['DOXS'][:]
            instrument = OX.getncattr('instrument')
            data_doxs.append([deployment, instrument, DOXS.min(), DOXS.max()])
        else:
            if DOX2.shape[0] > 10:
                for l in range(DOXS.shape[1]):
                    DOXS = OX.variables['DOXS'][:, l]
                    ins = OX.variables['DOXS'].getncattr('sensor_name').split(';')
                    instrument = ins[l]
                    data_doxs.append([deployment, instrument, DOXS.min(), DOXS.max()])
            else:
                for l in range(DOX2.shape[0]):
                    DOXS = OX.variables['DOXS'][l, :]
                    ins = OX.variables['DOXS'].getncattr('sensor_name').split(';')
                    instrument = ins[l]
                    data_doxs.append([deployment, instrument, DOXS.min(), DOXS.max()])

    else:
        data_doxs = data_doxs


# add this into a panda frame for later

column_names = ['mooring', 'instrument', 'DOXS_min', 'DOXS_max']
climatology_sensors_DOXS = pd.DataFrame(data_doxs, columns=column_names)


#climatology_mooring = pd.merge(cl_mooring_dox2, cl_mooring_doxs, on='deployment')

# print the results
mooring_DOX2min = climatology_sensors_DOXS.DOXS_min.min()
print('Mooring DOX2 minimum', mooring_DOX2min)

mooring_DOX2max = climatology_sensors_DOXS.DOXS_max.max()
print('Mooring DOX2 maximum', mooring_DOX2max)


mooring_DOXSmin = climatology_sensors_DOXS.DOXS_min.min()
print('Mooring DOXS (Oxygen sat) minimum', mooring_DOXSmin)

mooring_DOXSmax = climatology_sensors_DOXS.DOXS_max.max()
print('Mooring DOXS (Oxygen sat) maximum', mooring_DOXSmax)