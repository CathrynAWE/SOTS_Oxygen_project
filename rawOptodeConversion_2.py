from netCDF4 import Dataset
import numpy as np
from scipy import interpolate
from shutil import copyfile
import shutil as shutil
import os
import gsw
from datetime import datetime

def rawOptodeConversion(filepath, mooring):

    location = filepath

    mooring_name = ['SOFS-9-2020', 'SOFS-8-2019', 'SOFS-7.5-2018', 'SOFS-7-2018', 'SOFS-6-2017', 'SOFS-5-2015',
                    'SOFS-4-2013', 'SOFS-3-2012', 'SOFS-2-2011', 'SOFS-1-2010', 'FluxPulse-1-2016', 'Pulse-11-2015',
                    'Pulse-10-2013', 'Pulse-9-2012', 'Pulse-8-2011', 'Pulse-7-2010', 'Pulse-6-2009']
    # mooring_name= ['Pulse-11-2015', 'Pulse-10-2013', 'Pulse-9-2012', 'Pulse-8-2011', 'Pulse-7-2010', 'Pulse-6-2009']
    if mooring == 'all':
        mooring_name = mooring_name
    else:
        mooring_name = []
        mooring_name += [mooring]

    # Define the folder path
    #location = 'C:/Users/cawynn/cloudstor/Shared/sots-Oxygen'
    #location = 'C:/Users/cawynn/OneDrive - University of Tasmania/Documents/GitHub/SOTS_Oxygen project'

    # for SOFS moorings the Temp and salinity data comes from a SBE file (for Pulse it is part of the raw optode file)
    for m in mooring_name:
        print(m)
        # create the calibration coefficient filename
        calfolder = location + '/' + str(m) + '/optode/cal'
        fncal=[]
        for i in os.listdir(calfolder):
           fncal = calfolder + '/' + i

        # create the SBE filename (for SOFS moorings only)
        fnSBE = []
        try:
            SBEfolder = location + '/' + str(m) + '/optode/SBE'
            for i in os.listdir(SBEfolder):
                fnSBE = SBEfolder + '/' + i
        except FileNotFoundError:
            print('No SBE file found')

        # create the Optode raw file filename
        fnOx = []
        Optodefolder = location + '/' + str(m) + '/optode/raw_data'
        for i in os.listdir(Optodefolder):
            if i.endswith('.nc'):
                fnOx = Optodefolder + '/' + i


        # create filename for combined file
        fnOXprocessed = m + '-OptodeLine-processed.nc'

        # copy oxygen file for easier debugging
        copyfile(fnOx, fnOXprocessed)
        OX = Dataset(fnOXprocessed, mode='a', format='NETCDF4')

        # see if the raw Optode file already has TEMP and SAL variables in it (true for Pulse moorings)
        try:
            temp = OX.variables['TEMP']
            psal = OX.variables['PSAL']
        # if not fetch them from the SBE file
        except KeyError:
            SBE = Dataset(fnSBE, 'r', format='NETCDF4')

            time_var = SBE.variables['TIME']
            sample_time = OX.variables['TIME']

            # copy required variables from SBE file to newly created Oxygen file
            set1 = ['TEMP', 'CNDC', 'PSAL']

            # add SBE sensor model and serial number to the SBE variables. The final file will have the Optode instrument information
            # contained in the global attribute, and the SBE instrument information attached to the SBE variables as variable attribute
            SBE_instrument = SBE.getncattr('instrument')
            #SBE_instrument_model = SBE.getncattr('instrument_model')
            SBE_instrument_serial_number = SBE.getncattr('instrument_serial_number')

            for v in set1:
                #print(v)
                new_var = OX.createVariable('SBE_'+v, SBE.variables[v].dtype, fill_value=SBE.variables[v]._FillValue, dimensions=SBE.variables[v].dimensions, zlib=True)
                new_var.setncattr('instrument', SBE_instrument)
                #new_var.setncattr('instrument_model', SBE_instrument_model)
                new_var.setncattr('instrument_serial_number', SBE_instrument_serial_number)
                new_varQC = OX.createVariable('SBE_'+v+'_quality_control', SBE.variables[v + '_quality_control'].dtype, fill_value=SBE.variables[v + '_quality_control']._FillValue, dimensions=SBE.variables[v +'_quality_control'].dimensions, zlib=True)
                for va in SBE.variables[v].ncattrs():
                    #print(va)
                    if va != '_FillValue':
                        new_var.setncattr(va, SBE.variables[v].getncattr(va))
                var = SBE.variables[v]
                var_QC = SBE.variables[v+'_quality_control']
                msk = var_QC[:]<3
                f = interpolate.interp1d(time_var[msk], var[msk], kind='nearest', bounds_error=False, fill_value=np.nan)
                new_var[:] = f(np.array(sample_time[:]))
                fQC = interpolate.interp1d(time_var[msk], var_QC[msk], kind='nearest', bounds_error=False, fill_value=9)

                new_varQC[:] = fQC(np.array(sample_time[:]))
                #print(new_var[:])
            temp = OX.variables['SBE_TEMP']
            psal = OX.variables['SBE_PSAL']

    # see if BPHASE is in the raw Optode file or already converted raw DOX
        try:
            bphase = OX.variables['BPHASE'][:]
            # BPHASE needs conversion to raw_dox
            # open text file with calibration coefficients for oxygen sensor
            cal = []
            with open(fncal, 'r') as f:
                cal = f.read().splitlines()

            # add calibration coefficients to BPHASE variable along with the name of the file where the coefficients came from
            OX.variables['BPHASE'].calcoefC0 = float(cal[0])
            OX.variables['BPHASE'].calcoefC1 = float(cal[1])
            OX.variables['BPHASE'].calcoefC2 = float(cal[2])
            OX.variables['BPHASE'].calcoefA0 = float(cal[3])
            OX.variables['BPHASE'].calcoefA1 = float(cal[4])
            OX.variables['BPHASE'].calcoefB0 = float(cal[5])
            OX.variables['BPHASE'].calcoefB1 = float(cal[6])
            split = fncal.split('/')
            OX.variables['BPHASE'].calfilename = split[-1]

            # convert bphase to raw dissolved oxygen
            dox_raw = ((float(cal[3]) + float(cal[4]) * OX.variables['OTEMP'][:]) / (float(cal[5]) + float(cal[6]) * OX.variables['BPHASE'][:]) - 1) / (float(cal[0]) + float(cal[1]) * OX.variables['OTEMP'][:] + float(cal[2]) * OX.variables['OTEMP'][:] * OX.variables['OTEMP'][:])
        except KeyError:
            dox_raw = OX.variables['DOX2_RAW'][:]


        if 'PRES' in OX.variables:
            var_pres = OX.variables["PRES"]
            pres = var_pres[:]
        elif 'NOMINAL_DEPTH' in OX.variables:
            var_nd = OX.variables["NOMINAL_DEPTH"]
            pres = var_nd[:]
        elif 'NOMINAL_DEPTH' in SBE.variables:
            var_nd = SBE.variables["NOMINAL_DEPTH"]
            pres = var_nd[:]
        else:
            print("no pressure variable, or nominal depth")


       # salinity correction of raw dox2
        B0 = -6.24097e-3
        B1 = -6.93498e-3
        B2 = -6.90358e-3
        B3 = -4.29155e-3
        C0 = -3.11680e-7

        temp_scaled = np.log((298.15 - OX.variables['OTEMP'][:])/(273.15 + OX.variables['OTEMP'][:]))

        dox_salCorrected = dox_raw * np.exp(psal[:] * (B0 + B1*temp_scaled + B2*np.power(temp_scaled, 2) + B3*np.power(temp_scaled, 3)) + C0*np.power(psal[:], 2))

        # pressure correction
        dox2 = dox_salCorrected * (1 + ((0.032 * pres)/1000))

        ncVarOut = OX.createVariable("DOX2", "f4", ("TIME",), fill_value=np.nan, zlib=True)  # fill_value=nan otherwise defaults to max
        ncVarOut[:] = dox2
        ncVarOut.units = "umol/kg"

        # calculate dissolved oxygen concentration using GSW

        try:
            lon = OX.geospatial_lon_max
            lat = OX.geospatial_lat_max
        except AttributeError:
            lon = 142
            lat = -47

        SA = gsw.SA_from_SP(psal[:], pres, lon, lat)
        pt = gsw.pt0_from_t(SA, temp[:], pres)
        oxsol = gsw.O2sol_SP_pt(psal[:], pt)

        ncVarOut = OX.createVariable("OXSOL", "f4", ("TIME",), fill_value=np.nan, zlib=True)  # fill_value=nan otherwise defaults to max
        ncVarOut[:] = oxsol
        ncVarOut.units = "umol/kg"
        ncVarOut.comment = "calculated using gsw-python https://teos-10.github.io/GSW-Python/index.html function gsw.O2sol_SP_pt"

        # oxygen saturation
        doxs = dox2/oxsol
        ncVarOut = OX.createVariable("DOXS", "f4", ("TIME",), fill_value=np.nan, zlib=True)  # fill_value=nan otherwise defaults to max
        ncVarOut[:] = doxs
        ncVarOut.units = '1'

        # quality control flags for oxygen parameters
        QC_list = ["TEMP_quality_control", "SBE_TEMP_quality_control"]
        var_list = set(OX.variables)

        for i in QC_list:
            if(i in var_list):
                ncVarOut = OX.createVariable("OXSOL_quality_control", "i1", ("TIME",), fill_value=128, zlib=True)
                ncVarOut[:] = OX.variables[i][:]
                ncVarOut.comment = 'Quality control flag is carried over from SBE Temperature variable'

                ncVarOut = OX.createVariable("DOX2_quality_control", "i1", ("TIME",), fill_value=128, zlib=True)
                ncVarOut[:] = OX.variables[i][:]
                ncVarOut.comment = 'Quality control flag is carried over from SBE Temperature variable'

                ncVarOut = OX.createVariable("DOXS_quality_control", "i1", ("TIME",), fill_value=128, zlib=True)
                ncVarOut[:] = OX.variables[i][:]
                ncVarOut.comment = 'Quality control flag is carried over from SBE Temperature variable'

    # update the history to reflect which, if any, files were combined here
        try:
            #SBEfolder = location + '/' + m + '/optode/SBE'
            split_1 = fnOx.split('/')
            split_2 = fnSBE.split('/')
            history = OX.getncattr('history') + '\n' + datetime.utcnow().strftime("%Y-%m-%d") \
                      + ' added TEMP, CNDC, PSAL and associated quality control flags from ' + split_2[-1]
        #add in deployment start and end date so that plots can be limited to that timeline
            time_deployment_start = SBE.getncattr('time_deployment_start')
            time_deployment_end = SBE.getncattr('time_deployment_end')
            OX.setncattr('time_deployment_start', time_deployment_start)
            OX.setncattr('time_deployment_end', time_deployment_end)
            ncTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
            OX.setncattr('date_created', datetime.utcnow().strftime(ncTimeFormat))

        except AttributeError:
            print('No SBE file found')
            history = OX.getncattr('history') + '\n' + datetime.utcnow().strftime("%Y-%m-%d") \
                      + ' added DOX2 and DOXS variables'
            OX.setncattr('history', history)

        # close all files
        OX.close()
        try:
            SBE.close()
        except RuntimeError:
            print('no SBE file open')


        # move the newly created netCDF file with SBE, oxygen data and newly created variables to the respective mooring folder
        # outputFolder = location + '/' + m + '/optode/netCDF'
        # source = os.path.join(os.getcwd(), fnOXprocessed)
        #
        # shutil.copy(source, outputFolder)

if __name__ == "__main__":
    filepath = input('enter filepath')
    mooring = input('enter mooring deployment code or all for all moorings')
    rawOptodeConversion(filepath, mooring)
