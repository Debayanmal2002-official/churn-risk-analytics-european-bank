import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
file_path = BASE_DIR / "data" / "raw_european_bank_data.xlsx"
df = pd.read_excel(file_path)
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

cols2 = ['CreditScore', 'Age', 'EstimatedSalary','Tenure','Balance']
print(df[cols2].describe())



## -- Creating bins --

# Credit Score Segmentation
df['CreditScoreGroup'] = pd.cut(
    df['CreditScore'],
    bins=[300, 580, 720, 850],
    labels=[
        'Low (300–580)',
        'Medium (580–720)',
        'High (720+)'
    ]
)
# Age Segmentation
df['AgeGroup'] = pd.cut(
    df['Age'],
    bins=[0, 30, 45, 60, 100],
    labels=[
        'Young (0–30)',
        'Mid-age (30–45)',
        'Mature (45–60)',
        'Senior (60+)'
    ]
)
# Salary Segmentation
df['SalaryGroup'] = pd.cut(
    df['EstimatedSalary'],
    bins=[0, 50000, 150000, 200000],
    labels=[
        'Low (0–50K)',
        'Medium (50K–150K)',
        'High (150K+)'
    ]
)
# Tenure Group
df['TenureGroup'] = pd.cut(
    df['Tenure'],
    bins=[-1, 3, 7, 10],
    labels=[
        'New (0–3 yrs)',
        'Mid-term (4–7 yrs)',
        'Long-term (8+ yrs)'
    ]
)
# Balance Group
df['BalanceGroup'] = pd.cut(
    df['Balance'],
    bins=[-1, 0, 100000, 300000],
    labels=[
        'Zero (0)',
        'Low (1–100K)',
        'High (100K+)'
    ]
)

for col in cols2:
    print(df[col].value_counts())

print(df.info())
print(df.isnull().sum())

## -- Final Save --

save_path = BASE_DIR / "data" / "processed_data.xlsx"
df.to_excel(save_path, index=False)
