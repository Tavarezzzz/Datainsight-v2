# 🚀 GUIA DE IMPLEMENTAÇÃO - DataInsight v2.0

## Instalação Rápida
```bash
pip install -r requirements.txt
streamlit run app_v2.py
```

Abra http://localhost:8501

## Como Usar

1. **Carregue um arquivo** (CSV ou Excel)
2. **Veja análises automáticas**
3. **Exporte relatório em Excel**

## Deploy em Produção

### Streamlit Cloud (Gratuito)
1. Push no GitHub
2. Vá em https://share.streamlit.io
3. Conecte seu repositório
4. Pronto!

### Heroku
```bash
heroku create seu-app
git push heroku main
```

## Casos de Uso

- Análise de Vendas
- Recursos Humanos
- Financeiro
- Logística
- E-commerce
- Qualquer dataset com CSV/Excel

## Customizações

### Mudar cores
Edite `app_v2.py` e procure por `#667eea` e `#764ba2`

### Adicionar novo gráfico
Use Plotly Express:
```python
fig = px.seu_tipo_grafico(df, ...)
st.plotly_chart(fig, use_container_width=True)
```

## Troubleshooting

**Erro: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Gráficos não aparecem**
Verifique se suas colunas têm tipos corretos (numérico vs texto)

---

Desenvolvido com ❤️ para transformar dados em decisões