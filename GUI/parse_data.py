import csv

def parse_files():
    NORMAL_FILE = "../Data/cs01_no_ls.csv"
    RAS_FILE = "../Data/cs01_with_dufls_[VR].csv"

    normalFile = open(NORMAL_FILE, 'r') 
    rasFile = open(RAS_FILE, 'r')

    normalReader = csv.reader(normalFile)
    rasReader = csv.reader(rasFile)

    normalReadings = [row[1] for row in normalReader]
    rasReadings = [row[1] for row in rasReader]

    normalFile.close()
    rasFile.close()

    return normalReadings, rasReadings

print parse_files()
