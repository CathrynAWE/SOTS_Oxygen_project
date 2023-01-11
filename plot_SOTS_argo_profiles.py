# this script will plot argo profiles from csv files "SOTS_argo_files.csv" (from Matlab scrtip SOTS_O2_argoprofiles.m)

import os
from netCDF4 import Dataset, chartostring
import matplotlib.pyplot as plt

dirName = 'C:/Users/cawynn/OneDrive - University of Tasmania/Documents/GitHub/SOTS_Oxygen project/argo/data/profiles3'
def get_data_filenames():
    files_to_plot = [os.path.join(root, name)
                     for root, dirs, files in os.walk(dirName)
                     for name in files
                     if name.endswith('.nc')]

    return files_to_plot

def plot_argo():

    files_to_plot = get_data_filenames()
    for f in files_to_plot:

        print(f)
        nc = Dataset(f)
        try:
            var = nc.variables['DOXY_ADJUSTED'][0,:]
            #var_qc = chartostring(nc.variables['DOXY_ADJUSTED_QC'][0,:])
            depth = nc.variables['PRES_ADJUSTED'][0,:]

            plt.plot(var, depth, marker = ',', color = 'y')
            nc.close()
        except:
            pass
    axes = plt.gca()
    xlimits = axes.get_xlim()
    return xlimits



if __name__ == "__main__":
    fig = plt.figure()
    plot_argo()
    plt.show()



