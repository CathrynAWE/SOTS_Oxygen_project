# For the purpose of QC of the oxygen data find the min and max (climatology) of all existing measurements
# starting with CTD measurements

import pandas as pd
import os
import gsw
from netCDF4 import Dataset
import datetime as dt
import matplotlib.pyplot as plt
from netCDF4 import num2date
import numpy as np

# all CTD data is located in
def get_data():
    CTD_folder = 'C:/Users/cawynn/cloudstor/Shared/CTD/CTD'

    # compile all the necessary files
    files = []
    for i in os.listdir(CTD_folder):
        if i.endswith('.csv'):
            filename = [CTD_folder + '/' + i]
            files += filename
    print(files)
    return files

# the oxygen data is presented as umol/L in the CTD csv files
# need to convert to umol/kg
def plot_allCTD():

    files = get_data()
    data = []
    fig1, ax1 = plt.subplots(figsize=(11.69, 8.27))
    leg=[]
    for i in files:
        CTD_data = pd.read_csv(i)
        SA = gsw.SA_from_SP(CTD_data.SALINITY, CTD_data.PRESSURE, CTD_data.START_LON, CTD_data.START_LAT)
        CT = gsw.CT_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        pt = gsw.pt0_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        sigma0 = gsw.sigma0(SA, CT)
        O2_umol_kg = (CTD_data.OXYGEN / (sigma0 + 1000))*1000
        oxsol = gsw.O2sol_SP_pt(CTD_data.SALINITY, pt)
        doxs = O2_umol_kg / oxsol
        data.append([CTD_data.SURVEY_NAME[0], CTD_data.STATION[0], O2_umol_kg.min(), O2_umol_kg.max()])

        # plot the climatology of CTD data
        leg += [CTD_data.SURVEY_NAME[0] + '_' + str(CTD_data.STATION[0])]
        ax1.scatter(O2_umol_kg, CTD_data.PRESSURE, s=2)
        ax1.invert_yaxis()
        ax1.set_yscale('log')
        ax1.set_xlabel('Oxygen umol/kg')
        ax1.set_ylabel('Pressure - log scale')
        #ax.legend(leg, loc='best', fontsize='x-small')  # bbox_to_anchor=(0.5, -0.2),
        ax1.set_title('CTD data - converted to umol/kg')
        plt.tight_layout()
        #figurename = 'CTD_oxygen_data_umol_kg.png'
        #plt.savefig(figurename)
        #plt.show()
    return data


def plot_goodCTD(plotvar):
    files = get_data()
    data = []
    #fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
    leg = []
    for i in files:
        CTD_data = pd.read_csv(i)
        SA = gsw.SA_from_SP(CTD_data.SALINITY, CTD_data.PRESSURE, CTD_data.START_LON, CTD_data.START_LAT)
        CT = gsw.CT_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        pt = gsw.pt0_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        sigma0 = gsw.sigma0(SA, CT)
        O2_umol_kg = (CTD_data.OXYGEN / (sigma0 + 1000)) * 1000
        oxsol = gsw.O2sol_SP_pt(CTD_data.SALINITY, pt)
        doxs = O2_umol_kg / oxsol
        data.append([CTD_data.SURVEY_NAME[0], CTD_data.STATION[0], O2_umol_kg.min(), O2_umol_kg.max()])

        # same again, this time limited to casts with >150 and <325 umol/kg data
        lower_bound = 150
        upper_bound = 325
        if plotvar == 'DOX2':
            if O2_umol_kg.min() > lower_bound and O2_umol_kg.max() < upper_bound:
                plt.scatter(O2_umol_kg, CTD_data.PRESSURE, s=2)
                leg += [CTD_data.SURVEY_NAME[0] + '_' + str(CTD_data.STATION[0])]
        else:
            if O2_umol_kg.min() > lower_bound and O2_umol_kg.max() < upper_bound:
                plt.scatter(doxs, CTD_data.PRESSURE, s=2)
                leg += [CTD_data.SURVEY_NAME[0] + '_' + str(CTD_data.STATION[0])]
    return data

def plot_goodCTD_upper():
    files = get_data()
    data = []
    fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
    leg = []
    for i in files:
        CTD_data = pd.read_csv(i)
        SA = gsw.SA_from_SP(CTD_data.SALINITY, CTD_data.PRESSURE, CTD_data.START_LON, CTD_data.START_LAT)
        CT = gsw.CT_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        pt = gsw.pt0_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        sigma0 = gsw.sigma0(SA, CT)
        O2_umol_kg = (CTD_data.OXYGEN / (sigma0 + 1000)) * 1000
        oxsol = gsw.O2sol_SP_pt(CTD_data.SALINITY, pt)
        doxs = O2_umol_kg / oxsol
        data.append([CTD_data.SURVEY_NAME[0], CTD_data.STATION[0], O2_umol_kg.min(), O2_umol_kg.max()])

        # same again, this time limited to casts with >150 and <325 umol/kg data

        lower_bound = 150
        upper_bound = 325
        bend = 600
        msk = CTD_data.PRESSURE[:]<bend
        CTD_data = pd.read_csv(i)
        if O2_umol_kg.min()>lower_bound and O2_umol_kg.max()<upper_bound:
            leg += [CTD_data.SURVEY_NAME[0] + '_' + str(CTD_data.STATION[0])]
            ax3.scatter(O2_umol_kg[msk], CTD_data.PRESSURE[msk], s=2)
            ax3.invert_yaxis()
            ax3.set_yscale('log')
            ax3.set_xlabel('Oxygen umol/kg')
            ax3.set_ylabel('Pressure - log scale')
            #ax3.legend(leg, loc='best', fontsize='x-small')  # bbox_to_anchor=(0.5, -0.2),
            ax3.set_title('CTD data - converted to umol/kg upper '+ str(bend) + 'm')
            plt.tight_layout()
            #figurename = 'CTD_oxygen_data_umol_kg_good_data.png'
            #plt.savefig(figurename)
            #plt.show()
    return data

def plot_goodCTD_lower():
    files = get_data()
    data = []
    fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
    leg = []
    for i in files:
        CTD_data = pd.read_csv(i)
        SA = gsw.SA_from_SP(CTD_data.SALINITY, CTD_data.PRESSURE, CTD_data.START_LON, CTD_data.START_LAT)
        CT = gsw.CT_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        pt = gsw.pt0_from_t(SA, CTD_data.TEMPERATURE, CTD_data.PRESSURE)
        sigma0 = gsw.sigma0(SA, CT)
        O2_umol_kg = (CTD_data.OXYGEN / (sigma0 + 1000)) * 1000
        oxsol = gsw.O2sol_SP_pt(CTD_data.SALINITY, pt)
        doxs = O2_umol_kg / oxsol

        data.append([CTD_data.SURVEY_NAME[0], CTD_data.STATION[0], O2_umol_kg.min(), O2_umol_kg.max()])

        # same again, this time limited to casts with >150 and <325 umol/kg data

        lower_bound = 150
        upper_bound = 325
        bend = 600
        msk = CTD_data.PRESSURE[:]>=bend
        CTD_data = pd.read_csv(i)
        if O2_umol_kg.min()>lower_bound and O2_umol_kg.max()<upper_bound:
            leg += [CTD_data.SURVEY_NAME[0] + '_' + str(CTD_data.STATION[0])]
            ax3.scatter(O2_umol_kg[msk], CTD_data.PRESSURE[msk], s=2)
            ax3.invert_yaxis()
            ax3.set_yscale('log')
            ax3.set_xlabel('Oxygen umol/kg')
            ax3.set_ylabel('Pressure - log scale')
            #ax3.legend(leg, loc='best', fontsize='x-small')  # bbox_to_anchor=(0.5, -0.2),
            ax3.set_title('CTD data - converted to umol/kg below ' + str(bend) + 'm')
            plt.tight_layout()
            #figurename = 'CTD_oxygen_data_umol_kg_good_data.png'
            #plt.savefig(figurename)
            #plt.show()
    return data

def store_data():
    data = get_data()
    # add this into a panda frame for later
    column_names = ['voyage', 'station', 'min_O2', 'max_O2']
    climatology_CTD_umol_kg = pd.DataFrame(data, columns=column_names)

if __name__ == "__main__":
    fig = plt.figure()
    plotvar = input('DOX2 or oxygen saturation? DOX2 or DOXS')

    plot_goodCTD(plotvar)
    if plotvar == 'DOX2':
        plt.gca().set_xlabel('Dissolved oxygen umol/kg')
        plt.gca().set_yalbel('Depth - log scale')
    else:
        plt.gca().set_xlabel('Oxygen saturation')
        plt.gca().set_ylabel('Depth - log scale')

    plt.gca().set_yscale('log')
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.show()



