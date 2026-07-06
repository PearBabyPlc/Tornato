import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import metpy.calc as mpcalc
import numpy as np
from metpy.plots import Hodograph, SkewT
from metpy.units import units
from datetime import datetime
from siphon.simplewebservice.igra2 import IGRAUpperAir

#UTC    Local    hPa    degC    dewC    knots   dir     deg     notes
#0:00	10:00AM	1006	24.0	17.0	9.9 	NE  	45      YMML radiosonde DONE
#4:30	2:30PM	1003	31.0	16.0	22.0	N    	0       YMML high temp DONE
#6:06	4:06PM	1001	25.0	18.0	14.0	S   	180     Laverton radar
#6:43	4:43PM	1001	25.0	19.0	9.0 	S	    180     YMML high dew

# IGRA request
filename = "443pm"
directoryname = "./YMML-25dec2011-supercell/"
description = "Melbourne Airport (113m ASL), 10am radiosonde"
station = "ASM00094866"
date = datetime(2011, 12, 25, 0)
df, header = IGRAUpperAir.request_data(date, station)

# surface data
sH = 113.0
sP = 1001.0
sT = 25.0
sTd = 19.0
sWS = 9.0
sWD = 180.0

# convert into 1d numpy arrays
h = df['height'].values
p = df['pressure'].values #* units.hPa
T = df['temperature'].values #* units.degC
Td = df['dewpoint'].values #* units.degC
wind_speed = df['speed'].values #* units.knots
wind_dir = df['direction'].values #* units.degrees

# find the number of entries to remove (no pressure data)
# also remove everything below 100hPa
revP = np.flip(p)
nanLen = 0
minP = 100.0
for x in revP:
    if (np.isnan(x) == True):
        nanLen += 1
    else:
        break

# remove those entries at the end of the arrays
h = h[:-nanLen]
p = p[:-nanLen]
T = T[:-nanLen]
Td = Td[:-nanLen]
wind_speed = wind_speed[:-nanLen]
wind_dir = wind_dir[:-nanLen]

# linear interpolation for missing values
def fillGaps(arr):
    ind = -1
    xArr = []
    yArr = []
    for x in arr:
        ind += 1
        if (np.isnan(x) != True):
            xArr.append(ind)
            yArr.append(x)
        else:
            pass
    fillRange = np.linspace(0, len(arr), num=int(len(arr) + 1), endpoint=True)
    fillArr = np.interp(fillRange, xArr, yArr)
    testicle = zip(arr, fillArr)
    return fillArr

h = fillGaps(h)
p = fillGaps(p)
T = fillGaps(T)
Td = fillGaps(Td)
wind_speed = fillGaps(wind_speed)
wind_dir = fillGaps(wind_dir)

# converting wind speed to knots
wind_speed = wind_speed * 1.94384449

# add surface conditions
h = np.concatenate(([sH],h))
p = np.concatenate(([sP],p))
T = np.concatenate(([sT],T))
Td = np.concatenate(([sTd],Td))
wind_speed = np.concatenate(([sWS],wind_speed))
wind_dir = np.concatenate(([sWD],wind_dir))

# zip cond at pressure readout thingy
condAtP = zip(p, T, Td, wind_speed, wind_dir, h)

# get stuff for the plot
h = h * units.meters
p = p * units.hPa
T = T * units.degC
Td = Td * units.degC
wind_speed = wind_speed * units.knots
wind_dir = wind_dir * units.degrees
u, v = mpcalc.wind_components(wind_speed, wind_dir)
pLCL, tLCL = mpcalc.lcl(p[0], T[0], Td[0])
parcel = mpcalc.parcel_profile(p, T[0], Td[0])

# calculate indices, lol this is a dog's breakfast
CAPE, CIN = mpcalc.cape_cin(p, T, Td, parcel)
sbcape, sbcin = mpcalc.surface_based_cape_cin(p, T, Td)
mucape, mucin = mpcalc.most_unstable_cape_cin(p, T, Td)
lclParr = np.stack((p[0], pLCL))
lclTarr = np.stack((T[0], tLCL))
sbRH = mpcalc.relative_humidity_from_dewpoint(T[0], Td[0])
mixingRatioSB = mpcalc.mixing_ratio_from_relative_humidity(p[0], T[0], sbRH)
surfaceBasedLCLheight = mpcalc.thickness_hydrostatic(lclParr, lclTarr, mixing_ratio=mixingRatioSB)
_, _, stormHelicity1km = mpcalc.storm_relative_helicity(h, u.to('meters / second'), v.to('meters / second'), (1000 * units.meters))
_, _, stormHelicity3km = mpcalc.storm_relative_helicity(h, u.to('meters / second'), v.to('meters / second'), (3000 * units.meters))
pEL, tEL = mpcalc.el(p, T, Td, parcel)
elParr = np.stack((pLCL, pEL))
elTarr = np.stack((tLCL, tEL))
EL = mpcalc.thickness_hydrostatic(elParr, elTarr) + surfaceBasedLCLheight
effTop = ((EL - surfaceBasedLCLheight) * 0.5) + surfaceBasedLCLheight
_, _, effStormHelicity = mpcalc.storm_relative_helicity(h, u.to('meters / second'), v.to('meters / second'), effTop, bottom=surfaceBasedLCLheight)
sixkm = 6000 * units.meters
u6, v6, = mpcalc.bulk_shear(p, u.to('meters / second'), v.to('meters / second'), height=h, depth=sixkm)
print("eff top:", effTop)
ue, ve= mpcalc.bulk_shear(p, u.to('meters / second'), v.to('meters / second'), height=h, bottom=surfaceBasedLCLheight, depth=effTop)
shear6km = mpcalc.wind_speed(u6, v6).to('knots')
effShear = mpcalc.wind_speed(ue, ve).to('knots')
Sigtor = mpcalc.significant_tornado(sbcape, surfaceBasedLCLheight, stormHelicity1km, shear6km)
supercellComposite = mpcalc.supercell_composite(mucape, effStormHelicity, effShear)
SWEAT = mpcalc.sweat_index(p, T, Td, wind_speed, wind_dir)

# write sounding md file for archival purposes
MDfilename = str(directoryname + filename + ".md")
SVGfilename = str(directoryname + filename + ".svg")
with open(MDfilename, 'w') as f:
    f.write(f"{description}\n")
    f.write(f"station: {station}\n")
    f.write(f"datetime: {datetime}\n\n")
    
    f.write(f"CAPE: {CAPE}\n")
    f.write(f"CIN: {CIN}\n")
    f.write(f"sbCAPE: {sbcape}\n")
    f.write(f"muCAPE: {mucape}\n")
    f.write(f"LCL height: {surfaceBasedLCLheight}\n")
    f.write(f"EL height: {EL}\n")
    f.write(f"SRH 1km: {stormHelicity1km}\n")
    f.write(f"SRH 3km: {stormHelicity3km}\n")
    f.write(f"SRH eff: {effStormHelicity}\n")
    f.write(f"shear 6km: {shear6km}\n")
    f.write(f"shear eff: {effShear}\n")
    f.write(f"Significant Tornado: {Sigtor}\n")
    f.write(f"Supercell Composite: {supercellComposite}\n")
    f.write(f"SWEAT index: {SWEAT}\n\n")

    f.write("km, hPa, degC, dewC, kts, deg\n")
    for x in condAtP:
        he = x[-1]
        pa = x[0]
        tk = x[1]
        td = x[2]
        ws = x[3]
        wd = x[4]
        f.write(f"{he:.1f} {pa:.1f} {tk:.1f} {td:.1f} {ws:.1f} {wd:.1f}\n")

# plot skew-T
fig = plt.figure(figsize=(9, 9))
skew = SkewT(fig, rotation=30)
skew.plot(p, T, 'r')
skew.plot(p, Td, 'g')
skew.plot_barbs(p, u, v)
skew.ax.set_ylim(1000, 70)
skew.ax.set_xlim(-40, 40)
skew.plot(pLCL, tLCL, 'ko', markerfacecolor='black')
skew.plot(p, parcel, 'k', linewidth=2)
skew.shade_cin(p, T, parcel, Td)
skew.shade_cape(p, T, parcel)
skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)
skew.plot_dry_adiabats()
skew.plot_moist_adiabats()
skew.plot_mixing_lines()

#plot hodograph
ax_hod = inset_axes(skew.ax, '40%', '40%', loc=1, borderpad=4.0)
h = Hodograph(ax_hod, component_range=80.)
h.add_grid(increment=20)
h.plot_colormapped(u, v, wind_speed)
plt.savefig(SVGfilename)
plt.show()
