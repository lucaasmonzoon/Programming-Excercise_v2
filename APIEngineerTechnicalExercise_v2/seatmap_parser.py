#Notes:
#    I assumed on both files that each one of the "element type" are seats 
#    because I did not find references to that property on the XML file.

import sys
import json
import xml.etree.ElementTree as ET

###############################################################################################
dictionary_rows = {} # Dict that stores the following properties: SeatID, seatPrice, Availability, CabinClass and Element Type.
id_prices = {} # Dict that stores the OfferItemID and their respective price
price_amount = [] # A List that stores the prices as a float in GBP
###############################################################################################
# Here I obtain the desired seatmap's path, which should be in the same folder as the script
# The seadmap should be put as an argument in the terminal when you run the script (ie. python seatmap_parser.py seatmap2.xml)
path = sys.argv[1]

if path =='seatmap2.xml':
    #CODE FOR SEATMAP2:

    seatmap2 = ET.parse(path)
    root=seatmap2.getroot()

    ###############################################################################################
    
    dictionary_rows = {} # Dict that stores the following properties: SeatID, seatPrice, Availability and Element Type.
    id_prices = {} # Dict that stores the OfferItemID and their respective price
    price_amount = [] # A List that stores the prices as a float in GBP

    # Here I try to obtain the XML elements that contains the seat's prices and their IDs by using list comprehension
    prices = [child for child in root.iter() if child.tag == '{http://www.iata.org/IATA/EDIST/2017.2}ALaCarteOfferItem']

    # A loop that parses through the XML elements that contains the prices of the seats and
    # the attribute of each one, then appends every one of them to the price_amount list.
    for price in prices:
        for elements in price.iter():
            if elements.tag == '{http://www.iata.org/IATA/EDIST/2017.2}SimpleCurrencyPrice':
                price_amount.append(float(elements.text))

    # Here I complete the dictionary by putting the OfferItemID attribute as the key of each data value, and the
    # price as the value of that key.
    for i in range(len(price_amount)):
        id_prices[prices[i].attrib["OfferItemID"]] = price_amount[i]

    ###############################################################################################
    #Positions:
    positions={}
    for child in root.iter():
        if child.tag == '{http://www.iata.org/IATA/EDIST/2017.2}Columns':
            if child.text==None:
                positions[child.attrib['Position']]='CENTER'
            else:
                 positions[child.attrib['Position']]=child.text
    
    # Another variable using list comprenhension to obtain all of the rows of the seatmap, by comparing
    # the tagname of the XML elements to 'Row'
    rows_list = [child for child in root.iter() if child.tag == '{http://www.iata.org/IATA/EDIST/2017.2}Row'] 

    # Main loop that goes through the rows obtained in rows_list, then parses along each one of the elements of those rows,
    # being the majority of those elements the seats, which I then obtain the data of the seatID, seatPrice (by using the
    # dictionary 'dictionary_rows') and their availability.
    # Then, I put them all on a dictionary organized by rows and their respective seats.
    for row in rows_list:
        seat_list = []
        for elements in row.iter():
            seat_dict = {}
            if elements.tag == '{http://www.iata.org/IATA/EDIST/2017.2}Number':
                row_number = elements.text
            elif elements.tag =='{http://www.iata.org/IATA/EDIST/2017.2}Seat':
                for child in elements.iter():
                    seat_dict['Element Type']="Seat"
                    # In the "seatemap2.xml" I did not find any mention of the property "Cabin class".
                    seat_dict['Cabin Class']='Not specified'

                    if child.tag == '{http://www.iata.org/IATA/EDIST/2017.2}Column':
                        columna = child.text
                        seat_dict['seatID'] = str(row_number + columna)
                        seat_dict['Position'] = positions[columna]
                    elif child.tag == '{http://www.iata.org/IATA/EDIST/2017.2}OfferItemRefs':
                        seat_dict['seatPrice'] = id_prices[child.text]
                        seat_dict['Availability'] = True
                    elif child.text == 'SD11' or child.text == 'SD19' or child.text=='SD22':
                        seat_dict['Availability'] = False
                        seat_dict['seatPrice'] = None
                    
        
                seat_list.append(seat_dict)
        dictionary_rows['row_' + str(row_number)] = seat_list
    
    # Here I create the json file
    with open('seatmap2_parsed.json', 'w') as outfile:
        json.dump(dictionary_rows, outfile,indent = 4)
elif path == 'seatmap1.xml':

    #CODE FOR 'SEATMAP1.XML:'

    seatmap1 = ET.parse(path)
    root = seatmap1.getroot()
    #Function that shifts the decimal place n times, where n is given as an argument to the function.
    def realprice(price, decimal):
        for i in range(abs(decimal)):

                if decimal>0:
                    price /= 10
                else:
                    price *= 10

        return float(price)

    # Another variable using list comprenhension to obtain all of the rows of the seatmap, by comparing
    # the tagname of the XML elements to 'RowInfo'.

    rows_list = [child for child in root.iter() if child.tag == '{http://www.opentravel.org/OTA/2003/05/common/}RowInfo']

    # Main loop that goes through the rows obtained in rows_list, then parses along each one of the elements of those rows,
    # being the majority of those elements the seats, which I then obtain the data of the seatID, seatPrice (by using the
    # dictionary 'dictionary_rows') and their availability.
    # Then, I put them all on a dictionary organized by rows and their respective seats.
    
    for child in rows_list:
        seat_list = []
        row_number2 = child.attrib['RowNumber']
        for child1 in child.iter():
            if child1.tag == '{http://www.opentravel.org/OTA/2003/05/common/}SeatInfo':
                seat_dict = {}
                for seats in child1.iter():
                    if seats.tag == '{http://www.opentravel.org/OTA/2003/05/common/}Summary':
                        seat_dict['Element type'] = 'Seat'
                        seat_dict['Position'] = ''
                        seat_dict['Cabin Class'] = child.attrib['CabinType']
                        seat_dict['SeatID'] = seats.attrib['SeatNumber']
                        availability = seats.attrib['AvailableInd']
                        if availability == 'true':
                            seat_dict['Available'] = True
                        else:
                            seat_dict['Available'] = False
                            
                        seat_dict['seatPrice'] = None
                    elif seats.tag == '{http://www.opentravel.org/OTA/2003/05/common/}Features' and seats.text != 'Other_':
                        seat_dict['Position'] = seats.text.upper()
                    elif seats.tag == '{http://www.opentravel.org/OTA/2003/05/common/}Fee':
                        decimalplace = int(seats.attrib['DecimalPlaces'])
                        seat_dict['seatPrice'] = realprice(int(seats.attrib['Amount']),decimalplace)

                
                seat_list.append(seat_dict)
            

        dictionary_rows['row_' + str(row_number2)] = seat_list

    
    # Here I create the json file
    with open('seatmap1_parsed.json', 'w') as outfile:
        json.dump(dictionary_rows, outfile,indent = 4)
else:
    print("Wrong file path")




