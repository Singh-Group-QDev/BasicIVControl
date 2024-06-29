import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator
import pandas as pd

filename = "C:\\Users\\blloy\\Documents\\BasicIVControl\\Data\\IVB\\V4P2024-06-04_8.csv"
dataframe = pd.read_csv(filename, on_bad_lines='skip', header=11, names=["Current","Voltage","CurrentSTD","TemperatureA","TemperatureB"])

matplotlib.rcParams.update({'font.size': 8})   
gs = gridspec.GridSpec(2, 2)
fig1, ax1 = plt.subplots()
ax1.plot(dataframe.Voltage, dataframe.Current)
ax1.xaxis.set_minor_locator(AutoMinorLocator())
ax1.yaxis.set_minor_locator(AutoMinorLocator())
ax1.set_axisbelow(True)
fig1.set_size_inches(3.4,2.5)
fig1.set_dpi(600)
ax1.grid(True, linestyle=':',lw=0.3,which='minor')
ax1.grid(True, linestyle='-',lw=0.3,which='major')
ax1.set_ylabel('Resistivity ($\Omega$)')
ax1.set_xlabel('B (T)')
plt.setp(ax1.spines.values(), linewidth=0.5)
ax1.tick_params(width=0.5)
ax1.scatter(Ttrunc1,Rtrunc1,s=3,c='firebrick',label='Clathrate')