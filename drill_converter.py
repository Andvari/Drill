#!/usr/bin/python3

"""
Created on May 5, 2016
author: nemo
"""

import re
import sys

def save(a):
    g.write(a + "\n")
    print(a)


def mm2inches(a):
    return a/25.4


def inches2mm(a):
    return a*25.4

gcode_units = {'Inch': 'g20', 'MM': 'g21'}
gcode_mode = {'Absolute': 'g90', 'Incremental': 'g91'}
pcb_thickness = {'Inch': mm2inches(1.5), 'MM': 1.5}
zdepth = {'Inch': mm2inches(-2.), 'MM': -2.}     # drill depth, mm
zfeed_rate = 100
xyfeed_rate = 1000
zstart = {'Inch': mm2inches(1.), 'MM': 1.}     # drill start, mm
contour_drill = 1.

name = ""
if len(sys.argv) > 1:
    print(sys.argv[1])
    name = sys.argv[1][:sys.argv[1].rfind(".")]
    drd_file = open(name + ".drd")
    dri_file = open(name + ".dri")
else:
    print("No input file")
    exit(1)

xsize = 0.
ysize = 0.
if len(sys.argv) > 2:
    xsize = float(sys.argv[2])
    ysize = float(sys.argv[3])

for line in dri_file:
    if line.find('Data Mode') != -1:
        data_mode = line[line.find(':')+2: len(line)-1]
    if line.find('Units') != -1:
        line = line[line.find(':')+2:]
        dividend = int(line[: line.find('/')])
        divisor = int(line[line.find('/')+1: line.find(' ')])
        units = line[line.find(' ')+1:len(line)-1]

scale = float(divisor)
print(data_mode, units, scale, sep=", ")
page = drd_file.read()
page = page.replace("\n", "")

header = page[page.find("T"):page.rfind("%")] + "T"
ndrills = re.compile("T(.*?)C").findall(header)
ddrills = re.compile("C(.*?)T").findall(header)
body = page[page.rfind("%")+2 : len(page)-3] + "T"
ddrills.reverse()
sholes = re.compile("(.+?)T").findall(body)


for shole in sholes:
    if units == 'Inch':
        drill_diameter = format(inches2mm(float(ddrills.pop())), '.2f')
    else:
        drill_diameter = format(float(ddrills.pop()), '.2f')
    g = open(name + "_" + str(drill_diameter) + "_mm.ngc", "w")
    save("%")
    if units == 'Inch':
        save('g20 (inches)')
    else:
        save('g21 (mm)')
    if data_mode == 'Absolute':
        save("g90 (absolute mode)")
    else:
        save("g91 (incremental mode)")
    save("g1 f" + str(zfeed_rate))
    save("(drill diameter " + str(drill_diameter) + " mm)")
    shole = shole[3:] + "X"
    holes = re.compile("(.*?)X").findall(shole)
    for hole in holes:
        (x, y) = hole.split('Y')
        x = float(x) / scale
        y = float(y) / scale
        save("g99 g81 x" + format(x, '.4f') + " y" + format(y, '.4f') + " z" + format(zdepth[units], '.4f') + ' R' + format(zstart[units], '.4f'))
    save('g91 g0 z25')
    save('g90 (return to absolute mode)')
    save('g0 x0 y0')
    save('m2')
    save('%')
    g.close()

if xsize == 0 or ysize == 0:
    print('No board dimensions defined')
    exit(0)

print('Board X dimension: ', xsize)
print('Board Y dimension: ', ysize)
data_mode = 'Absolute'
units = 'MM'

g = open(name + '_contour_1.0_mm.ngc', 'w')
save('%')
save(gcode_units[units] + ' (' + units + ')')
save(gcode_mode[data_mode] + ' (' + data_mode + ')')
save('g1 z1 f' + str(zfeed_rate))

save('g0 x0 y0')
#+ str(0+contour_drill/2) + ' y' + str(0-contour_drill/2))
zstart = 0
while zstart >= -pcb_thickness[units]:
    save('g0 x' + str(0 + contour_drill / 2) + ' y' + str(0 - contour_drill / 2))
    save('g1 z' + str(zstart) + ' f' + str(zfeed_rate))
    save('g1 x' + format(xsize-contour_drill/2, '.4f') + ' f' + str(xyfeed_rate))
    save('g1 z1 f' + str(zfeed_rate))

    save('g0 x' + str(xsize + contour_drill / 2) + ' y' + str(0 + contour_drill / 2))
    save('g1 z' + str(zstart) + ' f' + str(zfeed_rate))
    save('g1 y' + format(ysize-contour_drill/2, '.4f') + ' f' + str(xyfeed_rate))
    save('g1 z1 f' + str(zfeed_rate))

    save('g0 x' + str(xsize - contour_drill / 2) + ' y' + str(ysize + contour_drill / 2))
    save('g1 z' + str(zstart) + ' f' + str(zfeed_rate))
    save('g1 x' + format(0 + contour_drill/2, '.4f') + ' f' + str(xyfeed_rate))
    save('g1 z1 f' + str(zfeed_rate))

    save('g0 x' + str(0 - contour_drill / 2) + ' y' + str(ysize - contour_drill / 2))
    save('g1 z' + str(zstart) + ' f' + str(zfeed_rate))
    save('g1 y' + format(0 + contour_drill/2, '.4f') + ' f' + str(xyfeed_rate))
    save('g1 z1 f' + str(zfeed_rate))

    zstart -= contour_drill/4
save('g91 g0 z25' + ' f' + str(zfeed_rate))
save('g90 (return to absolute mode)')
save('g0 x0 y0')
save('m2')
save('%')
g.close()
