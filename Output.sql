-- Query for MainTable_Decomposed_1_BCNF_1
-- Table MainTable_Decomposed_1_BCNF_1 is already in 5NF
CREATE TABLE MainTable_Decomposed_1_BCNF_1 (
  CustomerName VARCHAR(255),
  CustomerID VARCHAR(255),
  PRIMARY KEY (CustomerID)
);;

-- Query for MainTable_Decomposed_1_Base
-- Table MainTable_Decomposed_1_Base is already in 5NF
CREATE TABLE MainTable_Decomposed_1_Base (
  Date VARCHAR(255),
  TotalFoodCost VARCHAR(255),
  OrderID VARCHAR(255),
  CustomerID VARCHAR(255),
  TotalCost VARCHAR(255),
  TotalDrinkCost VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for MainTable_Decomposed_2_BCNF_1
-- Table MainTable_Decomposed_2_BCNF_1 is already in 5NF
CREATE TABLE MainTable_Decomposed_2_BCNF_1 (
  DrinkID VARCHAR(255),
  DrinkName VARCHAR(255),
  PRIMARY KEY (DrinkID)
);;

-- Query for MainTable_Decomposed_2_Base
-- Table MainTable_Decomposed_2_Base is already in 5NF
CREATE TABLE MainTable_Decomposed_2_Base (
  DrinkSize VARCHAR(255),
  DrinkID VARCHAR(255),
  Milk VARCHAR(255),
  OrderID VARCHAR(255),
  DrinkQuantity VARCHAR(255),
  PRIMARY KEY (OrderID, DrinkID)
);;

-- Query for MainTable_Decomposed_3
-- Table MainTable_Decomposed_3 is already in 5NF
CREATE TABLE MainTable_Decomposed_3 (
  OrderID VARCHAR(255),
  FoodID VARCHAR(255),
  FoodQuantity VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID)
);;

-- Query for MainTable_Decomposed_4
-- Table MainTable_Decomposed_4 is already in 5NF
CREATE TABLE MainTable_Decomposed_4 (
  DrinkID VARCHAR(255),
  DrinkName VARCHAR(255),
  PRIMARY KEY (DrinkID)
);;

-- Query for MainTable_Decomposed_5
-- Table MainTable_Decomposed_5 is already in 5NF
CREATE TABLE MainTable_Decomposed_5 (
  FoodID VARCHAR(255),
  FoodName VARCHAR(255),
  PRIMARY KEY (FoodID)
);;

-- Query for MainTable_Remaining
-- Table MainTable_Remaining is already in 5NF
CREATE TABLE MainTable_Remaining (
  PromocodeUsed VARCHAR(255),
  DrinkIngredient VARCHAR(255),
  DrinkAllergen VARCHAR(255),
  FoodIngredient VARCHAR(255),
  FoodAllergen VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID)
);;

-- Query for PromocodeUsed_Table_4NF_1
-- Table PromocodeUsed_Table_4NF_1 is already in 5NF
CREATE TABLE PromocodeUsed_Table_4NF_1 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for PromocodeUsed_Table_Base
-- Table PromocodeUsed_Table_Base is already in 5NF
CREATE TABLE PromocodeUsed_Table_Base (
  OrderID VARCHAR(255),
  PromocodeUsed VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID, DrinkID, PromocodeUsed)
);;

-- Query for DrinkIngredient_Table_4NF_1
-- Table DrinkIngredient_Table_4NF_1 is already in 5NF
CREATE TABLE DrinkIngredient_Table_4NF_1 (
  OrderID VARCHAR(255),
  DrinkIngredient VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID, DrinkID)
);;

-- Query for DrinkAllergen_Table_4NF_1
-- Table DrinkAllergen_Table_4NF_1 is already in 5NF
CREATE TABLE DrinkAllergen_Table_4NF_1 (
  OrderID VARCHAR(255),
  DrinkAllergen VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID, DrinkID)
);;

-- Query for FoodIngredient_Table_4NF_1
-- Table FoodIngredient_Table_4NF_1 is already in 5NF
CREATE TABLE FoodIngredient_Table_4NF_1 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodIngredient VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID)
);;

-- Query for FoodIngredient_Table_4NF_2
-- Table FoodIngredient_Table_4NF_2 is already in 5NF
CREATE TABLE FoodIngredient_Table_4NF_2 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

-- Query for FoodAllergen_Table_4NF_1
-- Table FoodAllergen_Table_4NF_1 is already in 5NF
CREATE TABLE FoodAllergen_Table_4NF_1 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodAllergen VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID, FoodID)
);;

-- Query for FoodAllergen_Table_4NF_2
-- Table FoodAllergen_Table_4NF_2 is already in 5NF
CREATE TABLE FoodAllergen_Table_4NF_2 (
  OrderID VARCHAR(255),
  DrinkID VARCHAR(255),
  FoodID VARCHAR(255),
  PRIMARY KEY (OrderID)
);;

