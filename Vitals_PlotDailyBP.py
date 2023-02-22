# plots dail blood pressures, protocol limits and means
# for an arbitrary date range.  Null ending date defeaults to now.import numpy as np
#This iteration repairs to major design/execution flaws in prior version.
# it should now properly handle ending ddates rather just defaulting to now
 #prior version did not properly handlee nulls.  This version appears to properly
#habdle nulls (as far as it has been tested.)  Have not been able to figure out 
#an xticks/xtickslabel schemme thatt makes sense to me.  So what you see is what you 
#get (no xtickslabel) and ,aking do wwith an x-axis label.
# 2/21/23
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3 as sql
import datetime as dt
import sys

# specify starting and ending dates for plots
startyear = '2022'
startmth  = '11'
startday  = '01'
endyear   = '2023'
endmth    = '01'		# null will default to now
endday    = '31'
tflist = ['AM','PM']

empty = [np.nan,'','NaN','NaT','nan',' ',0,0.0]
bpsyslim = 150		# current protocol for my age
bpdialim = 90 
long = 120			# # charsfor length of x-axis label
stats = ''
mthlist = ['','Jan','Feb','Mar','Apr','May','Jun','Jul',
			'Aug','Sep','Oct','Nov','Dec']

# set up dates
if endyear == '':
	now1 	  = dt.datetime.now()
	now       = str(now1)
	curyear   = now[0:4]
	curmth    = now[5:7]
	curday    = now[8:10]
	endyear   = curyear
	endmth    = curmth
	endday    = curday

sd = startyear + '-' + startmth + '-' + startday
ed = endyear + '-' + endmth + '-' +endday
sp = dt.datetime(int(startyear),int(startmth),int(startday))
ep = dt.datetime(int(endyear),int(endmth),int(endday))
pc = str(ep - sp)
pc = int(pc[0:int(pc.find(' '))])
dr  =  pd.date_range(sp, periods=pc, freq="D")

con = sql.connect("D:/SqlData/Diary.db")
cur = con.cursor()

# for each time frame
for tf in tflist:
	# initialize plot line lists
	sys  = ''
	dia  = ''
	lim1 = ''
	lim2 = ''
	avg1 = ''
	avg2 = ''

	qry = 'Select Date, Sys, Dia from VITALS1 where TF = ' + '"'+tf+'"'
	qry += ' and Date Between ' + '"' + sd + '"'
	qry += ' and ' + '"' + ed + '"' + ' order by date'
	df = pd.read_sql_query(qry, con)	# read data into datafframe
	df.replace(['nan','Nan',0,0.0,' ','  '],np.nan, inplace=True)

	try:
		bx  = df.aggregate({"Sys":['mean','std'], "Dia":['mean','std']})
		savg = str(round(df.loc["mean",'Sys'],))
		sstd = str(round(df.loc['std','Sys'],1))
		davg = str(round(df.loc['mean','Dia'],1))
		dstd = str(round(df.loc['std', 'Dia'],1))
		sstd = str(round(df.loc['std', 'Sys'],1))
		stats = 1	
	except:
		savg  = 0
		savgn = 0
		davg  = 0
		davgn = 0
		sstd = ''
		dstd = ''


	# set report dates to acutal dates in data
	numrows   = len(df)
	startyear = str(df.Date[0])[0:4]
	startmth  = str(df.Date[0])[5:7]
	startday  = str(df.Date[0])[8:10]
	rndyear   = str(df.Date[numrows-1])[0:4]
	endmth    = str(df.Date[numrows-1])[5:7]
	endday    = str(df.Date[numrows-1])[8:10]

	sd = startyear + '-' + startmth + '-' + startday
	ed = endyear + '-' + endmth + '-' + endday
	sp = dt.datetime(int(startyear),int(startmth),int(startday))
	dr  =  pd.date_range(sp, periods=pc, freq="D")

	# add missing days to datagrane
	needsort = 0
	for idx in range(len(dr)-1):
		dte = str(dr[idx])[0:10]
		found = 0
		for jdx in range(len(df)-1):
			if dte == str(df.Date[jdx]):
				found = 1
		if not found:
			needsort = 1
			df.loc[len(df.index)] = [dte,0,0] 

	# sort by date
	if needsort:
		dx = df.sort_values(by=['Date'],kind='mergesorrt')
		df = dx
		df.set_index("Date")  # may not be necessary

	# calc the means
	if not stats:
		for idx in range(len(df)-1):
			if df.Sys[idx] != '':
				savg += df.Sys[idx]
				savgn += 1
			if df.Dia[idx] != '':
				davg += df.Dia[idx]
				davgn += 1

	# add average values
	if savgn > 0:
		savg = round(savg/savgn,1)
	if davgn > 0:
		davg = round(davg/davgn,1)

	# plot routine barfs on nulls
	df.replace(['nan','Nan',0,0.0,'',' ','  '],np.nan, inplace=True)

	if tf == "AM":
	#	df.to_csv('d:/exceldata/daiybpAM.csv')
		df.to_excel('d:/exceldata/daiybpAM.xlsx')
		jpgfname = 'D:/prgout/plotDailyBP-AM.jpg'
	else:
	#	df.to_csv('d:/exceldata/daiybpPM.csv')
		df.to_excel('d:/exceldata/daiybpPM.xlsx')	
		jpgfname = 'D:/prgout/plotDailyBP-PM.jpg'

	numdf = len(df)
	lim1 = np.zeros((numdf),dtype=int)
	lim2 = np.zeros((numdf),dtype=int)
	ticks = np.zeros((numdf),dtype=int)
	tckl = np.array((numdf))
	avg1 = np.zeros((numdf),dtype=float)
	avg2 = np.zeros((numdf),dtype=float)
	xlab = []
	for x in range(numdf):
		lim1[x] = bpsyslim		# Upper protocol linit
		lim2[x] = bpdialim		# lower protocol limit
		avg1[x] = savg			# systolic mean
		avg2[x] = davg 			# diastolic mean
		ticks[x] = x
		mth = int(str(df.loc[x,'Date'])[5:7])
		day = int(str(df.loc[x,'Date'])[8:10])
		lab = mthlist[mth]
		if lab not in xlab:
			xlab.append(lab)

	# set up the x-axis label
	xlabel = ''
	if numdf < long:
		long = numdf
	cnt = len(xlab)
	if cnt > 1:
		if cnt > 2:
			used = cnt * 3
			reqd = long - used
			spc = int(reqd/cnt-2)
			spaces = ''
			for jdx in range(spc):
				spaces += ' '
			for idx in range(cnt-1):
				xlab[idx] += spaces
			xlabel = xlab[0]
			for idx in range(cnt-2):
				xlabel += xlab[idx+1]
			xlabel += xlab[cnt-1]
		else:
			xlabel = xlab[0]
			for jdx in range(100):
				xlabel += ' '
			xlabel += xlab[1]
	else:
		for jdx in range(int(long/2)):
			xlabel += ' '
		xlabel += xlab[0]

	plottitle = tf+' Daily Blood Pressures for: ' + sd + '-' + ed +'\n'
	plottitle += 'Sys Mean = ' + str(savg) + '   Dia Mean = ' + str(davg)
	if sstd and dstd:
		plottitle +='\nSys StdDev = ' + str(sstd) + '   Dia StdDev = ' + str(dstd)

	x = df.Date
	fig = plt.figure()
	ax = fig.subplots()
	plt.subplot()
	ax.set_title(plottitle)
	ax.set_xticks(ticks)	
	ax.set_xlabel(xlabel)
#	ax.set(xticklabels =tckl)
	ax.plot(x,df.Sys,label='Systolic',color='red')
	ax.plot(x,df.Dia,label='Diastolic',color='blue')
	ax.plot(lim1,label='Protocol', color='gray')
	ax.plot(lim2,color='gray')
	ax.plot(avg1,label='Means',color='green')
	ax.plot(avg2,color='green')
	ax.legend();
	plt.savefig(jpgfname)
	plt.show()
	print(jpgfname,"saved")

con.close()
			