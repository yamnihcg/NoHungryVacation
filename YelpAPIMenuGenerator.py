#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 00:07:11 2019

@author: yamnihcg
"""

api_key = 'taiZp9tjrx35L7DjcznI97roBu-KCSW-hJ9Dp1jJ8bCLlkhGVHCGR8HFmC33h4N-DxDo9LsiV5-yyiCmUXKtAyHiH8J-Rm2YwkqGUna51M7Z1o5yZmXzDjo-l4FcXXYx'

from restaurantSelector import getActualWeekdays
from restaurantSelector import getRangeOfDates
from restaurantSelector import getListOfRestaurants
from restaurantSelector import name

''' Information necessary ''' 
weekdayNames = getActualWeekdays()
actualDates = getRangeOfDates()
listOfRestaurants = getListOfRestaurants()

''' Helper Function: Split Name and Address in Restaurant Description '''

def separateNameAndAddress(restaurant):
    stoppingIndex = 0
    for i in range(len(restaurant)):
        if restaurant[i:i+8] == 'Address:':
            stoppingIndex = i 
    return [restaurant[0:stoppingIndex], restaurant[stoppingIndex:len(restaurant)]]

''' Formats the final .txt file output '''

def writeThePlanningFile(listOfRestaurants):
    finalPlannerFile = open(name + "TripMenu.txt", "w+")
    meals = ['Lunch', 'Dinner']
    resCount = 0 
    for k in range(len(actualDates)):
        finalPlannerFile.write(weekdayNames[k] + ", " + actualDates[k] + '\n')
        for i in range(len(meals)):
            finalPlannerFile.write(meals[i] + '\n')
            nameAndAddress = separateNameAndAddress(listOfRestaurants[resCount] + '\n') 
            finalPlannerFile.write(nameAndAddress[0] + '\n')
            finalPlannerFile.write(nameAndAddress[1] + '\n')
            resCount = resCount + 1
    finalPlannerFile.write('\n')
    finalPlannerFile.write('\n')
    finalPlannerFile.write('\n')
    finalPlannerFile.write('If you did not like the suggested menu, here are some other restaurants that match your preferences!')
    finalPlannerFile.write('\n')
    finalPlannerFile.write('\n')
    for b in range(resCount, len(listOfRestaurants)):
        nameAndAddress = separateNameAndAddress(listOfRestaurants[b] + '\n') 
        finalPlannerFile.write(nameAndAddress[0] + '\n')
        finalPlannerFile.write(nameAndAddress[1] + '\n')
writeThePlanningFile(listOfRestaurants)
print('File writing complete! Check ' + name + 'TripMenu.txt for your meal plan')






