############################################ Imports

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from datetime import datetime
import os
import re
import copy

############################################ Variables

global selected_settings
selected_settings = [False, False, False, False, False, True, False, False, False, False, False]

############################################ Get URL

url_base = "https://www.swimmingresults.org/individualbest/personal_best.php?back=individualbestname&mode=A&name=&tiref="
membership_code = int(input("Enter Membership Code : "))
#membership_code = 1574039 //my code
url = url_base + str(membership_code)

############################################  Getting Page Text
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
page_text = soup.get_text()

############################################ Cut Off Everything Before/After Including Phrases

start_phrase = "LicenceLevel"
end_phrase = "Disclosure of your information"

text_lower = page_text.lower()

start_index = text_lower.find(start_phrase.lower())
if start_index != -1:
    start_index += len(start_phrase)
else:
    start_index = 0

end_index = text_lower.find(end_phrase.lower(), start_index)
if end_index == -1:
    end_index = len(page_text)

page_text = page_text[start_index:end_index].strip()

############################################ Split up bulk text to distance, stroke, time, conversion, points

def split_up_2(text):

    #Fix long distance not being outputted
    text = re.sub(r'(Freestyle|Backstroke|Breaststroke|Butterfly|Individual Medley)(?=\d)', r'\1 ', text)
    text = re.sub(r'(?<=\d\.\d{2})(?=\d+:)', r' ', text)

    # Regex pattern: event (distance + stroke), time, conversion, points
    pattern = r'(50|100|200|400|800|1500)m?\s?' \
        r'(Freestyle|Backstroke|Breaststroke|Butterfly|Individual Medley)\s+' \
        r'(\d+:\d+\.\d+|\d+\.\d+)\s*' \
        r'(\d+:\d+\.\d+|\d+\.\d+)\s*' \
        r'(\d{3})\s*' \
        r'(\d{2}/\d{2}/\d{2})'

    # Find all matches
    matches = re.findall(pattern, text)

    # Convert to 2D list
    all_event_data = [list(match) for match in matches]

    #Fix long merged number
    for event_data in all_event_data:
        time_str = str(event_data[3])
        minutes_seconds, decimal_part = time_str.split(".")
        time_decimal = decimal_part[:2]
        event_data[3] = f"{minutes_seconds}.{time_decimal}"
        points = decimal_part[2:5]
        event_data.append(points)

    #Combine Distance and Stroke
    all_event_data = [[row[0] + " " + row[1]] + row[2:] for row in all_event_data]

    for event_data in all_event_data:
        event_data.pop()

    return all_event_data

############################################ Split at split_point to Short Course And Long Course

def split_up_1(text):
    split_point = "Short CourseStrokeSC TimeConverted to LCSC WA PtsDateMeetVenueLicenseLevel"

    start_index = text.find(split_point)
    if start_index != -1:
        end_index = start_index + len(split_point)
        long_course = text[:start_index].strip()
        short_course = text[end_index:].strip()
        short_course = split_up_2(short_course)
        long_course = split_up_2(long_course)
        return short_course, long_course

############################################ Clear Screen

def clear_screen():
    os.system('cls')

############################################ Output Table

def output_table(contents):
    clear_screen()
    copy_contents = copy.deepcopy(contents)
    _headers = ["Event", "Time", "Converion Time", "Points", "Date"]

    #Hide Conversion Time
    if selected_settings[0] == True:
        _headers = ["Event", "Time", "Points", "Date"]
        for event in copy_contents:
            del event[2]

    #Sort by Points (High -> Low)
    if selected_settings[1] == True:
        if selected_settings[0] == True:
            copy_contents = sorted(copy_contents, key=lambda x: x[2], reverse=True)
        else:
            copy_contents = sorted(copy_contents, key=lambda x: x[3], reverse=True)

    #Sort by Points (Low -> High)
    elif selected_settings[2] == True:
        if selected_settings[0] == True:
            copy_contents = sorted(copy_contents, key=lambda x: x[2])
        else:
            copy_contents = sorted(copy_contents, key=lambda x: x[3])

    #Sort By Date (Newest -> Oldest)
    elif selected_settings[3] == True:
        if selected_settings[0] == True:
            copy_contents = sorted(copy_contents, key=lambda x: datetime.strptime(x[3], "%d/%m/%y"), reverse=True)
        else:
            copy_contents = sorted(copy_contents, key=lambda x: datetime.strptime(x[4], "%d/%m/%y"), reverse=True)

    #Sort By Date (Oldest -> Newest)
    elif selected_settings[4] == True:
        if selected_settings[0] == True:
            copy_contents = sorted(copy_contents, key=lambda x: datetime.strptime(x[3], "%d/%m/%y"))
        else:
            copy_contents = sorted(copy_contents, key=lambda x: datetime.strptime(x[4], "%d/%m/%y"))

    #Output Table
    print(tabulate(copy_contents, headers=_headers, tablefmt="fancy_grid"))
    print("\n")
    menu()

############################################ Menu

def menu():
    print("LC | SC | Both | Settings | Exit")
    option = input(":")
    if option == "exit":
        exit()
    elif option == "settings":
        settings()
    elif option == "LC" or option == "lc" or option == "long course":
        output_table(long_course)
    elif option == "SC" or option == "sc" or option == "short course":
        output_table(short_course)
    elif option == "both":
        output_table(lc_and_sc)
    else:
        menu()

############################################ Settings

def settings():
    s_option = -1

    while s_option < 1 or s_option > 5:
        clear_screen()
        print("\n SETTINGS...")
        print("0. Exit")
        print("1. Hide Conversion Time - Currently", selected_settings[0])
        print("2. Sort By Points (High -> Low) - Currently", selected_settings[1])
        print("3. Sort By Points (Low  -> High) - Currently", selected_settings[2])
        print("4. Sort By Date (Newest -> Oldest) - Currently", selected_settings[3])
        print("5. Sort By Date (Oldest -> Newest) - Currently", selected_settings[4])
        print("6. Apply Default Sorting - Currently", selected_settings[5])
        print("7. Hide Butterfly - Currently", selected_settings[6])
        print("8. Hide Backstroke - Currently", selected_settings[7])
        print("9. Hide Breastroke - Currently", selected_settings[8])
        print("10. Hide Freestyle - Currently", selected_settings[9])
        print("11. Hide Individual Medley - Currently", selected_settings[10])

        print("\n Enter Setting")
        s_option = int(input(":"))

        if s_option == 0:
            menu()
        elif s_option == 1:
            selected_settings[0] = not selected_settings[0]
        elif s_option > 1 and s_option < 7:
            selected_settings[1] = False
            selected_settings[2] = False
            selected_settings[3] = False
            selected_settings[4] = False
            selected_settings[5] = False
            selected_settings[s_option - 1] = True
        elif s_option == 7:
            selected_settings[6] = not selected_settings[6]
        elif s_option == 8:
            selected_settings[7] = not selected_settings[7]
        elif s_option == 9:
            selected_settings[8] = not selected_settings[8]
        elif s_option == 10:
            selected_settings[9] = not selected_settings[9]
        elif s_option == 11:
            selected_settings[10] = not selected_settings[10]

        s_option = -1

############################################ Create lc_and_sc

def create_lc_and_sc(long_course, short_course):
    for item in long_course:
        item[0] = "LC " + item[0]

    for item in short_course:
        item[0] = "SC " + item[0]

    lc_and_sc = long_course + short_course
    return lc_and_sc

############################################ Main Code

short_course, long_course = split_up_1(page_text)

lc_and_sc = create_lc_and_sc(long_course, short_course)

menu()