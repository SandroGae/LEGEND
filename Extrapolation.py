# Formula: A(t) = A_0 * exp(-lamda*t)
# Calculating the decay constant lamda: lamda = -[ln(A_2 / A_1)/(t_2 - t_1)]
import math
from datetime import datetime
import numpy as np


data_21 = [
    {"sample": 1, "date": "9. Feb. 2021", "value": 2922},
    {"sample": 2, "date": "9. Feb. 2021", "value": 1728},
    {"sample": 3, "date": "9. Feb. 2021", "value": 2603},
    {"sample": 4, "date": "9. Feb. 2021", "value": 2502},
    {"sample": 5, "date": "9. Feb. 2021", "value": 4675},
    {"sample": 6, "date": "9. Feb. 2021", "value": 3337},
    {"sample": 7, "date": "9. Feb. 2021", "value": 6034},
    {"sample": 8, "date": "9. Feb. 2021", "value": 7431},
    {"sample": 9, "date": "9. Feb. 2021", "value": 3977},
    {"sample": 10, "date": "9. Feb. 2021", "value": 266},
    {"sample": 11, "date": "9. Feb. 2021", "value": 2093},
    {"sample": 12, "date": "9. Feb. 2021", "value": 6087},
    {"sample": 13, "date": "9. Feb. 2021", "value": 5567},
    {"sample": 14, "date": "9. Feb. 2021", "value": 5521},
    {"sample": 15, "date": "9. Feb. 2021", "value": 6278},
    {"sample": 16, "date": "9. Feb. 2021", "value": 4322}
]

data_23 = [
    {"sample": 1, "date": "27 Oct 2023", "value": 1086.29},
    {"sample": 2, "date": "27 Oct 2023", "value": 642.41},
    {"sample": 3, "date": "27 Oct 2023", "value": 967.70},
    {"sample": 4, "date": "27 Oct 2023", "value": 930.15},
    {"sample": 5, "date": "27 Oct 2023", "value": 1738.00},
    {"sample": 6, "date": "27 Oct 2023", "value": 1240.58},
    {"sample": 7, "date": "27 Oct 2023", "value": 2243.22},
    {"sample": 8, "date": "27 Oct 2023", "value": 2762.58},
    {"sample": 9, "date": "27 Oct 2023", "value": 1478.50},
    {"sample": 10, "date": "27 Oct 2023", "value": 98.89},
    {"sample": 11, "date": "27 Oct 2023", "value": 778.10},
    {"sample": 12, "date": "27 Oct 2023", "value": 2262.93},
    {"sample": 13, "date": "27 Oct 2023", "value": 2069.61},
    {"sample": 14, "date": "27 Oct 2023", "value": 2052.51},
    {"sample": 15, "date": "27 Oct 2023", "value": 2333.93},
    {"sample": 16, "date": "27 Oct 2023", "value": 1606.76}
]

def calc_decay_constant(value1, value2, time1, time2):
    decay_constant = -math.log(value2 / value1) / (time2 - time1)
    return decay_constant

def predict_activity(initial_value, decay_constant, seconds):
    predicted_activity = initial_value * math.exp(-decay_constant * seconds)
    return predicted_activity

# Taking the current date for our calculations
current_date = datetime.now()
day = current_date.day
month = current_date.month
year = current_date.year

# Time difference for the two measurements taken
date_format = "%d %b %Y"
start_date = datetime.strptime("9 Feb 2021", date_format)
end_date = datetime.strptime("27 Oct 2023", date_format)
time_difference = (end_date - start_date).total_seconds() # in seconds

# Calculating the decay constant
decay_constant_list = []
for i in range(0, len(data_21), 1):
    decay_constant_list.append(calc_decay_constant(data_21[i]['value'], data_23[i]['value'], 0, time_difference))

real_decay_constant = np.mean(decay_constant_list)
time_difference_today = (current_date - end_date).total_seconds()


current_mass_list = []
for k in range(0, len(data_21), 1):
    # Value of 2023 taken and the time is the difference from 27.10.2023 to today
    current_activity = predict_activity(data_23[k]['value'], real_decay_constant, time_difference_today)
    # Mass can be calculated using: producing one Bq needs 0.06 microgram of Th228
    mass = 0.06 *10**-6 * current_activity #in grams
    current_mass_list.append(mass)
    #print(f'The current mass for source {k + 1} is {round(mass,8)} gram')