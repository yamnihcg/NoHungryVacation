#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 20:35:44 2019

@author: yamnihcg
"""
#Necessary Imports 
import requests
import json
import datetime
from datetime import date
from datetime import timedelta

#Businness Search API Request Information headers, url, api_key)
api_key = 'taiZp9tjrx35L7DjcznI97roBu-KCSW-hJ9Dp1jJ8bCLlkhGVHCGR8HFmC33h4N-DxDo9LsiV5-yyiCmUXKtAyHiH8J-Rm2YwkqGUna51M7Z1o5yZmXzDjo-l4FcXXYx'
businessSearchHeaders = {'Authorization': 'Bearer %s' % api_key}
businessSearchURL = 'https://api.yelp.com/v3/businesses/search'

# Helper functions to parse API data to generate menu 

from menuBuilderHelperFunctions import determineTicker
from menuBuilderHelperFunctions import timeStringToMilitaryTime
from menuBuilderHelperFunctions import validTime
from menuBuilderHelperFunctions import removeDuplicates
from menuBuilderHelperFunctions import getListOfWeekdayIndexes
from menuBuilderHelperFunctions import returnAddressAndNameString
from menuBuilderHelperFunctions import weekdayInformation
from menuBuilderHelperFunctions import weekdayNames

# Function to handle cuisine name input (CLI requests cuisine name input one by one)

def getCuisineNames():
    cuisineArray = []
    while(True):
        cuisineInput = input("Enter cuisines that you like. If you want to stop adding cuisines, type STOP ")
        filteredCuisineInput = cuisineInput.strip()
        tempCopy = cuisineInput.upper()
        if(tempCopy == 'STOP'):
            return cuisineArray
        else: 
            cuisineArray.append(filteredCuisineInput)
            continue

#User Inputs 
name = input("What's your name?   ")
name = name.strip()      
location = input("Which city are you currently located in?  ")
location = location.strip()
stateAbbreviation = input("Which state are you located in. Use an abbreviation for convenience sake (Ex: CA, WA, NY)?   ")
stateAbbreviation = stateAbbreviation.strip()
cuisineTypes = getCuisineNames()
budget = input("What is the most you would spend for a single lunch or dinner? ")
budget = budget.strip()
startYear = int(input("What year do you want to start the plan on? Ex: 2017    "))
startMonth = int(input("What month do you want to start the plan on? Ex: Enter 3 for March    "))
startDay = int(input("What day do you want to start the plan? Ex: 21   "))
endYear = int(input("What year do you want to end the plan on? Ex: 2017    "))
endMonth = int(input("What month do you want to end the plan on? Ex: Enter 3 for March    "))
endDay = int(input("What day do you want to start the plan? Ex: 21   "))
print("Retrieving your restaurants......")


#Relevant parameters to judge how many restaurants to select 

budgetTicker = determineTicker(budget)
fullLocationInfo = location + ", " + stateAbbreviation
startDate = datetime.datetime(startYear, startMonth, startDay)
endDate = datetime.datetime(endYear, endMonth, endDay)
rangeStartDate = date(startYear, startMonth, startDay)
rangeEndDate = date(endYear, endMonth, endDay)
tripLength = abs(endDate-startDate).days + 1
tripLength = tripLength * 2

# Account for Lunch+Dinner

#Extra 10 suggestions if user doesn't like their current menu

tripLength = tripLength + 10

def getRangeOfDatesInHyphenFormat(rangeStartDate, rangeEndDate): 
    listOfDays = []
    delta = rangeEndDate - rangeStartDate
    for i in range(delta.days + 1):
        day = rangeStartDate + timedelta(days=i)
        day = str(day)
        listOfDays.append(day)
    return listOfDays

rangeOfDates = getRangeOfDatesInHyphenFormat(rangeStartDate, rangeEndDate)
def getRangeOfDates():
    return rangeOfDates

tripLength = abs(endDate - startDate).days + 1
startWeekday = startDate.weekday()
endWeekday = endDate.weekday()
numericalListOfWeekdays = getListOfWeekdayIndexes(startWeekday, endWeekday)
actualWeekdays = weekdayNames(numericalListOfWeekdays)

def getActualWeekdays():
    return actualWeekdays

ratingToAddressMap = {}
nameToIDMap = {}

'''
This function makes a Yelp Business Search API request. The request retrieves information about restaurants that 
have the specified cuisine type and are near the location specified by the user. 
'''

def makeBusinessSearchAPIRequest(cuisineType, fullLocationInfo, businessSearchParams, businessSearchHeaders):
    businessSearchParams = {'term': cuisineType,'location': fullLocationInfo}
    businessSearchReq = requests.get(businessSearchURL, params=businessSearchParams, headers=businessSearchHeaders)
    cuisineSpecificResp = json.loads(businessSearchReq.text)
    return cuisineSpecificResp

#Obtaining all the Available Restaurants according to the budgets(first filter)

''' This function returns the restaurant ID's of all businesses that are in the price range of the user. '''

def filterBusinessesByBudget(listOfBusinesses, budgetTicker):
    budgetIDList = []
    for i in range(len(listOfBusinesses['businesses'])):
        if 'price' in listOfBusinesses['businesses'][i].keys():
            if listOfBusinesses['businesses'][i]['price'] in budgetTicker:
                budgetIDList.append(listOfBusinesses['businesses'][i]['id'])
    return budgetIDList

''' This function returns a list of all unique ratings of restaurants, given the businessID 
of all restaurants that match our desired cuisine types and budget. The function also maps 
each unique rating to the list of restaurants that have that rating. '''

def getDuplicateRatingsArray(allBusinessesID):
    ratingsArray = []
    for b in range(len(allBusinessesID)):
        businessContentHeaders2 = {'Authorization': 'Bearer %s' % api_key}
        businessContentURL2 = "https://api.yelp.com/v3/businesses/" + allBusinessesID[b]
        postFilterInformationRequest = requests.get(businessContentURL2, headers=businessContentHeaders2)
        postFilterContentResp = json.loads(postFilterInformationRequest.text)
        currentRating = postFilterContentResp['rating']
        ratingsArray.append(currentRating)
        address = postFilterContentResp['location']['display_address']
        name = postFilterContentResp['name']
        nameToIDMap[name] = allBusinessesID[b]
        addressFiltered = returnAddressAndNameString(address, name)
        #Mapping of Restaurant Rating to Name and Address Information
        try:
            ratingToAddressMap[str(currentRating)]
            tempRemoved = ratingToAddressMap[str(currentRating)]
            tempRemoved.append(addressFiltered)
            ratingToAddressMap[str(currentRating)] = tempRemoved
        except KeyError:
            ratingToAddressMap[str(currentRating)] = [addressFiltered]
    duplicateRatingsArray = ratingsArray
    duplicateRatingsArray.sort(reverse=True)
    duplicateRatingsArray = removeDuplicates(duplicateRatingsArray)
    return duplicateRatingsArray

restaurantToCuisineMap = {}

'''
This function retrieves the Top N Restaurants based on rating after restaurants 
have been filtered based on cuisine and price.
'''

def getFirstNRestaurants(tripLength, completeRatingsArray, ratingToAddressMap):
    curCount = 0
    finalListOfRestaurants = []
    for i in range(tripLength):
        ratingToAddressMap[(str(completeRatingsArray[curCount]))]
        restaurants = ratingToAddressMap[str(completeRatingsArray[curCount])]
        finalListOfRestaurants.append(restaurants[0])
        restaurants = restaurants[1:]
        ratingToAddressMap[(str(completeRatingsArray[curCount]))] = restaurants
        if (ratingToAddressMap[(str(completeRatingsArray[curCount]))] == []):
            curCount = curCount + 1
    return finalListOfRestaurants

lunchTimeAvailability = {}
dinnerTimeAvailability = {}
def getListOfRestaurants():
    allBusinessesID = []
    for cu in range(len(cuisineTypes)):
        businessSearchParams = {'term': cuisineTypes[cu],'location': fullLocationInfo}
        listOfBusinesses = makeBusinessSearchAPIRequest(cuisineTypes[cu], fullLocationInfo, businessSearchParams, businessSearchHeaders)
        budgetFilteredID = filterBusinessesByBudget(listOfBusinesses, budgetTicker)
        for i in range(len(budgetFilteredID)):
            allBusinessesID.append(budgetFilteredID[i])
        
    completeRatingsArray = getDuplicateRatingsArray(allBusinessesID)
    return getFirstNRestaurants(tripLength * 2, completeRatingsArray, ratingToAddressMap)

''' Map for Restaurant ID to Days / Lunch hours '''

def mapIDToLunchHours(postBudgetFilterID, listOfWeekdays, lunchTime, dinnerTime):
    numWeekdays = len(listOfWeekdays)
    lTime = timeStringToMilitaryTime(lunchTime)
    for j in range(len(postBudgetFilterID)):
        businessContentHeaders = {'Authorization': 'Bearer %s' % api_key}
        businessContentURL = "https://api.yelp.com/v3/businesses/" + postBudgetFilterID[j]
        informationRequest = requests.get(businessContentURL, headers=businessContentHeaders)
        contentResp = json.loads(informationRequest.text) 
        if len(contentResp["hours"][0]["open"]) == 7:
            for k in range(numWeekdays):
                lowerBound = int(contentResp["hours"][0]["open"][listOfWeekdays[k]]["start"])
                upperBound = int(contentResp["hours"][0]["open"][listOfWeekdays[k]]["end"])
                #Handle functionality to add multiple days into the map without replacing previous values
                if validTime(lTime, lowerBound, upperBound):
                    try:
                        tempValue = lunchTimeAvailability[postBudgetFilterID[j]]
                        tempValue.append(str(True) + " , " + weekdayInformation(listOfWeekdays[k]))
                        lunchTimeAvailability[postBudgetFilterID[j]] = tempValue
                    except KeyError: 
                        availabilityArray = [str(True) + " , " + weekdayInformation(listOfWeekdays[k])]
                        lunchTimeAvailability[postBudgetFilterID[j]] = availabilityArray
                else:
                    try:
                        tempValue = lunchTimeAvailability[postBudgetFilterID[j]]
                        tempValue.append(str(False) + " , " + weekdayInformation(listOfWeekdays[k]))
                        lunchTimeAvailability[postBudgetFilterID[j]] = tempValue
                    except KeyError: 
                        availabilityArray = [str(False) + " , " + weekdayInformation(listOfWeekdays[k])]
                        lunchTimeAvailability[postBudgetFilterID[j]] = availabilityArray
    return lunchTimeAvailability

def getLunchTimeAvailability(): 
    return lunchTimeAvailability

''' Map for Restaurant ID to Days / Dinner Hours '''

def mapIDToDinnerHours(postBudgetFilterID, listOfWeekdays, lunchTime, dinnerTime):
    numWeekdays = len(listOfWeekdays)
    dTime = timeStringToMilitaryTime(dinnerTime)
    for j in range(len(postBudgetFilterID)):
        businessContentHeaders = {'Authorization': 'Bearer %s' % api_key}
        businessContentURL = "https://api.yelp.com/v3/businesses/" + postBudgetFilterID[j]
        informationRequest = requests.get(businessContentURL, headers=businessContentHeaders)
        contentResp = json.loads(informationRequest.text) 
        if len(contentResp["hours"][0]["open"]) == 7:
            for k in range(numWeekdays):
                lowerBound = int(contentResp["hours"][0]["open"][listOfWeekdays[k]]["start"])
                upperBound = int(contentResp["hours"][0]["open"][listOfWeekdays[k]]["end"])
                if validTime(dTime, lowerBound, upperBound):
                    try:
                        tempValue = dinnerTimeAvailability[postBudgetFilterID[j]]
                        tempValue.append(str(True) + " , " + weekdayInformation(listOfWeekdays[k]))
                        dinnerTimeAvailability[postBudgetFilterID[j]] = tempValue
                    except KeyError: 
                        availabilityArray = [str(True) + " , " + weekdayInformation(listOfWeekdays[k])]
                        dinnerTimeAvailability[postBudgetFilterID[j]] = availabilityArray
                else:
                    try:
                        tempValue = dinnerTimeAvailability[postBudgetFilterID[j]]
                        tempValue.append(str(False) + " , " + weekdayInformation(listOfWeekdays[k]))
                        dinnerTimeAvailability[postBudgetFilterID[j]] = tempValue
                    except KeyError: 
                        availabilityArray = [str(False) + " , " + weekdayInformation(listOfWeekdays[k])]
                        dinnerTimeAvailability[postBudgetFilterID[j]] = availabilityArray
    return dinnerTimeAvailability

def getDinnerTimeAvailability():
    return dinnerTimeAvailability

def main(): 
    print(getListOfRestaurants())
    
if __name__ == "__main__":
    main()




    
