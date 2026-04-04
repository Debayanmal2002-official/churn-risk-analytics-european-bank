import pandas as pd
import numpy as np
from debugpy.launcher.debuggee import describe

df = pd.read_excel("data/raw_european_bank_data.xlsx")
print(df.info())

## -- Dropping Surname for privacy reason --
df.drop(['Surname'], axis=1, inplace=True)

## -- Changing data type --
df['Geography'] = df['Geography'].astype('category')
df['Gender'] = df['Gender'].astype('category')

## -- Basic features info --
cols1 = ['Geography', 'Gender', 'Tenure', 'NumOfProducts',
        'HasCrCard', 'IsActiveMember', 'Exited']
for col in cols1:
    print(f"{col}: {df[col].unique()}")

cols2 = ['CreditScore', 'Age', 'EstimatedSalary']
print(df[cols2].describe())



## -- Creating bins --

# Credit Score Segmentation
df['CreditScoreGroup'] = pd.cut(
    df['CreditScore'],
    bins=[300, 580, 720, 850],
    labels=['Low', 'Medium', 'High']
)
# Age Segmentation
df['AgeGroup'] = pd.cut(
    df['Age'],
    bins=[0, 30, 45, 60, 100],
    labels=['Young', 'Mid-age', 'Mature', 'Senior']
)
# Salary Segmentation
df['SalaryGroup'] = pd.cut(
    df['EstimatedSalary'],
    bins=[0, 50000, 150000, 200000],
    labels=['Low', 'Medium', 'High']
)

for col in ['CreditScoreGroup', 'AgeGroup', 'SalaryGroup']:
    print(df[col].value_counts())

print(df.info())
print(df.isnull().sum())

## -- Final Save --
df.to_excel("data/processed_data.xlsx", index=False)
