-- Query for MainTable_Decomposed_1
CREATE TABLE MainTable_Decomposed_1 (
  OrderID VARCHAR(255),
  TotalDrinkCost VARCHAR(255),
  TotalCost VARCHAR(255),
  CustomerName VARCHAR(255),
  Date VARCHAR(255),
  CustomerID VARCHAR(255),
  TotalFoodCost VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for MainTable_Decomposed_2
CREATE TABLE MainTable_Decomposed_2 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  Milk VARCHAR(255),
  DrinkName VARCHAR(255),
  DrinkQuantity VARCHAR(255),
  DrinkSize VARCHAR(255),
  PRIMARY KEY (OrderID, DrinkID)
);;

-- Query for MainTable_Decomposed_3
CREATE TABLE MainTable_Decomposed_3 (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  FoodQuantity VARCHAR(255),
  FoodName VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID)
);;

-- Query for MainTable_Decomposed_4
CREATE TABLE MainTable_Decomposed_4 (
  DrinkID VARCHAR(255),
  DrinkName VARCHAR(255),
  PRIMARY KEY (DrinkID)
);;

-- Query for MainTable_Decomposed_5
CREATE TABLE MainTable_Decomposed_5 (
  FoodID VARCHAR(255),
  FoodName VARCHAR(255),
  PRIMARY KEY (FoodID)
);;

-- Query for MainTable_Decomposed_6
CREATE TABLE MainTable_Decomposed_6 (
  OrderID VARCHAR(255),
  PromocodeUsed VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for MainTable_Remaining
CREATE TABLE MainTable_Remaining (
  FoodAllergen VARCHAR(255),
  FoodIngredient VARCHAR(255),
  DrinkAllergen VARCHAR(255),
  DrinkIngredient VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID)
);;

-- Query for PromocodeUsed_Table_Decomposed_1
CREATE TABLE PromocodeUsed_Table_Decomposed_1 (
  OrderID VARCHAR(255),
  PromocodeUsed VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for PromocodeUsed_Table_Remaining
CREATE TABLE PromocodeUsed_Table_Remaining (
  FoodID VARCHAR(255),
  DrinkID VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, PromocodeUsed)
);;

-- Query for DrinkIngredient_Table
-- Table DrinkIngredient_Table is already in 2NF
CREATE TABLE DrinkIngredient_Table (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  DrinkID VARCHAR(255),
  DrinkIngredient VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, DrinkIngredient)
);;

-- Query for DrinkAllergen_Table
-- Table DrinkAllergen_Table is already in 2NF
CREATE TABLE DrinkAllergen_Table (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  DrinkID VARCHAR(255),
  DrinkAllergen VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, DrinkAllergen)
);;

-- Query for FoodIngredient_Table
-- Table FoodIngredient_Table is already in 2NF
CREATE TABLE FoodIngredient_Table (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodIngredient VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, FoodIngredient)
);;

-- Query for FoodAllergen_Table
-- Table FoodAllergen_Table is already in 2NF
CREATE TABLE FoodAllergen_Table (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodAllergen VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, FoodAllergen)
);;

