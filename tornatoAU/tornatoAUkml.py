import csv

# ingest data, I have already prepared the csv file by removing a few flubs
tornados = []
with open("tornatoAU.csv", newline="\n") as t:
    tor = csv.reader(t, delimiter=",", quotechar=r'"')
    for row in tor:
        tornadoTup = []
        for x in row:
            tornadoTup.append(x)
        tornados.append(tornadoTup)

# get rid of header
tornados.pop(0)

# sort the data
outF0 = []
outF1 = []
outF2 = []
outF3 = []
outF4 = []
outF5 = []
outError = []
for x in tornados:
    outDict = {"ID": x[0],
               "dt": x[1],
               "lat": x[3],
               "lon": x[2],
               "town": x[4],
               "state": x[5],
               "F": x[6]}
    match int(outDict.get("F")):
        case 0:
            outF0.append(outDict)
        case 1:
            outF1.append(outDict)
        case 2:
            outF2.append(outDict)
        case 3:
            outF3.append(outDict)
        case 4:
            outF4.append(outDict)
        case 5:
            outF5.append(outDict)
        case _:
            outError.append(outDict)

# unused debug stuff
#def printDicts(outDicts):
#    for x in outDicts:
#        print(x.get("ID"))
#        print(x.get("dt"))
#        print(x.get("lat"))
#        print(x.get("lon"))
#        print(x.get("town"))
#        print(x.get("state"))
#        print(x.get("F"))
#        print()
#    pass
#printDicts(outF0)
#printDicts(outF1)
#printDicts(outF2)
#printDicts(outF3)
#printDicts(outF4)
#printDicts(outF5)

# write a folder per Fujita category
def foldus(k, out):
    for x in out:
        tID = x.get("ID")
        tDt = x.get("dt")
        tLat = x.get("lat")
        tLon = x.get("lon")
        tTown = x.get("town")
        tState = x.get("state")
        fujita = x.get("F")
        k.write("<Placemark>\n")
        k.write(f"<name>F{fujita} {tTown} {tState}</name>\n")
        k.write(f"<description>{tDt} {tID}</description>\n")
        k.write(f"<Point>\n<coordinates>{tLat},{tLon},0</coordinates>\n</Point>\n")
        k.write("</Placemark>\n")

# write to the kml output
with open("tornatoAU.kml", "w") as k:
    k.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    k.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\"\n>")
    k.write("<Document>\n")
    k.write("<Folder>\n<name>F0</name>\n")
    foldus(k, outF0)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>F1</name>\n")
    foldus(k, outF1)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>F2</name>\n")
    foldus(k, outF2)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>F3</name>\n")
    foldus(k, outF3)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>F4</name>\n")
    foldus(k, outF4)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>F5</name>\n")
    foldus(k, outF5)
    k.write("</Folder>\n")
    k.write("</Document>\n</kml>")
