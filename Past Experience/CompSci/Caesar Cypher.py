# Natash Sieh
# Feburary 25, 2023
# Period 4
# Caesar Cypher Lab

# import library for taking input from terminal
import sys
# import library cs50 to allow getting input
from cs50 import get_string

def main():
    # finds the length of arguments in the command line
    length = len(sys.argv)

    # if the argument does not equal 2 arguments return 1 (error stop)
    if len(sys.argv) != 2:
        print("Usage: ./caesar key")
        exit(1)
    # else if argument equals 2
    elif length == 2:
        # check if each letter is a digit
        for i in range(len(sys.argv[1])):
            if not str.isdigit(sys.argv[1][i]):
                print("Usage: python caesar.py")
                exit(1)
            else:
                # start program
                print('WELCOME TO CAESAR CIPHER!')
                # shift number equals the number the user typed out
                shift_amount = sys.argv[1]

                # user get_string input
                noChange = get_string("Plaintext: ")

                # calls cypher_function
                cypher_function(noChange, shift_amount)
                #print("Try again with proper format")
                exit(0)

# function that ciphers the onoChanged text (PlainText)
def cypher_function(noChange, shift_amount):
    # type of output print
    sys.stdout.write("ciphertext: ")
    # for loop for going through the length of noChange and checking if it is alpha, upper, or lower
    for y in range (len(noChange)):
        # if it is a letter, shift by the equation
        if str.isalpha(noChange[y]):
            # or else if it is uppercase, keep capital
            if str.isupper(noChange[y]):
                cipher = chr(((ord(noChange[y]) + int(shift_amount) - 65) % 26 + 65))
                # prints on the same line
                sys.stdout.write(cipher)

                # if it is lowercase, keep lower case
            elif str.islower(noChange[y]):
                cipher = chr(((ord(noChange[y]) + int(shift_amount) - 97) % 26 + 97))
                # prints on the same line
                sys.stdout.write(cipher)
        # if not a letter, do not shift by the equation
        else:
            if (noChange[y] == ',' or noChange[y] == '.' or noChange[y] == ' ' or noChange[y] == '?' or noChange[y] == '!'):
                sys.stdout.write(noChange[y])
            # if it is a digit, keep it
            elif (str.isdigit(noChange[y])):
                sys.stdout.write(noChange[y])
    print()


# runs the main function
if __name__ == "__main__":
    # call function main
    main()
