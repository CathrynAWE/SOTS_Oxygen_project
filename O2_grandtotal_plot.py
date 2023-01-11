import matplotlib.pyplot as plt
import plot_atlas_profile_DOX as atlas
import CTD_O2_climatology as CTD
import plot_O2_sensor_all_moorings as sensor
import plot_SOTS_argo_profiles as argo

fig1, ax1 = plt.subplots(figsize=(11.69, 8.27))

argo.plot_argo()
plt.gca().invert_yaxis()
plt.grid(True)
plt.xlim([0, 400])
#plt.ylim([0, 3000])
#plt.gca().set_yscale('log')
plt.gca().set_xlabel('Oxygen umol/kg')
plt.gca().set_ylabel('Depth')# - log scale')


fig1, ax2 = plt.subplots(figsize=(11.69, 8.27))
plotvarCTD = 'DOX2'
CTD.plot_goodCTD(plotvarCTD)

depth_lim = 800
plotvar = 'depth'
sensor.plot_sensor_O2(depth_lim, plotvar)

atlas.plot()


plt.gca().invert_yaxis()
plt.grid(True)
plt.xlim([0, 400])
#plt.ylim([0, 3000])
#plt.gca().set_yscale('log')
plt.gca().set_xlabel('Oxygen umol/kg')
plt.gca().set_ylabel('Depth')# - log scale')
plt.show()





