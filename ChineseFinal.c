// Natasha Sieh
// May 26, 2023
// Chinese Final Project

#define _DEFAULT_SOURCE
#include <stdlib.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/************************************************************************************

This program is a interactive and fun personality test for students learning Chinese.

*************************************************************************************/

int main(void)
{
    // this program does NOT accept chinese characters, so you put english numbers instead of chinese ones
    printf("\033[1;32;40m Welcome to this personality 考试! \033[0;32;0m\n");
    printf("\n");
    printf("************************************************");
    printf("\n");

// question 1

    string name = get_string("\033[1;32;40m 问题一: 你叫什么名字? (character) ");
    printf("\x1b[36m 你好,  %s !\033[0;32;0m\n\x1b[0m", name);


    printf("************************************************\n");

// question 2 and alternative answers

    int age = get_int("\033[1;32;40m 问题二: 你今年几岁? (number) ");
    if (age == 16)
    {
        printf("\x1b[36m 你有一年到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 15)
    {
        printf("\x1b[36m 你有二年到上大学!\033\033[0;32;0m\n\x1b[0m");

    }
    else if (age == 14)
    {
        printf("\x1b[36m 你有三年到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 13)
    {
        printf("\x1b[36m 你有四年到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 12)
    {
        printf("\x1b[36m 你有五年到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 11)
    {
        printf("\x1b[36m 你有六年到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 10)
    {
        printf("\x1b[36m 你有七到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 9)
    {
        printf("\x1b[36m 你有八到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 8)
    {
        printf("\x1b[36m 你有九到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 7)
    {
        printf("\x1b[36m 你有十到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 6)
    {
        printf("\x1b[36m 你有十一到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 5)
    {
        printf("\x1b[36m 你有十二到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 4)
    {
        printf("\x1b[36m 你有十三到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 3)
    {
        printf("\x1b[36m 你有十四到上大学!\033\033[0;32;0m\n\x1b[0m");
    }
    else if (age == 2)
    {
        printf("\x1b[36m 你有十五到上大学!\033[0;32;0m\n\x1b[0m\n");
    }
    else if (age == 1)
    {
        printf("\x1b[36m 你有十六到上大学!\033[0;32;0m\n\x1b[0m");
    }
    else if (age >= 17 && age <= 22)
    {
        printf("\x1b[36m 你在上大学!\033[0;32;0m\n\x1b[0m");
    }
    else if (age > 22)
    {
        printf("\x1b[36m 你应该找份工作!!!\033[0;32;0m\n\x1b[0m");
    }

    printf("************************************************\n");

// question 3 and alternative answers

    int familyMembers = get_int("\033[1;32;40m 问题三: 你家有几口人？(number) ");
    if (familyMembers == 4)
    {
        printf("\x1b[36m 太好了。我也有四口家人！！！爸爸，妈妈，妹妹，和我。\033[0;32;0m\n\x1b[0m");
    }
    else if (familyMembers >= 3)
    {
        int oldest = get_int("\x1b[36m 你是最老的吗? (对(1) 还是 不对(2): ");

        if (oldest == 1)
        {
            printf("\x1b[36m 我也是最老的!!!\033[0;32;0m\n\x1b[0m");
        }

        else if (oldest == 2)
        {
            printf("\x1b[36m 那很好!!!\033[0;32;0m\n\x1b[0m");
        }
        printf("************************************************\n");
    }

    else if (familyMembers < 3)
        {
            printf("\x1b[36m 太好了。\033[0;32;0m\n\x1b[0m");
            printf("************************************************\n");
        }

        printf("************************************************\n");

// questions 4-11

        string where = get_string("\033[1;32;40m 问题四: 你喜欢去哪里? (character) ");
        printf("\x1b[36m 我也喜欢去 %s。可是我最喜欢去 Spain。\033[0;32;0m\n\x1b[0m", where);
        printf("************************************************\n");

        string transport = get_string("\033[1;32;40m 问题五: 你喜欢坐汽车、出租车、火车、电车还是公共汽车? (character) ");
        printf("\x1b[36m 你喜欢坐%s, 我也喜欢坐%s\033[0;32;0m\n\x1b[0m", transport, transport);
        printf("************************************************\n");

        string color = get_string("\033[1;32;40m 问题六: 你最喜欢的颜色是什么? (character) ");
        printf("\x1b[36m 我喜欢紫色。\033[0;32;0m\n\x1b[0m");
        printf("************************************************\n");

        string food = get_string("\033[1;32;40m 问题七: 你最喜欢的饭是什么? (character) ");
        printf("\x1b[36m 我也喜欢吃 %s \033[0;32;0m\n\x1b[0m", food);
        printf("************************************************\n");

        string school = get_string("\033[1;32;40m 问题八: 你上什么学校？(character) ");
        printf("\x1b[36m %s 学校很好!!!\033[0;32;0m\n\x1b[0m", school);
        printf("************************************************\n");

        string season = get_string("\033[1;32;40m 问题九: 你最喜欢的季节是什么？(character) ");
        printf("\x1b[36m 我很喜欢夏天，因为有很多空儿。可是，有的时候我上暑期班。\033[0;32;0m\n\x1b[0m");
        printf("************************************************\n");

        string subject = get_string("\033[1;32;40m 问题十: 你最喜欢什么课？(character) ");
        printf("\x1b[36m 我也喜欢%s因为有意思。我的%s老师是 Bob 老师。我觉得他很酷。可是他给我们太多功课。\033[0;32;0m\n\x1b[0m", subject, subject);
        printf("************************************************\n");

        string book = get_string("\033[1;32;40m 问题十一: 你最喜欢的书是什么? (character) ");
        printf("\x1b[36m 我很喜欢念 Harry Potter。\033[0;32;0m\n\x1b[0m");
        printf("************************************************\n");

        /* age == 12:
            print(age)

           age == 1
            print(age - 17)
            print("你今年一岁!!! you still have a long time")

           age == 11
            print()

           age == 17
            print("我也是十七岁。")*/

// end message (added delays it make it suspisious)

        sleep(2);
        printf(".");
        printf(".");
        printf(".");
        printf(".");
        printf(".");
        sleep(2);
        printf(".");
        printf(".");
        printf(".");
        printf(".");
        printf(".");
        sleep(2);
        printf(".");
        printf(".");
        printf(".");
        printf(".");
        printf(".\n");
        printf("\n");
        sleep(2);
        printf("You have completed the personality test!!!\n");
        printf("\n");
        printf("等待结果...\n");
        sleep(3);
        printf("\n");
        printf("\n");

// at the end of the game, use all the information to write a paragraph about your predictions on the person.

        printf("Paragraph: \n");
        printf("    很高兴见到你，%s。你%i岁所以你有很多机会。你上%s的学校 🏫。别个人告诉我%s学校很难。你最喜欢的季节是, %s。你最喜欢的课是%s。我建议你住在西班牙 🇪🇸 因为西班牙有很好的饭和人。在西班牙你可以做运动。西班牙也有 Tapas 的饭。 我最喜欢那们的 Patatas Bravas, Jamon, 和 Calamares fritos。在西班牙你也可以看到 Sagrada Familia, Alhambra, 和 Plaza de España。我觉得你有很好家人, 谢谢 🙏 他们。很高兴见到你, 祝你福 🧧 。\n", name, age, school, school, season, subject);
        printf("\n");
        printf("\n");
        printf("再见 👋 \n");

}
