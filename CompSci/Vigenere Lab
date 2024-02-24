// Natasha Sieh
// 1/14/22
// Period 4
// Vigenere Lab

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

//string cypher_function(string plainText, int key);

string cypher_function(string plainText, int SHIFT[], int keywordCount)
{
    // integer variable for where the shift location is in the plaintext
    int shiftLoc = 0;
    // char for the variable that stores the math behind the shifting process
    char cypher1;
    //printf("%s\n", plainText);

    /*
    // for loop to store each letter in key to an array
    for (int z = 0; z < keywordCount; z++)
    {
        printf("%i\n", SHIFT[z]);
    }
    */

    // for loop to go through the plaintext, check if it is an alphabetical letter, is upper or lower case, and goes through the shift number
    for (int y = 0; y <= strlen(plainText); y++)
    {
        if (isalpha(plainText[y]))
        {
            if (isupper(plainText[y]))
            {
                cypher1 = (char)((((int)(plainText[y] + SHIFT[shiftLoc]) - 65) % 26) + 65);
            }

            if (islower(plainText[y]))
            {
                cypher1 = (char)((((int)(plainText[y] + SHIFT[shiftLoc]) - 97) % 26) + 97);
            }
            plainText[y] = cypher1;
            //printf("Character: %c\n", cypher1);
            // increase the shift location every time
            shiftLoc++;
            // if the shift location is greater than the inputted length of the key - 1, set the shift location to 0 to start from the beginning of the key that was inputted
            if (shiftLoc > keywordCount - 1)
            {
                shiftLoc = 0;
            }
            //printf("ShiftLoc: %i\n", shiftLoc);
        }

        /*
        // if it is not a character, leave it as it is
        else
        {
            //printf("Character: %c\n", plainText[y]);
        }
        */
    }
    return plainText;
}

int main(int argc, string argv[])
{
    // variable for the amount of letters in the inputted key
    int keywordCount;
    string plainText;
    // creates an array of 100 letters to store as the different shift numbers
    int SHIFT[100];
    //printf("%c", argc);

    // if statement for if the argument count is not equal to 2
    if (argc != 2)
    {
        printf("Usage: ./vigenere key\n");
        return 1;
    }

    // for loop to go through the inputted key and check if it is alphabetical
    for (int z = 0; z < strlen(argv[1]); z++)
    {

        if (!isalpha(argv[1][z]))
        {
            printf("Usage: ./vigenere key\n");
            //printf("%c", argv[1][z]);
            return 1;
        }
    }

    // for loop to go through the argv[1]
    for (int w = 0; w <= strlen(argv[1]); w++)
    {
        // ALL upercase: if statement that converts char to int (decimal), calculates the shift number, and stores it into an array called SHIFT[]
        if (isupper(argv[1][w]))
        {
            //printf("%c\n", argv[1][w]);
            SHIFT[w] = (int) argv[1][w] - 65;
            //printf("%i\n", SHIFT[w]);
        }

        // ALL lowercase: if statement that converts char to int (decimal), calculates the shift number, and stores it into an array called SHIFT[]
        if (islower(argv[1][w]))
        {
            //printf("%c\n", argv[1][w]);
            SHIFT[w] = (int) argv[1][w] - 97;
            //printf("%i\n", SHIFT[w]);
        }
    }

    // keyword count is equal to the length of argv[1]
    keywordCount = strlen(argv[1]);
    // get the input from plaintext:
    plainText = get_string("plaintext: ");
    // prints the ciphertext: and calls the function
    printf("ciphertext: %s\n", cypher_function(plainText, SHIFT, keywordCount));
    return 0;
}
