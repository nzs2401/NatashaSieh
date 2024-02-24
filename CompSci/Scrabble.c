// Natasha Sieh
// 1/5/22
// Period 4
// Scrabble Lab

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/*
Includes 1 function named compute_score: looks at each letter in the word and adds the value of that word. This function does it for both word1 and word2.
*/

// Points assigned to each letter of the alphabet
int POINTS[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};
// declare a function named 'compute_score' that takes in a string named 'word'
int compute_score(string word);

int main(void)
{
    // TODO: Declare all variables
    string word1 = get_string("Player 1: ");
    string word2 = get_string("Player 2: ");
    int score1 = compute_score(word1);
    int score2 = compute_score(word2);

    // Print the winner
    if (score1 > score2)
    {
        printf("Player 1 wins!!!\n");
    }

    if (score1 < score2)
    {
        printf("Player 2 wins!!!\n");
    }

    if (score1 == score2)
    {
        printf("Tie!!!\n");
    }
}

// defines what the funciton compute_score does
int compute_score(string word)
{
    // start the points at zero
    int countPoints = 0;

    // for loop for starting at the beginning of the word and stops at the end
    for (int i = 0; i < strlen(word); i++)
    {
        // uppercase
        if (isupper(word[i]))
        {
            // uppercase = 65 to 90
            countPoints = countPoints + POINTS[word[i] - 65];
        }

        // lowercase
        if (islower(word[i]))
        {
            // lowercase = 97 to 122
            countPoints = countPoints + POINTS[word[i] - 97];
        }
        // prints all letter values
        //printf("%i", countPoints);
    }
    // returns countPoints, which is the math part
    return countPoints;
}
