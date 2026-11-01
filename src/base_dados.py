import pandas as pd


class BaseDados:
    """Lê os arquivos do Economatica: data no índice, uma coluna por ação, NaN onde falta dado."""

    def __init__(self, pasta, defasagem_dias, volume_minimo, meses_liquidez):
        self.pasta = pasta
        self.defasagem = pd.Timedelta(days=defasagem_dias)
        self.volume_minimo = volume_minimo
        self.meses_liquidez = meses_liquidez

        # Dia sem negócio mantém o preço anterior, para o retorno não sumir da conta.
        self.precos = self._acoes("fechamento").ffill()
        self.retornos = self.precos.pct_change(fill_method=None)
        self.roic = self._acoes("roic")
        self.lucro = self._acoes("lucro_liquido")
        self.receita = self._acoes("receita_liquida")
        self.valor_mercado = self._acoes("valor_mercado")
        self.volume = self._acoes("volume")
        self.retorno_ibov = self._retorno_indice("ibovespa")
        self.retorno_cdi = self._retorno_indice("CDI")

    def _ler(self, nome):
        bruto = pd.read_excel(f"{self.pasta}/{nome}.xlsx", header=None, engine="calamine")
        linha = bruto.index[bruto[0] == "Data"][0]  # o cabeçalho muda de linha entre os arquivos
        tabela = bruto.loc[linha + 1:].set_index(0)
        tabela.index = pd.to_datetime(tabela.index).rename("Data")
        tabela.columns = bruto.loc[linha, 1:].str.split("\n").str[-1].str.strip()
        return tabela.apply(pd.to_numeric, errors="coerce").sort_index()

    def _acoes(self, nome):
        # O filtro descarta a coluna sem ticker que o Economatica coloca depois da data.
        return self._ler(nome).filter(regex=r"^[A-Z0-9]+$").dropna(how="all")

    def _retorno_indice(self, nome):
        indice = self._ler(nome).iloc[:, 0].reindex(self.precos.index).ffill()
        return indice.pct_change(fill_method=None)

    def ultimo_pregao(self, data):
        return self.precos.loc[:data].index[-1]

    def universo(self, data):
        """Classe mais negociada de cada empresa, entre as ações líquidas na data."""
        inicio = data - pd.DateOffset(months=self.meses_liquidez)
        volume = self.volume.loc[inicio:data].fillna(0).median()
        liquidas = volume[volume >= self.volume_minimo]
        return liquidas.groupby(lambda ticker: ticker[:4]).idxmax().tolist()

    def ultimo_balanco(self, tabela, data):
        """Último balanço já publicado: a defasagem evita usar informação do futuro."""
        corte = data - self.defasagem
        return tabela.loc[corte - pd.DateOffset(months=6):corte].ffill().iloc[-1]
