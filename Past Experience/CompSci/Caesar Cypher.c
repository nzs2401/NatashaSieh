// Natasha Sieh
// 1/9/22
// Period 4
// Caesar Lab

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

//string cypher_function(string plainText, int key);

string cypher_function(string plainText, int key)
{
    char cipher1;
    char cipher2;
    char noChange;
    string shift;
    printf("ciphertext: ");
    for (int j = 0; j < strlen(plainText); j++)
    {
        if (isalpha(plainText[j]))
        {
            if (isupper(plainText[j]))
            {
                // rotate all the upper case letters
                // print out rotated letters
                cipher1 = printf("%c", (char)(((int)(plainText[j] + key) - 65) % 26) + 65);
                shift = &cipher1;
            }

            if (islower(plainText[j]))
            {
                // rotate all the lower case letters
                // print out rotated letters
                cipher2 = printf("%c", (char)(((int)(plainText[j] + key) - 97) % 26) + 97);
                shift = &cipher2;
            }

        }

        else
        {
            noChange = printf("%c", plainText[j]);
            shift = &plainText[j];
        }
    }
    //printf("\n");
    return (string) shift;
}

int main(int argc, string argv[])
{
    string plainText;
    int key;
    printf("%c", argc);

    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    for (int z = 0; z < strlen(argv[1]); z++)
    {

        if (!isdigit(argv[1][z]))
        {
            printf("Usage: ./caesar key\n");
            //printf("%c", argv[1][z]);
            return 1;
        }
    }


    if (argc == 2)
    {
        key = atoi(argv[1]);
        //printf("%i\n", key);
        plainText = get_string("plaintext: ");
        printf("%s\n", cypher_function(plainText, key));
        return 0;

    }

    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    printf("\n");
}
