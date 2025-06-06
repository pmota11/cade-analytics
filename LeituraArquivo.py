import pandas as pd

# LINHA DE SELEÇÃO DO INPUT
df = pd.read_csv(r'C:\Users\annun\OneDrive\Documents\PROJETOS\Analide CADE\cade_clinicas_II.csv', sep=',', encoding='utf-8', low_memory=False)

print(df.columns.tolist())
