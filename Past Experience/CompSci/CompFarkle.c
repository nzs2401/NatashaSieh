// Farkle Lite

#define _DEFAULT_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <cs50.h>
#include <string.h>
#include <unistd.h> // for the sleep function (delay)

// Goal of this program is to make a dice game named Farkle. Roll 6 dice, count your points that you want to keep, keep rolling if you want to take the risk until you decide that you want to stop. We add up the total points of the roll and compare which player wins. When you roll and get ones, each one counts as 100 points. When you roll fives, each one counts as 50 points. If you roll a triplet (EX: 111, 222,333…), it counts as a certain number of points, which will be in the introduction of the game.

// funtion for checking if an inputted string is valid for my program
int check_string_valid(string keepLetter, char keptDice[2][6], int y, int player[2][6]);
// function for calculating points according to the rules of Farkle
int farkle_points(int diceNumber, int diceValues[]);
// function for how the computer selects rolled dice
string compselectDice(char keptDice[2][6], int player[2][6], int y);
// string variable to store computer kept rolled dice
char keptCompLetters[10];

int main(void)
{
    char start;
    int randomNum;
    char stop = 'C';
    string keepLetter;
    char keptDice[2][6] = {};
    int player[2][6] = {};
    int diceChosen;
    int diceValues[6] = {};
    int diceNumber = 0;
    int totalPoints;
    int accumulatedPoints[2] = {0, 0};
    int points;
    int diceCount;
    int farkled = 0;
    int hotDice = 0;
    char computerFlag = 'p';

    // for loop that sets the 2D array to 'N' for new, which means that the user can only choose dice with 'N' under it
    for (int d = 0; d < 6; d++)
    {
        keptDice[0][d] = 'N';
        keptDice[1][d] = 'N';
        // printf("%c", keptDice[0][d]);
        // printf("%c", keptDice[1][d]);
    }

    // WELCOME MESSAGES
    printf("\n\n");
    printf("\x1b[34m Welcome to Farkle!!! \x1b[0m \n\n");
    printf("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT\n");
    printf("| How to Play:                                                                      |\n");
    printf("|                                                                                   |\n");
    printf("| 1. Choose if you want to play against a \x1b[36m computer \x1b[0m or a \x1b[36m second player \x1b[0m.          |\n");
    printf("| 2. Start by rolling \x1b[36m 6 \x1b[0m dice.                                                     |\n");
    printf("|     - Dice that roll are \x1b[36m 1s, 5s, and/or triplets SCORE POINTS \x1b[0m                   |\n");
    printf("| 3. Choose the dice you want to keep (which will be labeled as '\x1b[36m K \x1b[0m')              |\n");
    printf("| 4. You will roll again. (dice with '\x1b[36m N \x1b[0m' means you can choose those dice)         |\n");
    printf("|     - you can \x1b[36m no longer choose dice with 'K' \x1b[0m under it                           |\n");
    printf("|     - you can \x1b[36m only choose dice with 'N' \x1b[0m under it                                |\n");
    printf("| 4. Stop rolling when there is too much \x1b[36m risk \x1b[0m to roll the rest of the dice.       |\n");
    printf("|                                                                                   |\n");
    printf("| Here are some examples:                                                           |\n");
    printf("|                                                                                   |\n");
    printf("|                                                                                   |\n");
    printf("|  Dice A    Dice B    Dice C    Dice D    Dice E    Dice F                         |\n");
    printf("|    1         5         3         3         6         3                            |\n");
    printf("|                                                                                   |\n");
    printf("| \x1b[34m You would want to choose dice ABCDF for maximum points \x1b[0m                          |\n");
    printf("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT\n\n");
    printf(" Here is an online version of Farkle to practice before you play!!!: \x1b[34m https://cardgames.io/farkle/ \x1b[0m \n\n\n");
    sleep(4);

    printf("\x1b[32m________________________  \n");
    printf("  POINTS\n");
    printf("________________________\n\n");

    // I used this source for scoring point numbers in farkle
    // I just used the scoring for triplets
    // https://rnkgaming.com/farkle-rules-2

    printf("       BASIC POINTS\n");
    printf("      ---------------\n");
    printf("       Each 1 is 100\n");
    printf("       Each 5 is 50\n\n");
    printf("       TRIPLET POINTS\n");
    printf("    ---------------------\n");
    printf("     Triplet of 1: 1000\n");
    printf("     Triplet of 2: 200\n");
    printf("     Triplet of 3: 300\n");
    printf("     Triplet of 4: 400\n");
    printf("     Triplet of 5: 500\n");
    printf("     Triplet of 6: 600 \x1b[0m \n\n");
    sleep(4);

    printf("************************************************************************************************************\n");
    start = get_char(" Type \x1b[36m c \x1b[0m to play against a computer or \x1b[36m any other character \x1b[0m to play against another player: ");
    printf("************************************************************************************************************\n\n\n");

    if (start == 'c' || start == 'C')
    {
        computerFlag = 'c';
        printf("\x1b[32m Y O U   G O   F I R S T!!! \x1b[0m \n\n\n");
        sleep(2);
    }
    // array creation that contains 2 series of arrays of 6 numbers
    // generates random numbers every time it is run
    srandom(time(NULL));
    // for each player 1 and 2
    for (int y = 0; y < 2; y++)
    {
        do
        {
            for (int x = 0; x < 6; x++)
            {
                // IF THERE IS AN 'N', GENERATE RANDOM NUMBERS UNDER THE DASHED LINE
                if (keptDice[y][x] == 'N')
                {
                    // RANDOM NUMBER CODE
                    // any random number between 1 and 6
                    randomNum = rand() % 6 + 1;
                    // stores the random number value to a position in the array
                    player[y][x] = randomNum;
                    // printf("rand: %i\n  ", player[y][x]);
                }
            }
            // GRAPHICS FOR THE TABLE FOR EACH PLAYER
            if (computerFlag == 'c' && y == 1)
            {
                printf("\n");
                printf("\x1b[31m Computer: \x1b[0m \n");
            }
            else
            {
                printf("\x1b[32m PLAYER %i: \x1b[0m \n\n", y + 1);
            }
            printf("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n");
            printf("X Dice:             A  B  C  D  E  F                 X\n");
            printf("X (N)ew or (K)ept:  %c  %c  %c  %c  %c  %c                 X\n", keptDice[y][0], keptDice[y][1], keptDice[y][2], keptDice[y][3], keptDice[y][4], keptDice[y][5]);
            printf("X                  -----------------                 X\n");
            printf("X Dice Roll:        %i  %i  %i  %i  %i  %i                 X\n", player[y][0], player[y][1], player[y][2], player[y][3], player[y][4], player[y][5]);
            printf("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n");

            // WHICH DICE AND HOW MANY ROLLED
            // ONLY CALCULATING FOR (N)EW DICE
            diceNumber = 0;
            totalPoints = 0;
            // FOR LOOP FOR GOING THROUGH ALL THE DICEVALUES FOR A-F
            for (int e = 0; e < 6; e++)
            { // checks if the dice has an 'N' under it and if it does,
                if (keptDice[y][e] == 'N')
                {
                    // prints every dice value
                    diceValues[diceNumber] = player[y][e];
                    // printf("Dice Value: %i\n", diceValues[diceNumber]);
                    diceNumber++;
                }
            }

            // CALCULATE POINTS CALLING farkle_points
            // printf("Dice Number: %i\n", diceNumber);
            totalPoints = farkle_points(diceNumber, diceValues);
            // if the total points is greater than 10000, then active the flag hotDice (which says it is hot dice and restarts the array)
            if (totalPoints > 10000)
            {
                hotDice = 1;
                // when a player got hot dice, I increased their points by 10000, so to get their actual points, I had to subtract 10000
                totalPoints = totalPoints - 10000;
            }

            if (computerFlag == 'c' && y == 1)
            {
                printf("The computer currently has \x1b[43m %i \x1b[0m points\n", accumulatedPoints[y]);
            }
            else
            {
                printf("You currently have \x1b[43m %i \x1b[0m points!!! \n", accumulatedPoints[y]);
            }

            printf("Total Points Rolled: \x1b[43m %i \x1b[0m \n", totalPoints);


            // IF TOTAL POINTS IS ZERO, IT IS FARKLE AND THE PLAYERS SCORE GOES TO ZERO
            if (totalPoints == 0)
            {
                printf("**************************\n");
                printf("    F A R K L E ! ! !\n");
                printf("You lost all your points!!!\n");
                printf("**************************\n");
                accumulatedPoints[y] = 0;
                // set the flag for farkled = 1, which means that it will move onto the next player, if it is on player 1
                farkled = 1;
                // set the flag for stop = 'S', which means that it will display their accumulated score and move on to the next player
                stop = 'S';
            }
            // if hotDice == 1, keep their accumulated score and add on to it, restart the array to have all 'N'
            if (hotDice == 1)
            {
                accumulatedPoints[y] = accumulatedPoints[y] + totalPoints;
                printf("***************************************************\n");
                printf("                H O T   D I C E ! ! !\n");
                printf("You get to keep %i points and roll all dice again!!!\n", accumulatedPoints[y]);
                printf("***************************************************\n");
                // SET ALL FLAGS BACK TO 'N'
                for (int h = 0; h < 6; h++)
                {
                    keptDice[y][h] = 'N';
                }
                farkled = 1;
                stop = 'C';
                printf("\x1b[36m Press Return to Continue \x1b[0m ");
                getchar();
            }
            // if farkled == 0, move onto next player
            if (farkled == 0)
            {
                if (computerFlag == 'c' && y == 1)
                {
                    // calculate score of all computer rolled dice + accumulated score
                    if (totalPoints + accumulatedPoints[y] >= accumulatedPoints[0])
                    {
                        stop = 'S';
                        printf("\x1b[34m Computer is done.........\n \x1b[0m");
                        sleep(4);
                    }

                    else
                    {
                        stop = 'C';
                    }
                }
                else
                {
                    do
                    {
                        printf("\n");
                        stop = get_char("Do you want to stop or continue? (S or C): ");
                    } while (stop != 'S' && stop != 'C');
                }
            }
            // IF STOP == 'S', DISPLAY ACCUMULATED POINTS AND MOVE ON
            if (stop == 'S')
            {
                accumulatedPoints[y] = accumulatedPoints[y] + totalPoints;
                printf("*****************************************\n");
                if (computerFlag == 'c' && y == 1)
                {
                    printf("\x1b[41m Computer Final Accumulated Points: %i \x1b[0m \n", accumulatedPoints[y]);
                }
                else
                {
                    printf("\x1b[42m Player %i Final Accumulated Points: %i \x1b[0m \n", y + 1, accumulatedPoints[y]);
                }
                printf("*****************************************\n\n");
                // go to next player
                printf("\x1b[36m Press Return to Continue \x1b[0m ");
                getchar();
                printf("\n");
                farkled = 0;

            }

            if (stop == 'C' && hotDice == 0)
            {

                if (computerFlag == 'c' && y == 1)
                {
                    // call the select function
                    keepLetter = compselectDice(keptDice, player, y);
                    printf("\x1b[31m Computer Chose:  %s \x1b[0m \n", keepLetter);
                    sleep(5);
                }
                else
                {
                    int playerInput = 0;
                    do
                    {
                        printf("\n");
                        keepLetter = get_string("Which dice letter(s) would you like to keep (only dice with N can be kept)(include a string without spaces)?");
                        // CALLING THE FUNCTION check_string_valid TO CHECK THE INPUTTED STRING if the playerInput is zero
                        playerInput = check_string_valid(keepLetter, keptDice, y, player);
                    } while (playerInput == 0);
                }

                // GO THROUGH ALL KEEP LETTERS AND STORING THE VALUE OF THE DICE INTO diceValues ARRAY.
                diceCount = 0;
                // FOR LOOP FOR GOING THROUGH THE STRING AND COUNTING HOW MANY DICE COUNT AS SCORES
                for (int s = 0; s < strlen(keepLetter); s++)
                {
                    if (keepLetter[s] == 'A')
                    {
                        diceValues[diceCount] = player[y][0];
                        diceCount++;
                    }
                    if (keepLetter[s] == 'B')
                    {
                        diceValues[diceCount] = player[y][1];
                        diceCount++;
                    }
                    if (keepLetter[s] == 'C')
                    {
                        diceValues[diceCount] = player[y][2];
                        diceCount++;
                    }
                    if (keepLetter[s] == 'D')
                    {
                        diceValues[diceCount] = player[y][3];
                        diceCount++;
                    }
                    if (keepLetter[s] == 'E')
                    {
                        diceValues[diceCount] = player[y][4];
                        diceCount++;
                    }
                    if (keepLetter[s] == 'F')
                    {
                        diceValues[diceCount] = player[y][5];
                        diceCount++;
                    }
                }
                points = farkle_points(diceCount, diceValues) - 10000;
                accumulatedPoints[y] = accumulatedPoints[y] + points;

                // FLAGGING DICE CHOSEN
                for (int g = 0; g < strlen(keepLetter); g++)
                {
                    int keepDiceNum = 0;
                    keepDiceNum = (int)keepLetter[g] - 65;
                    keptDice[y][keepDiceNum] = 'K';
                }
            }

            else
            {
                // means that farkled is not true
                farkled = 0;
                // means that hotDice is not true
                hotDice = 0;
            }

        } while (stop == 'C');
    }
    // END GAME
    printf("-------------------------------------------------------------\n");
    printf("\x1b[32m PLAYER 1: \n");
    printf("A  B  C  D  E  F\n");
    printf("%i  %i  %i  %i  %i  %i\n", player[0][0], player[0][1], player[0][2], player[0][3], player[0][4], player[0][5]);
    printf("\n");
    printf("\x1b[32m Accumulated Points for Player 1: %i \x1b[0m \n", accumulatedPoints[0]);
    printf("\n");

    if (computerFlag == 'c')
    {
        printf("\x1b[31m Computer: \n");
        printf("A  B  C  D  E  F\n");
        printf("%i  %i  %i  %i  %i  %i\n", player[1][0], player[1][1], player[1][2], player[1][3], player[1][4], player[1][5]);
        printf("\n");
        printf("Accumulated Points for Computer: %i \x1b[0m \n", accumulatedPoints[1]);
        printf("\n");
        printf("----------------------------\n");
    }
    else
    {
        printf("\x1b[31m PLAYER 2: \n");
        printf("A  B  C  D  E  F\n");
        printf("%i  %i  %i  %i  %i  %i\n", player[1][0], player[1][1], player[1][2], player[1][3], player[1][4], player[1][5]);
        printf("\n");
        printf("Accumulated Points for Player 2: %i \x1b[0m \n", accumulatedPoints[1]);
        printf("\n");
        printf("----------------------------\n");
    }

    // COMPARING THE ACCUMULATED SCORES FOR PLAYER 1 AND PLAYER 2
    if (accumulatedPoints[0] > accumulatedPoints[1])
    {
        printf("\x1b[1m Player 1 WINS!!! \x1b[0m \n");
    }

    else if (accumulatedPoints[1] > accumulatedPoints[0])
    {
        if (computerFlag == 'c')
        {
            printf("\x1b[41m Computer WINS!!! \x1b[0m \n");
        }
        else
        {
            printf("\x1b[41m Player 2 WINS!!! \x1b[0m \n");
        }
    }

    else
    {
        printf("\x1b[34m Both players TIE!!! \x1b[0m \n ");
    }
    printf("----------------------------\n");
    return 0;
}

int check_string_valid(string keepLetter, char keptDice[2][6], int y, int player[2][6])
{
    int diceNum;
    int valid = 1;
    int diceChosen;
    int diceValues[6] = {};
    int diceCount = 0;
    int points;

    // CHECKING THAT THE DICE ARE VALID CHARACTERS A-F
    for (int j = 0; j < strlen(keepLetter); j++)
    {
        if (keepLetter[j] == 'A' || keepLetter[j] == 'B' || keepLetter[j] == 'C' || keepLetter[j] == 'D' || keepLetter[j] == 'E' || keepLetter[j] == 'F')
        {
            diceChosen = (int)keepLetter[j];
            // printf("Dice Kept: %i diceletter: %c\n", diceChosen, keepLetter[j]);
        }

        else
        {
            printf("Error! you did not type A-F dice!\n");
            return 0;
        }
        // CHECKING IF THE SAME LETTER IS TYPED IN MORE THAN ONCE
        for (int q = 0; q < strlen(keepLetter); q++)
        {
            for (int w = q + 1; w < strlen(keepLetter); w++)
            {
                // if statement for checking if the letters are the same
                if (keepLetter[q] == keepLetter[w])
                {
                    printf("Error! you chose the same dice more than once!\n");
                    return 0;
                }
            }
        }
    }
    // CHECKING IF THE DICE IS NEW OR KEPT. IF THEY CHOSE A KEPT DICE, IT WILL NOT WORK THEY HAVE TO CHOOSE A NEW ONE
    for (int m = 0; m < strlen(keepLetter); m++)
    {
        diceNum = (int)keepLetter[m] - 65;
        // printf("DiceNum: %i  keepLetter: %i  keptDice: %c\n", diceNum, keepLetter[m], keptDice[y][diceNum]);
        if (keptDice[y][diceNum] == 'K')
        {
            printf("Error! you did not chose a (N)ew dice to keep!\n");
            return 0;
        }
    }

    // GO THROUGH ALL KEEP LETTERS AND STORING THE VALUE OF THE DICE INTO diceValues ARRAY.
    for (int l = 0; l < strlen(keepLetter); l++)
    {
        if (keepLetter[l] == 'A')
        {
            diceValues[diceCount] = player[y][0];
            diceCount++;
        }
        if (keepLetter[l] == 'B')
        {
            diceValues[diceCount] = player[y][1];
            diceCount++;
        }
        if (keepLetter[l] == 'C')
        {
            diceValues[diceCount] = player[y][2];
            diceCount++;
        }
        if (keepLetter[l] == 'D')
        {
            diceValues[diceCount] = player[y][3];
            diceCount++;
        }
        if (keepLetter[l] == 'E')
        {
            diceValues[diceCount] = player[y][4];
            diceCount++;
        }
        if (keepLetter[l] == 'F')
        {
            diceValues[diceCount] = player[y][5];
            diceCount++;
        }
    }
    points = farkle_points(diceCount, diceValues);
    // CHECKING IF THE DICE CHOSEN SCORE POINTS, IF THEY DON'T GIVE AN ERROR
    if (points < 10000)
    {
        printf("Error! You can only keep dice that scored points\n");
        return 0;
    }
    return valid;
}

int farkle_points(int diceNumber, int diceValues[])
{
    int diceCombination[6] = {0, 0, 0, 0, 0, 0};
    int calculatedDiceCounter = 0;
    int calculatedPoints = 0;

    for (int t = 0; t < diceNumber; t++)
    {
        // increases count of how many numbers there are of each type
        if (diceValues[t] == 1)
        {
            diceCombination[0]++;
        }
        else if (diceValues[t] == 2)
        {
            diceCombination[1]++;
        }

        else if (diceValues[t] == 3)
        {
            diceCombination[2]++;
        }

        else if (diceValues[t] == 4)
        {
            diceCombination[3]++;
        }

        else if (diceValues[t] == 5)
        {
            diceCombination[4]++;
        }

        else if (diceValues[t] == 6)
        {
            diceCombination[5]++;
        }
    }

    // for loop for counting how many numbers there are of each type
    /*
    for (int v = 0; v < 6; v++)
    {
        printf("Dice Values Array of %i: %i\n", v + 1, diceCombination[v]);
    }
    */

    // CHECKING THE VALUE OF THE 1st SLOT OF diceCombination array and increasing points earned and number of numbers that score
    if (diceCombination[0] == 6)
    {
        // 6 of number 1 gives you 2000 additional points and increases the number of scored dice to 6
        calculatedPoints = calculatedPoints + 2000;
        calculatedDiceCounter = calculatedDiceCounter + 6;
    }

    else if (diceCombination[0] == 5)
    {
        calculatedPoints = calculatedPoints + 1200;
        calculatedDiceCounter = calculatedDiceCounter + 5;
    }

    else if (diceCombination[0] == 4)
    {
        calculatedPoints = calculatedPoints + 1100;
        calculatedDiceCounter = calculatedDiceCounter + 4;
    }
    else if (diceCombination[0] == 3)
    {
        calculatedPoints = calculatedPoints + 1000;
        calculatedDiceCounter = calculatedDiceCounter + 3;
    }
    else if (diceCombination[0] == 2)
    {
        calculatedPoints = calculatedPoints + 200;
        calculatedDiceCounter = calculatedDiceCounter + 2;
    }
    else if (diceCombination[0] == 1)
    {
        calculatedPoints = calculatedPoints + 100;
        calculatedDiceCounter = calculatedDiceCounter + 1;
    }
    else if (diceCombination[0] == 0)
    {
        calculatedPoints = calculatedPoints + 0;
        calculatedDiceCounter = calculatedDiceCounter + 0;
    }
    // printf ("Points: %i\n", calculatedPoints);
    //  CHECKING THE VALUE OF THE 5th SLOT OF diceCombination array and increasing points earned and number of numbers that score
    if (diceCombination[4] == 5)
    {
        calculatedPoints = calculatedPoints + 100;
        calculatedDiceCounter = calculatedDiceCounter + 2;
    }
    else if (diceCombination[4] == 4)
    {
        calculatedPoints = calculatedPoints + 50;
        calculatedDiceCounter = calculatedDiceCounter + 1;
    }
    else if (diceCombination[4] == 2)
    {
        calculatedPoints = calculatedPoints + 100;
        calculatedDiceCounter = calculatedDiceCounter + 2;
    }
    else if (diceCombination[4] == 1)
    {
        calculatedPoints = calculatedPoints + 50;
        calculatedDiceCounter = calculatedDiceCounter + 1;
    }
    else if (diceCombination[4] == 0)
    {
        calculatedPoints = calculatedPoints + 0;
        calculatedDiceCounter = calculatedDiceCounter + 0;
    }
    // printf("Points: %i\n", calculatedPoints);
    //  for each slot in diceCombination array between 2 and 6
    for (int g = 1; g < 6; g++)
    {
        if (diceCombination[g] == 6)
        {
            calculatedPoints = calculatedPoints + ((g + 1) * 200);
            calculatedDiceCounter = calculatedDiceCounter + 6;
        }
        else if (diceCombination[g] >= 3 && diceCombination[g] <= 5)
        {
            calculatedPoints = calculatedPoints + ((g + 1) * 100);
            calculatedDiceCounter = calculatedDiceCounter + 3;
        }
        else if (diceCombination[g] < 3)
        {
            calculatedPoints = calculatedPoints + 0;
            calculatedDiceCounter = calculatedDiceCounter + 0;
        }
    }
    // printf("Points: %i\n", calculatedPoints);
    // printf("How many numbers count as scores: %i\n", calculatedDiceCounter);

    // CHECKING HOW MANY OF THE DICE THROWN SCORED POINTS
    if (calculatedDiceCounter == diceNumber)
    {
        calculatedPoints = calculatedPoints + 10000;
        // printf("HOT DICE\n");
    }

    // return total points scored
    return calculatedPoints;
}

string compselectDice(char keptDice[2][6], int player[2][6], int y)
{
    int countSelectedDice = 0;
    int selectDice[6] = {8, 8, 8, 8, 8, 8};

    // arrays for storing the number of 2s, 3,s 4s, and 6s in a roll
    int triplePick2[6] = {};
    int triplePick3[6] = {};
    int triplePick4[6] = {};
    int triplePick6[6] = {};

    // defining variables that keeps track of the number of 2s, 3,s 4s, and 6s in a roll
    int tripleCount2 = 0;
    int tripleCount3 = 0;
    int tripleCount4 = 0;
    int tripleCount6 = 0;

    // for loop that goes through each dice to see if it is new 'N' or kept 'K'
    // if it is 'N' then check if it is a 1 or 5
    // if it is a 1 or 5, save it to the selectDice array and keep increasing the count
    for (int e = 0; e < 6; e++)
    {
        // printf("Kept Dice %i %i %c\n", y, e, keptDice[y][e]);
        if (keptDice[y][e] == 'N')
        {
            if (player[y][e] == 1 || player[y][e] == 5)
            {
                selectDice[countSelectedDice] = e;
                countSelectedDice++;
            }

            // if statement that counts how many numbers of (2, 3, 4, 6) show up
            else if (player[y][e] == 2)
            {
                triplePick2[tripleCount2] = e;
                tripleCount2++;
                // if the numbers of 2 is equal to 3 (which means there is a triplet!!!), return the slot letter of each of the triplets
                if (tripleCount2 == 3)
                {
                    for (int f = 0; f < 3; f++)
                    {
                        selectDice[countSelectedDice] = triplePick2[f];
                        countSelectedDice++;
                    }
                }
            }

            // if statement that counts how many numbers of (2, 3, 4, 6) show up
            else if (player[y][e] == 3)
            {
                triplePick3[tripleCount3] = e;
                tripleCount3++;
                // if the numbers of 2 is equal to 3 (which means there is a triplet!!!), return the slot letter of each of the triplets
                if (tripleCount3 == 3)
                {
                    for (int r = 0; r < 3; r++)
                    {
                        selectDice[countSelectedDice] = triplePick3[r];
                        countSelectedDice++;
                    }
                }
            }

            // if statement that counts how many numbers of (2, 3, 4, 6) show up
            else if (player[y][e] == 4)
            {
                triplePick4[tripleCount4] = e;
                tripleCount4++;
                // if the numbers of 2 is equal to 3 (which means there is a triplet!!!), return the slot letter of each of the triplets
                if (tripleCount4 == 3)
                {
                    for (int w = 0; w < 3; w++)
                    {
                        selectDice[countSelectedDice] = triplePick4[w];
                        countSelectedDice++;
                    }
                }
            }

                // if statement that counts how many numbers of (2, 3, 4, 6) show up
            else if (player[y][e] == 6)
            {
                triplePick6[tripleCount6] = e;
                tripleCount6++;
                // if the numbers of 2 is equal to 3 (which means there is a triplet!!!), return the slot letter of each of the triplets
                if (tripleCount6 == 3)
                {
                    for (int t = 0; t < 3; t++)
                    {
                        selectDice[countSelectedDice] = triplePick6[t];
                        countSelectedDice++;
                    }
                }
            }
            // emptying out the kept letters
            keptCompLetters[e] = ' ';
        }
    }
    // printf("Count selected dice %i\n", countSelectedDice);

    // for loop that goes through all the positions of the dice values and checks to see if there is a dice from each position that the computer wants to keep so that it can generate a string
    // selectDice[0] is A
    // selectDice[1] is B
    // selectDice[2] is C
    // selectDice[3] is D
    // selectDice[4] is E
    // selectDice[5] is F

    for (int u = 0; u < countSelectedDice; u++)
    {
        if (selectDice[u] == 0)
        {
            keptCompLetters[u] = 'A';
        }
        else if (selectDice[u] == 1)
        {
            keptCompLetters[u] = 'B';
        }
        else if (selectDice[u] == 2)
        {
            keptCompLetters[u] = 'C';
        }
        else if (selectDice[u] == 3)
        {
            keptCompLetters[u] = 'D';
        }
        else if (selectDice[u] == 4)
        {
            keptCompLetters[u] = 'E';
        }
        else if (selectDice[u] == 5)
        {
            keptCompLetters[u] = 'F';
        }

        // printf("KeptLetter: %s\n", keptCompLetters);
    }
    // end the string with the null character so the strlen is correct
    keptCompLetters[countSelectedDice] = '\0';

    return keptCompLetters;
}
