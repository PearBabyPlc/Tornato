egFH = "ACM00078861  17.1170  -61.7830   10.0"
lenFH = len(egFH)
egLT = "1947 1993  13896"
lenLT = len(egLT) + 1

stationsActive = []
stationsNew = []
stationsInactive = []
with open("igra2-station-list.txt", newline="\n") as txt:
    for row in txt:
        firstHalf = row[:lenFH]
        secondHalf = row[lenFH:]

        oneSplit = firstHalf.split(" ")
        revSecond = secondHalf[::-1]
        threeRev = revSecond[:lenLT]
        twoRev = revSecond[lenLT:]
        two = twoRev[::-1]
        three = threeRev[::-1]

        one = []
        for x in oneSplit:
            if (x != ''):
                one.append(x)

        # why tf doesn't this fucking work
        #ID = one[0]
        #lat = one[1]
        #lon = one[2]
        #alt = one[3]

        # this doesnt work either bruh wtaf
        #ID = one[-4]
        #lat = one[-3]
        #lon = one[-2]
        #alt = one[-1]

        # why does this of all fucking things work
        it = 0
        ID = str()
        lat = str()
        lon = str()
        alt = ()
        for x in one:
            it += 1
            if (it == 1): ID = x
            if (it == 2): lat = x
            if (it == 3): lon = x
            if (it == 4): alt = x
            if (it >= 5): break

        name = two.strip()

        threeList = three.split(" ")
        start = threeList[0].strip()
        end = threeList[1].strip()
        samples = threeList[-1].strip("\n")

        station = (ID, lat, lon, alt, name, start, end, samples)
        #stations.append(station)
        endInt = int(end.strip())
        startInt = int(start.strip())
        if (endInt >= 2025):
            if (startInt >= 2000):
                stationsNew.append(station)
            else:
                stationsActive.append(station)
        else:
            stationsInactive.append(station)

print("     (active means up to 2025)")
print("==========ACTIVE=STATIONS==========")
for x in stationsActive:
    print("ID:", x[0])
    print("Lat:", x[1])
    print("Lon:", x[2])
    print("Alt:", x[3])
    print("Name:", x[4])
    print(x[5], "to", x[6], "with", x[7], "samples\n")
print()
print("      (new means after 2000)")
print("===========NEW=STATIONS============")
for x in stationsNew:
    print("ID:", x[0])
    print("Lat:", x[1])
    print("Lon:", x[2])
    print("Alt:", x[3])
    print("Name:", x[4])
    print(x[5], "to", x[6], "with", x[7], "samples\n")
print()
print("=========INACTIVE=STATIONS=========")
for x in stationsInactive:
    print("ID:", x[0])
    print("Lat:", x[1])
    print("Lon:", x[2])
    print("Alt:", x[3])
    print("Name:", x[4])
    print(x[5], "to", x[6], "with", x[7], "samples\n")  
print()

stations = stationsActive + stationsNew + stationsInactive
with open("igra-stations.txt", "w") as md:
    for x in stations:
        xid = x[0]
        xla = x[1]
        xlo = x[2]
        xal = x[3]
        xna = x[4]
        xst = x[5]
        xen = x[6]
        xsa = x[7]
        md.write(f"ID={xid}\nLat={xla}\nLon={xlo}\nAlt={xal}\nName={xna}\nStart={xst}\nEnd={xen}\nSamples={xsa}\n\n")

def foldus(k, out):
    for x in out:
        xid = x[0]
        xla = x[1]
        xlo = x[2]
        xal = x[3]
        xna = x[4]
        xst = x[5]
        xen = x[6]
        xsa = x[7]
        k.write("<Placemark>\n")
        k.write(f"<name>{xid}</name>\n")
        k.write(f"<description>Name: {xna}\nLatitude: {xla}\nLongitude: {xlo}\nAltitude: {xal}\nRange: {xst}-{xen} ({xsa} samples</description>\n")
        k.write(f"<Point>\n<coordinates>{xla},{xlo},{xal}</coordinates>\n</Point>\n")
        k.write("</Placemark>\n")

with open("igra-stations.kml", "w") as k:
    k.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    k.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\"\n>")
    k.write("<Document>\n")
    k.write("<Folder>\n<name>Active</name>/n")
    foldus(k, stationsActive)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>New</name>/n")
    foldus(k, stationsNew)
    k.write("</Folder>\n")
    k.write("<Folder>\n<name>Inacrive</name>/n")
    foldus(k, stationsInactive)
    k.write("</Folder>\n</Document>\n</kml>")
