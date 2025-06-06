import pandas as pd
import re

# LINHA DE SELEÇÃO DO INPUT
CAMINHO_ARQUIVO = r'C:\Users\annun\OneDrive\Documents\PROJETOS\Analide CADE\cade_clinicas_II.csv'
df = pd.read_csv(CAMINHO_ARQUIVO, sep=',', encoding='utf-8', low_memory=False)

# ==========================
# 1. FILTRO DE DOCUMENTOS RELEVANTES
# ==========================
TIPOS_RELEVANTES = [
    'Voto', 
    'Voto Processo Administrativo', 
    'Voto Embargos de Declaração'
]
df_filtrado = df[df['descricao_tipo_documento'].str.contains('|'.join(TIPOS_RELEVANTES), case=False, na=False)].copy()

# ==========================
# 2. IDENTIFICAR CONDENAÇÃO
# ==========================
# Supondo que 'decisao_tribunal' indica condenação (ajuste se necessário)
df_filtrado['condenacao'] = df_filtrado['decisao_tribunal'].str.contains('condena', case=False, na=False)

# ==========================
# 3. EXTRAIR PERCENTUAL DE FATURAMENTO FIXADO COMO MULTA
# ==========================
# Busca padrões como 10%, 2,5%, 0,5 %, etc no corpo do texto
def extrair_percentual(texto):
    if pd.isnull(texto):
        return None
    match = re.search(r'(\d{1,2}(?:[.,]\d+)?\s*%)', texto)
    if match:
        # Converte para float
        valor = match.group(1).replace(',', '.').replace('%', '').strip()
        try:
            return float(valor)
        except:
            return None
    return None

df_filtrado['percent_faturamento_multa'] = df_filtrado['corpo_texto'].apply(extrair_percentual)

# ==========================
# 4. ESTATÍSTICAS DESCRITIVAS
# ==========================
# Porcentagem de documentos contendo votos de condenação
total_docs = len(df_filtrado)
docs_condenacao = df_filtrado['condenacao'].sum()
porcentagem_condenacao = 100 * docs_condenacao / total_docs if total_docs else 0

# Média do valor em reais das condenações (pode não estar disponível, depende do campo)
# Se tiver um campo para valor de multa, extraia! Aqui um exemplo genérico para extrair R$ do corpo do texto:
def extrair_valor_reais(texto):
    if pd.isnull(texto):
        return None
    match = re.search(r'R\$\s?([\d\.]+,\d{2})', texto)
    if match:
        valor = match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(valor)
        except:
            return None
    return None

df_filtrado['valor_multa_reais'] = df_filtrado['corpo_texto'].apply(extrair_valor_reais)
media_valor_reais = df_filtrado['valor_multa_reais'].mean()

# Média do percentual do faturamento das multas
media_percentual_faturamento = df_filtrado['percent_faturamento_multa'].mean()

print(f'Porcentagem de condenação: {porcentagem_condenacao:.2f}%')
print(f'Média valor condenação (R$): {media_valor_reais:.2f}')
print(f'Média percentual do faturamento usado como multa: {media_percentual_faturamento:.2f}%')

# ==========================
# 5. EXPORTAÇÃO DO OUTPUT
# ==========================
# output.xlsx – planilha com os dados finais e novas colunas
df_filtrado['id'] = df_filtrado['id']  # Garante que coluna 'id' esteja no output
colunas_output = ['id', 'descricao_tipo_documento', 'condenacao', 'percent_faturamento_multa', 'valor_multa_reais', 'corpo_texto']
df_filtrado[colunas_output].to_excel('output.xlsx', index=False)

# relatorio.csv – resultados estatísticos
with open('relatorio.csv', 'w', encoding='utf-8') as f:
    f.write('porcentagem_condenacao,media_valor_reais,media_percentual_faturamento\n')
    f.write(f'{porcentagem_condenacao:.2f},{media_valor_reais:.2f},{media_percentual_faturamento:.2f}\n')

print('Arquivos output.xlsx e relatorio.csv gerados!')

# ==========================
# 6. (EXTRA) HISTOGRAMA DA MULTA EM PERCENTUAL
# ==========================
import matplotlib.pyplot as plt
df_filtrado['percent_faturamento_multa'].dropna().plot.hist(bins=20, edgecolor='k')
plt.title('Distribuição do Percentual do Faturamento como Multa')
plt.xlabel('Percentual (%)')
plt.ylabel('Frequência')
plt.savefig('histograma_percentual_multa.png')
plt.show()

