# final.py
# Natasha Sieh
# 6/22/22
# Python 3.10.4
# Description: You may not use the built-in python functions: sum(), average(), sort(), sorted(), median()

'''
A) Use a loop to make 10 random numbers between 20 and 30, store them in a variable numList  .
( Hint: use numList.append(number), where number is a randomint between 20 and 30 )
B) Write a function to Sort the list using the bubble sort you learned in this class.
C) Write a function to Show the sorted list and the unsorted list, array is shown one element per line.
D) Write a function to Find the sum, average, smallest and largest of the numbers in numList . 
E) Write a function to Find the median of the list.
  (Hint for 10 numbers the median is the average of the two numbers in the middle)
F) Write a function to Show how many numbers are evenly divisible by 2
G) Copy/paste the Output of your program (A-F) as a multiline comment at the bottom of your program.
'''

### Use a LOOP to make 10 random numbers between 20 and 30, store them in a variable numList ###

from random import randint # setting up for randint()
numList = [] # empty list
for i in range(0, 10,1):
    # Start: 0
    # Stop: 10
    # Step: 1
    num = randint(20,30) # between 20 and 30
    numList.append(num) # append
    x = numList

### Write a FUNCTION to Show the UNSORTED list, array is shown one element per line ###
def unsorted(): # new function called unsorted
    print("Unsorted: ", numList)
    for i in range(0, len(numList),1):
        print(numList[i])
     # end the function
unsorted() # call the function

### Write a FUNCTION to Sort the list using the bubble sort you learned in this class ###

def Bubble_Sort(numList): # function for bubble sorting
    for j in range(0, len(numList), 1):
        for i in range(0, len(numList)-1, 1): 
            if numList[i] > numList[i+1]:
                temp = numList[i]
                numList[i] = numList[i+1]
                numList[i+1] = temp
    return numList
    y = Bubble_Sort(numList)
print()

### Write a FUNCTION to Show the SORTED list, array is shown one element per line ###

def ordered(): # new function called unsorted
    print()
    print("Bubble Sorted: ", Bubble_Sort(numList))
    print()
    for i in range(0, len(numList),1):
        print(numList[i])
        # end the function
ordered() # call the function

### Write a FUNCTION to find the sum, average, smallest and largest of the numbers in numList ###
print()
def s_a_s_l():
    # SUM
    sum = 0
    for index in range(0, len(numList),1):
        sum = sum + numList[index]
    print("Sum =", sum)

    # AVERAGE
    avg = sum / len(numList)
    print("Average =", sum, "/", len(numList),"= %0.1f" %avg)

    # SMALLEST NUMBER
    smallest_min = numList[0]
    for i in range(0,len(numList),1):
        if numList[i] < smallest_min:
            smallest_min = numList[i]
    print("Smallest =", smallest_min)

    # LARGEST NUMBER
    largest_min = numList[0]
    for i in range(0,len(numList),1):
        if numList[i] > largest_min:
            largest_min = numList[i]
    print("Largest =", largest_min)
    return

s_a_s_l() # calling the sum_average_smallest_largest (s_a_s_l) function

### Write a function to Find the median of the list ###
def median():
    medianIndex2 = int(len(numList) / 2) 
    medianIndex1 = medianIndex2 - 1
    median = (int(numList[medianIndex1]) + int(numList[medianIndex2]) )/ 2
    print("Median = ", median)
    return

median() # calling the median function

### Write a function to show how many numbers are evenly divisible by 2 ###

def even(): # function for finding even numbers in the list
    count = 0 # start the count at 0

    for n in numList:
        if (n % 2 == 0): # if any number is even
            count += 1 # add 1 to the count if any number in the list is even
            print(n, "is even")
    print("There were", count, "numbers that are evenly divisible by 2.")
    return

even() # calling the function even()

'''
>>>
================= RESTART: /Users/natashasieh/Desktop/final.py =================
Unsorted:  [29, 26, 23, 21, 21, 29, 21, 28, 25, 29]
29
26
23
21
21
29
21
28
25
29


Bubble Sorted:  [21, 21, 21, 23, 25, 26, 28, 29, 29, 29]

21
21
21
23
25
26
28
29
29
29

Sum = 252
Average = 252 / 10 = 25.2
Smallest = 21
Largest = 29
Median =  25.5
26 is even
28 is even
There were 2 numbers that are evenly divisible by 2.
>>>
'''














    
