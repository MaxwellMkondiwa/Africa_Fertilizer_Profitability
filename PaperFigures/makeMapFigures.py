from __future__ import division
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib as mpl
import os
import pandas as pd

#os.environ['PROJ_LIB']='C:/Users/Julianne Quinn/Anaconda3/pkgs/proj4-5.2.0-ha925a31_1/Library/share' # Home Desktop
#os.environ['PROJ_LIB']='C:/Users/jdq21/Anaconda3/pkgs/proj4-4.9.3-vc14_5/Library/share' # Laptop
os.environ['PROJ_LIB']='C:/ProgramData/Anaconda3/pkgs/proj4-4.9.3-vc14_5/Library/share' # Work Desktop

from mpl_toolkits.basemap import Basemap

# load data
data = pd.read_csv('Simdata_cellid.csv')
yp_difSensitivity = pd.read_csv('yp_dif_avg_most_sensitive.csv')
irrSensitivity = pd.read_csv('irr_avg_most_sensitive.csv')

variables = ['temp_p1','temp_p2','temp_p3','precip_p1','precip_p2','precip_p3',
             'soilcec','soilph','acidity','soilom','soiln','claypct','siltpct','bulkdens',
             'elevm','mp','up','int']

def getGroup(sensitivity):
    # classify most sensitive variables into groups
    sensitivity['group'] = np.empty(len(sensitivity['MostSensitive']))
    sensitivity['group'][np.hstack([np.where(sensitivity['MostSensitive']=='temp_p1')[0],
                                    np.where(sensitivity['MostSensitive']=='temp_p2')[0],
                                    np.where(sensitivity['MostSensitive']=='temp_p3')[0]])] = 0
    sensitivity['group'][np.hstack([np.where(sensitivity['MostSensitive']=='precip_p1')[0],
                                    np.where(sensitivity['MostSensitive']=='precip_p2')[0],
                                    np.where(sensitivity['MostSensitive']=='precip_p3')[0]])] = 1
    sensitivity['group'][np.where(sensitivity['MostSensitive']=='soilph')[0]] = 2
    sensitivity['group'][np.hstack([np.where(sensitivity['MostSensitive']=='soilcec')[0],
                                    np.where(sensitivity['MostSensitive']=='acidity')[0],
                                    np.where(sensitivity['MostSensitive']=='soilom')[0],
                                    np.where(sensitivity['MostSensitive']=='soiln')[0],
                                    np.where(sensitivity['MostSensitive']=='claypct')[0],
                                    np.where(sensitivity['MostSensitive']=='siltpct')[0],
                                    np.where(sensitivity['MostSensitive']=='bulkdens')[0]])] = 3
    sensitivity['group'][np.where(sensitivity['MostSensitive']=='elevm')[0]] = 4
    sensitivity['group'][np.hstack([np.where(sensitivity['MostSensitive']=='mp')[0],
                                    np.where(sensitivity['MostSensitive']=='up')[0],
                                    np.where(sensitivity['MostSensitive']=='int')[0]])] = 5
    
    return sensitivity

irrSensitivity = getGroup(irrSensitivity)
yp_difSensitivity = getGroup(yp_difSensitivity)

irrData = pd.merge(data,irrSensitivity)
yp_difData = pd.merge(data,yp_difSensitivity)

# simulated IRR distributions at different sites
shortlist_data = pd.read_csv('TrialSites_Sim_Shortlist.csv')
selectSites = np.unique(shortlist_data['sitecode'])
site_names = selectSites.astype('str')
index = range(len(np.where(shortlist_data['sitecode']==16)[0]))
CDFs = pd.DataFrame(index=index, columns=site_names)
for i in range(len(selectSites)):
    CDFs[site_names[i]] = shortlist_data['irr_sim'].iloc[np.where(shortlist_data['sitecode']==selectSites[i])[0]].to_numpy()

# locations of sites with simulated IRRs
lat = np.arange(-39.875,40.125,0.25)
lon = np.arange(-19.875,55.125,0.25)
select_data = pd.DataFrame(index=range(len(site_names)), columns=data.columns)
for i in range(len(selectSites)):
    row = i*len(np.where(shortlist_data['sitecode']==shortlist_data['sitecode'][0])[0]) # row of shortlist_data where new sitecode is located, every n simulations
    index = np.intersect1d(np.where(data['lat']==shortlist_data['lat'][row])[0], np.where(data['lon']==shortlist_data['lon'][row])[0])
    select_data.iloc[i,:] = data.iloc[index,:].to_numpy()
    
# color of line for each site and where to label it on the map
siteColors = ['#fdbf6f','#b2df8a','#a6cee3','#cab2d6','#6a3d9a','#fb9a99','#ff7f00','#1f78b4','#e31a1c','#33a02c']
label_ys = np.array(select_data['lat']-1)
label_xs = np.array(select_data['lon']-1.5)
label_xs[0] = label_xs[0] - 2.5
label_xs[3] = label_xs[3] - 5
label_xs[5] = label_xs[5] - 6
label_xs[[1,2,8]] = label_xs[[1,2,8]] + 3
label_ys[[2,4,6,7]] = label_ys[[2,4,6,7]] + 2
label_ys[9] = label_ys[9] - 3

LobellSites = pd.read_csv("../Sites/EIL_site_lat_lon.csv")
CIMMYTsites = pd.read_csv("../Sites/additional_EIL_site_lat_lon.csv")
WortmannSites = pd.read_csv("../Sites/Wortmann_site_lat_lon.csv")

LobellSites['Label'] = 'Lobell Fertilizer Trial Sites'
CIMMYTsites['Label'] = 'CIMMYT Fertilizer Trial Sites'
WortmannSites['Label'] = 'Wortmann Fertilizer Trial Sites'

# remove sites at (0,0)
LobellSites = LobellSites.drop(index=np.intersect1d(np.where(LobellSites['Longitude']==0)[0],
                                   np.where(LobellSites['Latitude']==0)[0]))
CIMMYTsites = CIMMYTsites.drop(index=np.intersect1d(np.where(CIMMYTsites['Longitude']==0)[0],
                                   np.where(CIMMYTsites['Latitude']==0)[0]))
WortmannSites = WortmannSites.drop(index=np.intersect1d(np.where(WortmannSites['Longitude']==0)[0],
                                   np.where(WortmannSites['Latitude']==0)[0]))

maizeSites = pd.read_csv("../Prices/maize_country_mkt_lat_long_beta_stderror.csv")
ureaSites = pd.read_csv("../Prices/urea_country_mkt_lat_long_beta_stderror.csv")

maizeSites['Label'] = 'Maize Markets'
ureaSites['Label'] = 'Urea Markets'

cols = maizeSites.columns.tolist()
cols = cols[0:2] + cols[3:5]
combinedSites = pd.merge(maizeSites[cols], ureaSites[cols], how='outer', indicator='Exist')

maizeOnlySites = combinedSites.loc[combinedSites['Exist'] == 'left_only']
bothSites = combinedSites.loc[combinedSites['Exist'] == 'both']
ureaOnlySites = combinedSites.loc[combinedSites['Exist'] == 'right_only']

def plotSitesMap(LobellSites, CIMMYTsites, WortmannSites, maizeOnlySites, ureaOnlySites, bothSites):
    
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    
    # plot basemap and countries
    m = Basemap(llcrnrlat=-40,urcrnrlat=40,llcrnrlon=-20,urcrnrlon=55,resolution='l')
    m.drawlsmask()
    m.drawcountries(color='0.2', linewidth=0.5)
    m.drawparallels(np.arange(-40,41,20), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, 
                    color='0.8', fontsize=16)
    m.drawmeridians(np.arange(-20,56,15), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, 
                    color='0.8', fontsize=16)
    # plot fertilizer trial sites
    Lobell = ax.scatter(LobellSites['Longitude'],LobellSites['Latitude'],facecolor='#1b9e77',
                     edgecolor='k',marker='o')
    CIMMYT = ax.scatter(CIMMYTsites['Longitude'],CIMMYTsites['Latitude'],
                        facecolor='#1b9e77',edgecolor='k',marker='^')
    Wortmann = ax.scatter(WortmannSites['Longitude'],WortmannSites['Latitude'],
                          facecolor='#1b9e77',edgecolor='k',marker='s')
    
    ax = fig.add_subplot(1,2,2)
    m = Basemap(llcrnrlat=-40,urcrnrlat=40,llcrnrlon=-20,urcrnrlon=55,resolution='l')
    m.drawlsmask()
    m.drawcountries(color='0.2', linewidth=0.5)
    m.drawparallels(np.arange(-40,41,20), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, 
                    color='0.8', fontsize=16)
    m.drawmeridians(np.arange(-20,56,15), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, 
                    color='0.8', fontsize=16)
    # plot maize and urea markets
    maize = ax.scatter(maizeOnlySites['longitude'],maizeOnlySites['latitude'],facecolor='#e6ab02',
                       edgecolor='k',marker='o')
    urea = ax.scatter(ureaOnlySites['longitude'],ureaOnlySites['latitude'],facecolor='#d95f02',
                      edgecolor='k',marker='o')
    both = ax.scatter(bothSites['longitude'],bothSites['latitude'],facecolor='#666666',
                      edgecolor='k',marker='o')
    
    fig.subplots_adjust(bottom=0.3)
    fig.legend([Lobell, Wortmann, CIMMYT, maize, urea, both], ['Lobell Fertilizer Trial Sites',
                'Wortmann Fertilizer Trial Sites','CIMMYT Fertilizer Trial Sites',
                'Maize Markets','Urea Markets','Maize + Urea Markets'], loc='lower center', fontsize=16, ncol=2)
    fig.set_size_inches([12,6])
    fig.savefig('AllSites.pdf')
    fig.clf()
    
    return None

def makeFigure2(data, lat, lon, simIRR, selectSites, select_data, label_xs, label_ys, colors, colorbar):
    
    bounds = np.array([0.0,1.0]) # min and max values - to be replaced after finding them in get_array on next line
    array, bounds = get_array(data, lat, lon, 'y_pred_sim_dif_probT_cfrobust', bounds) # get yield difference and populate in "array"
    C = 'YlOrBr' # colormap
    classes =  [] # categorical classes - empty because plotting continuous values
    
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    makeSubplot(ax, 'y_pred_sim_dif_probT_cfrobust', array, bounds, selectSites, select_data, label_xs, label_ys, \
                C, 'Yield Difference (t/ha)', classes, colorbar, 1.0, True)
    
    # plot CDFs from each site
    ax = fig.add_subplot(1,2,2)
    n = np.shape(simIRR)[0]
    M = np.array(range(1,n+1))
    P = M/(n+1)
    for i in range(len(colors)):
        ax.step(np.sort(simIRR.iloc[:,i]), P, c=colors[i], label=str(int(selectSites[i])), linewidth=2)
        
    ax.set_xlim([-4,9])
    ax.set_ylim([0,1])
    ax.plot([0.2,0.2],[0,1],linewidth=2, linestyle='--', c='k')
    ax.plot([-4,9],[0.3,0.3],linewidth=2, linestyle='--', c='k')
    ax.text(4.5,0.272,"Low Profitability\nTolerance (1-p)",fontsize=18)
    ax.text(-0.25,0.8,"Profitability\nThreshold",fontsize=18,rotation=90)
    
    
    ax.tick_params(axis='both',labelsize=18)
    ax.set_xlabel('IRR (% of Fertilizer Investment)',fontsize=20)
    ax.set_ylabel('Cumulative Distribution',fontsize=20)
    handles, labels = plt.gca().get_legend_handles_labels()
    ax.legend([handles[8],handles[5],handles[6],handles[0],handles[9],handles[1],handles[7],handles[2],handles[4],handles[3]], \
              [labels[8],labels[5],labels[6],labels[0],labels[9],labels[1],labels[7],labels[2],labels[4],labels[3]], \
                  loc='upper right', ncol=1, fontsize=18)
    fig.set_size_inches([19, 9.6])
    
    if colorbar == True:
        fig.savefig('Figure2_cbar.pdf')
    else:
        fig.savefig('Figure2.pdf')
    
    fig.clf()
    
    return None
    
def makeFigure3(data, lat, lon, selectSites, select_data, label_xs, label_ys, figname):
    
    C1 = np.array([[178,24,43],[247,247,247],[146,197,222],[67,147,195],[33,102,172],[5,48,97]])/255.0
    C2 = np.array([[228, 26, 28],[77, 175, 74],[55, 126, 184],[255, 127, 0]])/255.0
    classes = ['Never','Always','Robust\nOnly','Naive\nOnly']
    bounds = np.array([-1.0,0.0,0.3,1.0,2.0,4.0,6.0])
    
    robust_array, bounds = get_array(data, lat, lon, 'irr_sim_probT_cfrobust', bounds)
    naive_array, bounds = get_array(data, lat, lon, 'irr_sim_probT_naive', bounds)
    class_array, bounds = get_array(data, lat, lon, 'class', bounds)
    
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,3,1)    
    makeSubplot(ax, 'irr_sim_probT_cfrobust', robust_array, bounds, selectSites, select_data, label_xs, label_ys, \
                C1, 'Robust IRR', classes, True, 0.5)
    
    ax = fig.add_subplot(1,3,2)
    makeSubplot(ax, 'irr_sim_probT_naive', naive_array, bounds, selectSites, select_data, label_xs, label_ys, C1, \
                'Naive IRR', classes, True, 0.5)
    
    ax = fig.add_subplot(1,3,3)
    makeSubplot(ax, 'class', class_array, bounds, selectSites, select_data, label_xs, label_ys, \
                C2, '', classes, True, 0.5)
    
    fig.set_size_inches([19, 9.6])
    fig.tight_layout()
    fig.savefig(figname)
    fig.clf()
    
    return None

def makeFigureS3(data, lat, lon, selectSites, select_data, label_xs, label_ys):
    
    cmap = 'YlOrBr' # colormap for left panel
    classes =  [] # categorical classes - empty because plotting continuous values in left panel
    #C = np.array([[255,255,204],[194,230,153],[120,198,121],[49,163,84],[0,104,55]])/255.0
    C = np.array([[237,248,251],[178,226,226],[102,194,164],[44,162,95],[0,109,44]])/255.0
    labels = ['Profitable if\nF:M $\leq$ 2.5','Profitable if\nF:M $\leq$ 4',
              'Profitable if\nF:M $\leq$ 6','Profitable if\nF:M $\leq$ 9','Profitable even if\nF:M > 9']
 
    bounds = np.array([0.0,2.5,4.0,6.0,9.0,13.0])
    robust_array, bounds = get_array(data, lat, lon, 'cr_sim_probT_cfrobust', bounds)
    diff_array, bounds = get_array(data, lat, lon, 'y_pred_sim_dif_probT_cfrobust', bounds) # get yield difference and populate in "array"
       
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    makeSubplot(ax, 'y_pred_sim_dif_probT_cfrobust', diff_array, bounds, selectSites, select_data, label_xs, label_ys, \
                cmap, 'Yield Difference (t/ha)', classes, True, 1.0)

    ax = fig.add_subplot(1,2,2)
    makeSubplot(ax, 'cr_sim_probT_cfrobust', robust_array, bounds, selectSites, select_data, label_xs, label_ys, \
                C, '', labels, True, 1.0)

    fig.set_size_inches([13, 5])
    fig.savefig('Map_y_pred_sim_dif_probT_cr_probT_robust.pdf')
    fig.clf()
    
    return None

def makeFigureS4(data, lat, lon, selectSites, select_data, label_xs, label_ys, figname):
    C = np.array([[228, 26, 28],[77, 175, 74],[55, 126, 184],[255, 127, 0]])/255.0
    classes = ['Never','Always','Robust\nOnly','Naive\nOnly']
    bounds = np.array([-1.0,0.0,0.3,1.0,2.0,4.0,6.0])
    
    class_array, bounds = get_array(data, lat, lon, 'classnrt', bounds)
    
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    makeSubplot(ax, 'classnrt', class_array, bounds, selectSites, select_data, label_xs, label_ys, \
                C, '', classes, True, 1.0)
    
    fig.tight_layout()
    fig.savefig(figname)
    fig.clf()
    
    return None

def makeSensitivityMap(yp_difData, irrData, lat, lon, selectSites, select_data, label_xs, label_ys, figname):    
    C_yp_dif = np.array([[228,26,28],[55,126,184],[255,127,0],[166,86,40],[255,255,51]])/255.0
    classes_yp_dif = ['Temperature','Precipitation','Soil pH','Other Soil\nVariables','Elevation']
    bounds_yp_dif = np.array([-0.5,0.5,1.5,2.5,3.5,4.5])
    
    C_irr = np.array([[228,26,28],[55,126,184],[255,127,0],[166,86,40],[255,255,51],[77,175,74]])/255.0
    classes_irr = ['Temperature','Precipitation','Soil pH','Other Soil\nVariables','Elevation','Prices']
    bounds_irr = np.array([-0.5,0.5,1.5,2.5,3.5,4.5,5.5])
    
    class_array_yp_dif, bounds_yp_dif = get_array(yp_difData, lat, lon, 'group', bounds_yp_dif)
    class_array_irr, bounds_irr = get_array(irrData, lat, lon, 'group', bounds_irr)
    
    sns.set()
    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    makeSubplot(ax, 'group', class_array_yp_dif, bounds_yp_dif, selectSites, select_data, label_xs, label_ys, \
                C_yp_dif, '', classes_yp_dif, True, 1.0)
    
    ax = fig.add_subplot(1,2,2)
    makeSubplot(ax, 'group', class_array_irr, bounds_irr, selectSites, select_data, label_xs, label_ys, \
                C_irr, '', classes_irr, True, 1.0)
    
    fig.set_size_inches([15,5])
    fig.savefig(figname)
    fig.clf()
    
    return None

def get_array(data, lat, lon, variable, bounds):
    array = np.empty((80*4,75*4))
    array[:] = np.NAN;
    
    for i in range(np.shape(data)[0]):
        row = int((data['lat'][i]-np.min(lat))/0.25)
        col = int((data['lon'][i]-np.min(lon))/0.25)
        if variable != 'class' and variable != 'classnrt':
            if np.isnan(data[variable][i]) == False:
                array[row,col] = data[variable][i]
        elif variable == 'class':
            if data['class_yesyes_probT'][i] == 1:
                array[row,col] = 1 # always
            elif data['class_nono_probT'][i] == 1:
                array[row,col] = 0 # never
            elif data['class_type1_probT'][i] == 1:
                array[row,col] = 2 # robust
            elif data['class_type2_probT'][i] == 1:
                array[row,col] = 3 # naive
        elif variable == 'classnrt':
            if data['classnrt_yesyes_probT'][i] == 1:
                array[row,col] = 1 # always
            elif data['classnrt_nono_probT'][i] == 1:
                array[row,col] = 0 # never
            elif data['classnrt_type1_probT'][i] == 1:
                array[row,col] = 2 # robust
            elif data['classnrt_type2_probT'][i] == 1:
                array[row,col] = 3 # naive
                
    # update bounds on lower and upper end
    bounds[0] = np.round(np.min([bounds[0], np.nanmin(array)]),1)
    bounds[-1] = np.round(np.max([bounds[-1], np.nanmax(array)]),1)
    
    return array, bounds

def makeSubplot(ax, variable, array, bounds, selectSites, select_data, label_xs, label_ys, \
                C, label, classes, colorbar, shrink, points=False):
    
    # plot basemap and countries
    m = Basemap(llcrnrlat=-40,urcrnrlat=40,llcrnrlon=-20,urcrnrlon=55,resolution='l')
    m.drawlsmask()
    m.drawcountries(color='0.2', linewidth=0.5)
    if variable != 'y_pred_sim_dif_probT_cfrobust':
        m.drawparallels(np.arange(-40,41,20), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, color='0.8', fontsize=16)
        m.drawmeridians(np.arange(-20,56,15), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, color='0.8', fontsize=16)
    else:
        m.drawparallels(np.arange(-40,41,20), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, color='0.8', fontsize=18)
        m.drawmeridians(np.arange(-20,56,15), labels=[1,0,0,1], dashes=[1,1], linewidth=0.25, color='0.8', fontsize=18)
        
    array_mask = np.ma.masked_invalid(array)
    x, y = np.meshgrid(lon, lat)
    x, y = m(x,y)
    if type(C) != str:
        cmap = mpl.colors.ListedColormap(C)
    else:
        cmap = C
        
    if variable == 'irr_sim_probT_cfrobust' or variable == 'irr_sim_probT_naive' or variable == 'cr_sim_probT_cfrobust':
        norm = mpl.colors.BoundaryNorm(boundaries=bounds,ncolors=(len(bounds)-1))
        m.pcolormesh(x, y, array_mask, cmap=cmap, norm=norm, rasterized=False, edgecolor='0.6', linewidth=0)
        cbar = plt.colorbar(shrink=shrink)
    else:
        m.pcolormesh(x, y, array_mask, cmap=cmap, rasterized=False, edgecolor='0.6', linewidth=0)
        if colorbar == True and variable != 'class' and variable != 'classnrt' and variable != 'group':
            cbar = plt.colorbar(shrink=shrink)
        if points == True:
            ax.scatter(select_data['lon'],select_data['lat'],c='k')
            for i in range(len(label_xs)):
                ax.text(label_xs[i], label_ys[i], selectSites[i], fontsize=16)
        
    if variable == 'class' or variable == 'classnrt' or variable == 'group':
        formatter = plt.FuncFormatter(lambda val, loc: classes[val])
        cbar = plt.colorbar(ticks=np.arange(len(C)), format=formatter, shrink=shrink)
        plt.clim(-0.5,len(C)-0.5)
        cbar.solids.set_edgecolor("face")
        
    if colorbar == True:
        if variable == 'cr_sim_probT_cfrobust':
            ticks = np.zeros([len(bounds)-1])
            for i in range(len(ticks)):
                ticks[i] = bounds[i] + (bounds[i+1] - bounds[i])/2
            cbar.set_ticks(ticks)
            cbar.set_ticklabels(classes)

        if variable != 'y_pred_sim_dif_probT_cfrobust':
            cbar.ax.tick_params(labelsize=16)
            cbar.ax.set_ylabel(label,fontsize=18)
        else:
            cbar.ax.tick_params(labelsize=18)
            cbar.ax.set_ylabel(label,fontsize=20)
    
    return ax
    
makeFigure2(data, lat, lon, CDFs, selectSites, select_data, label_xs, label_ys, siteColors, True)
makeFigure2(data, lat, lon, CDFs, selectSites, select_data, label_xs, label_ys, siteColors, False)
makeFigure3(data, lat, lon, selectSites, select_data, label_xs, label_ys, 'Map_IRR_sim_probT_naive_robust_compare.pdf')
makeFigureS3(data, lat, lon, selectSites, select_data, label_xs, label_ys)
makeFigureS4(data, lat, lon, selectSites, select_data, label_xs, label_ys, 
             'Map_IRR_sim_probT_naive_robust_compare_samenaiveprofT.pdf')
makeSensitivityMap(yp_difData, irrData, lat, lon, selectSites, select_data, label_xs, label_ys, 'SensitivityMap.pdf')
#makeSensitivityBarPlot(yp_difData, variables[0:-3], "SensitivityBar_yp_dif.pdf")
#makeSensitivityBarPlot(irrData, variables, "SensitivityBar_irr")
plotSitesMap(LobellSites, CIMMYTsites, WortmannSites, maizeOnlySites, ureaOnlySites, bothSites)
