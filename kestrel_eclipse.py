#This code makes a meteorogram from Kestrel Weather Meter data in a .txt file
#Created by Massey Bartolini, 8/23/2017

import matplotlib as mpl
import matplotlib.dates as mdates
mpl.use('Agg') #Prevent need for an X server
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from datetime import datetime,timedelta
import numpy as np
import matplotlib.pyplot as plt

fdir='' #Base file directory location (leave blank if running script in this directory)

#Read .txt file
fname='kestrel_20170821_eclipse.txt'
times,wspd,temp,wchl,relh,heat,dewp,wetb,pres,alti,dalt = np.loadtxt(fdir+fname,skiprows=4,comments='#',delimiter=',',unpack=True)

#Find gaps in the data
igaps=[]
index=1
for i in range(len(times)-1):
	if times[i+1]-times[i]>10.0:
		#gaps.append(times[i])
		igaps.append(index)
	index+=1
#print ('Here are the data gaps: ', igaps)
#print ('Here is the total length of the record', len(times))

#Convert integer time values from seconds to datetime
origin=datetime(2000,1,1,0,0) #Time is recorded in seconds elapsed since this date
dtimes=[origin+timedelta(seconds=time_sec) for time_sec in times]

#Create figure and plot variables
fig,ax=plt.subplots(figsize=(12,7))

#Select data ranges (have to plot two separate lines to allow for a 15-minute gap in the data where the Kestrel powered down by accident)
#Data before index 131 seem like they might have been skewed by temp sensor in sunlight, biased warm
start1=131 #Indices of intervals, split cleanly at gap
end1=220
start=220
end=2297

#For primary axis, plotting each line segment separately
lns1 = ax.plot(dtimes[start1:end1], heat[start1:end1], '-', label = 'Heat Index',color='m')
lns1 = ax.plot(dtimes[start:end], heat[start:end], '-', label = 'Heat Index',color='m')
lns2 = ax.plot(dtimes[start1:end1], temp[start1:end1], '-', label = 'Temperature',color='r')
lns2 = ax.plot(dtimes[start:end], temp[start:end], '-', label = 'Temperature',color='r')

#Secondary axis
ax2 = ax.twinx()
lns3 = ax.plot(dtimes[start1:end1], dewp[start1:end1], '-', label = 'Dewpoint',color='g')
lns3 = ax.plot(dtimes[start:end], dewp[start:end], '-', label = 'Dewpoint',color='g')
lns4 = ax2.plot(dtimes[start1:end1], pres[start1:end1], '-', label = 'Stn. Pressure',color='b')
lns4 = ax2.plot(dtimes[start:end], pres[start:end], '-', label = 'Stn. Pressure',color='b')

#Plot partial and total eclipse intervals as transparent gray colors
ax.axvspan(datetime(2017,8,21,13,4,32),datetime(2017,8,21,15,58,59),color='k',alpha=0.1) #Partial eclipse
ax.axvspan(datetime(2017,8,21,14,33,10),datetime(2017,8,21,14,35,40),color='k',alpha=0.4) #Total eclipse

#Gathering and formatting labels for legend
lns = lns1+lns2+lns3+lns4
#Append proxy artists for eclipse patches
ppatch=mpl.patches.Rectangle((0,0),1,1,fc='k',alpha=0.1,label='Partial Eclipse')
tpatch=mpl.patches.Rectangle((0,0),1,1,fc='k',alpha=0.4,label='Total Eclipse')
lns.append(ppatch)
lns.append(tpatch)
labs = [l.get_label() for l in lns]

#Set nice date formatting for x-axis
ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0,60,15)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

#Plot min temp, max dewp and other info as annotations
tminidx,=np.where(temp==temp[start:end].min()) #found lots of equally low temps (picking just the first and last occurrence for the lowest temp range around totality)
tminidxfirst=tminidx[0]
tminidxlast=tminidx[-1]
tdmaxidx,=np.where(dewp==dewp[start:end].max()) #finding the highest dewpoint
tdmaxidx=tdmaxidx[0]
ax.annotate('First Min. Temp.: '+str(temp[tminidxfirst])+' $^\circ$F\nTime: '+dtimes[tminidxfirst].strftime('%H:%M:%S EDT'),xy=(dtimes[tminidxfirst],temp[tminidxfirst]),xycoords='data',xytext=(0.25,0.5),textcoords='axes fraction',arrowprops=dict(facecolor='k',arrowstyle='-|>'),zorder=9)
ax.annotate('Last Min. Temp.: '+str(temp[tminidxlast])+' $^\circ$F\nTime: '+dtimes[tminidxlast].strftime('%H:%M:%S EDT'),xy=(dtimes[tminidxlast],temp[tminidxlast]),xycoords='data',xytext=(0.25,0.43),textcoords='axes fraction',arrowprops=dict(facecolor='k',arrowstyle='-|>'),zorder=9)
ax.annotate('Max. Dewp.: '+str(dewp[tdmaxidx])+' $^\circ$F\nTime: '+dtimes[tdmaxidx].strftime('%H:%M:%S EDT'),xy=(dtimes[tdmaxidx],dewp[tdmaxidx]),xycoords='data',xytext=(0.6,0.46),textcoords='axes fraction',arrowprops=dict(facecolor='k',arrowstyle='-|>'),zorder=9)
ax.annotate('Partial Eclipse: '+datetime(2017,8,21,13,4,32).strftime('%H:%M:%S')+' to '+datetime(2017,8,21,15,58,59).strftime('%H:%M:%S EDT'),xy=(0.01,0.085),xycoords='axes fraction',zorder=9)
ax.annotate('Total Eclipse: '+datetime(2017,8,21,14,33,10).strftime('%H:%M:%S')+' to '+datetime(2017,8,21,14,35,40).strftime('%H:%M:%S EDT'),xy=(0.01,0.05),xycoords='axes fraction',zorder=9)
ax.annotate('Plot by Massey Bartolini',xy=(0.01,0.015),xycoords='axes fraction',zorder=9)

#Inset basemap with totality path overlay
axin=inset_axes(ax,width='20%',height='20%',loc=5)
vlon,vlat=-84.2164,35.5798
inmap=Basemap(projection='mill',llcrnrlat=vlat-2,llcrnrlon=vlon-4,urcrnrlat=vlat+2,urcrnrlon=vlon+4, resolution='h',ax=axin,anchor='E')
xpt,ypt=inmap(vlon,vlat)
inmap.plot(xpt,ypt,'*',markersize=12,color='r',zorder=8) #My location during eclipse
ecdir='shapefiles/' #Eclipse shapefiles courtesy of NASA Scientific Visualization Studio (link, last accessed 23 Aug 2017: https://svs.gsfc.nasa.gov/4518)
inmap.readshapefile(ecdir+'upath17','upath17',linewidth=0,color='k')
patches,labels=[],[]
for info,shape in zip(inmap.upath17_info,inmap.upath17): #Gather shapefile patches to plot white shapefile boundary
	patches.append(mpl.patches.Polygon(np.array(shape),True))
	labels.append(info['Name'])
plt.gca().add_collection(mpl.collections.PatchCollection(patches,facecolor='0.1',edgecolor='w',linewidths=1.5,alpha=0.6,zorder=7))

#Draw inset map states, boundary, and lakes
inmap.drawstates(linewidth=1.0)
inmap.fillcontinents(color='goldenrod',lake_color='blue')
inmap.drawmapboundary(fill_color='blue')

#Set remaining plot info: title, labels, etc
ax.set_title('21 August 2017 Total Solar Eclipse\nVonore, TN, USA ('+str(vlat)+' N, '+str(abs(vlon))+' W, Elevation: 858 ft.)')
ax.set_ylabel(r'Heat Index / Temperature / Dewpoint ($^\circ$F)')
ax2.set_ylabel('Station Pressure (hPa)')
ax.set_yticks(range(0,110,5))
ax2.set_ylim(989,998)
ax.set_ylim(55,103)
ax.set_xlabel('Time (EDT)')
ax.grid(which='major',alpha=0.5)
ax.legend(lns, labs, loc='center left',prop={'size':10})

#Save plot
plt.savefig(fdir+'eclipse_20170821.png',bbox_inches='tight')
