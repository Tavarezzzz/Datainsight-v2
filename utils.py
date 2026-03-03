import pandas as pd
import numpy as np

def detect_outliers(data, column):
    """Detecta outliers usando IQR"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    return data[(data[column] < Q1 - 1.5*IQR) | (data[column] > Q3 + 1.5*IQR)]

def get_data_quality(data):
    """Retorna score de qualidade dos dados"""
    completeness = 100 - (data.isnull().sum().sum() / (len(data) * len(data.columns)) * 100)
    duplicates = data.duplicated().sum()
    return {'completeness': round(completeness, 2), 'duplicates': duplicates}