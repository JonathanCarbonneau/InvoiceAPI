import json
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates

templates = read_templates('Template/')  # load templates
result = extract_data('testcase/NOM220601094974R001-1-49228530.pdf',templates=templates)  # writes pdf to dictionary result

# converts currency data to a float value
def currency_data_to_foat(ammount):
    return float(ammount.replace(',', '').replace('$', ''))


# data is a nested dict this pulls the first list
summary_by_day = result["SUMMARY BY DAY"]

print(currency_data_to_foat(result['Fees'][1]) - currency_data_to_foat(result['Total_Interchange_Charges'][1])) 

# Test for loop
total = 0
counter = 0
for day in summary_by_day:
    # print(day)
    submitted_amount = currency_data_to_foat(day['Submitted_Amount'])
    total += submitted_amount
    counter += 1
    #print("Total:", total)
print("Mean", total/counter)
