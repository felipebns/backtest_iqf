# Backtest de Factor Investing — IQF, Grupo 4

Simula em Python a estratégia da Entrega 1 de out/2016 a out/2026, com rebalanceamento trimestral, e compara o resultado com o Ibovespa e o CDI, já descontados os custos.

## Estratégia

A carteira tem 20 ações, com 5% em cada uma, divididas em duas partes:

| Carteira | Peso | Filtros, em ordem |
|---|---|---|
| Defensiva | 70% (14 ações) | P/L < 20 → ROIC > 10%, 30 melhores → 14 melhores na nota 60% downside deviation (5 anos) + 40% momentum (12 meses) |
| Agressiva | 30% (6 ações) | Valor de mercado < R$ 2 bi → beta > 1 → receita +52,09% em 3 anos (15% a.a.) → 6 melhores em momentum (6 meses) |

Vaga que nenhuma ação preenche fica aplicada no CDI.

## Como rodar

Precisa de Python 3.11 ou mais novo (testado no 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

A execução leva cerca de 1 minuto. Os parâmetros gerais estão no começo de `main.py`, e os de cada carteira em `src/estrategia.py`.

O `backtest_grupo4.ipynb` traz o mesmo código e os resultados já executados. Para rodá-lo de novo, abra-o no VS Code ou no Jupyter com o kernel do `.venv`.

## Dados

Os arquivos do Economatica não vão para o Git. Baixe-os em frequência diária, com os mesmos tickers, e coloque-os em `data/`:

| Arquivo | Campo | Configuração |
|---|---|---|
| `fechamento.xlsx` | Fechamento | Ajustado por proventos, moeda original |
| `roic.xlsx` | ROIC (IC fim) | 12 meses, consolidado |
| `lucro_liquido.xlsx` | Lucro líquido (Dem result) | 12 meses, consolidado, em milhares |
| `receita_liquida.xlsx` | Receita líquida operacional (Dem result) | 12 meses, consolidado, em milhares |
| `valor_mercado.xlsx` | Valor de mercado | Da empresa, moeda original, em milhares |
| `volume.xlsx` | Volume$ | Moeda original, em milhares |
| `ibovespa.xlsx` | Fechamento do IBOV | Ajustado por proventos, moeda original |
| `CDI.xlsx` | Fechamento do CDI, classe Acumul | Ajustado por proventos, moeda original |

## Código

| Arquivo | Classe | Função |
|---|---|---|
| `src/base_dados.py` | `BaseDados` | Limpa as planilhas, define o universo e entrega o último balanço publicado |
| `src/estrategia.py` | `Estrategia`, `Defensiva`, `Agressiva` | Escolhe as ações em cada data |
| `src/backtest.py` | `Backtest` | Roda o loop da Aula 2 e calcula os retornos diários |
| `src/relatorio.py` | `Relatorio` | Salva os resultados |

## Resultados

Ficam em `output/`:

- `retorno_acumulado.png`: estratégia contra o Ibovespa e o CDI.
- `underwater.png`: queda em relação ao último topo.
- `piores_drawdowns.png`: os 5 piores períodos de queda.
- `metricas.txt`: métricas contra o Ibovespa e contra o CDI. O Sharpe desconta o CDI do período.
- `retornos_diarios.csv`: retorno diário da estratégia.
- `carteiras.csv`: ações escolhidas em cada rebalanceamento.

## Premissas

Definidas aqui porque a Entrega 1 não as fixa, ou traz valores diferentes entre os slides:

- **Liquidez:** mediana de pelo menos R$ 1 mi/dia nos últimos 3 meses, contando dia sem negócio como zero.
- **Várias classes:** só a mais negociada de cada empresa entra.
- **Balanços:** só são usados 90 dias depois da data de referência, para não olhar o futuro.
- **Calendário:** só pregões da B3. Data de rebalanceamento que cai em fim de semana ou feriado usa o pregão anterior.
- **Histórico curto:** ação com menos de 5 anos de bolsa calcula o downside deviation com o histórico que tem, no mínimo 1 ano, exigido pelo momentum.
- **Beta:** 1 ano de retornos diários contra o Ibovespa.
- **Crescimento:** 15% a.a., que aparece em dois slides; um terceiro cita 20%.
- **Nota da defensiva:** 60% para low vol, por causa da "prioridade à proteção contra quedas".
- **Custo:** 0,1% no primeiro dia de cada rebalanceamento, como no Handout 3.

## Limitações

- **Empresas que saíram da bolsa:** a base quase só tem empresas que seguem listadas, o que tende a inflar o resultado.
- **Pesos:** voltam a ser iguais todo dia, como no `.mean` do Handout 3.
- **Custo:** é fixo, não depende de quanto a carteira mudou.
- **Valor de mercado:** o corte de R$ 2 bi não é corrigido pela inflação.
- **Execução:** a ação é comprada no fechamento usado para escolhê-la, sem checar se o volume comporta a posição.
