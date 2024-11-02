# RDBMS-Normalizer-project

To develop a program that takes a database (relations) and functional dependencies as input, normalizes the relations based on the provided functional dependencies, produces SQL queries to generate the normalized database tables, and optionally determines the highest normal form of the input table.

Execution :
For execution of main program that performs normalization from 1NF to 5NF
Open CMD and enter
python Project1.py
Enter primary keys :OrderID,FoodID,DrinkID
Select Normal form from 1NF to 5nF (eg for 3NF enter 3)
That resultant table queries for the normal form selected are shown in in terminal and printed in output.sql file as output.

The program mvd.py will autonomously identify multi-valued dependencies WITHOUT relying on user-provided MVD data and prints them to terminal, It also performs 4Nf on given table based on auto identified mvds and print resultant table queries in terminal, additionally it also performs 5NF and finding join dependencies and print the result table.
Program execution :python mvd.py


The program dknf.py will perform Domain-key normal form and prints the result tables :
Program execution :python dknf.py
