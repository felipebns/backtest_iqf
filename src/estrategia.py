from abc import ABC, abstractmethod

import pandas as pd


class Estrategia(ABC):
    """Regra de seleção de uma carteira. Em cada data, só usa informação até aquela data."""

    peso = None
    n_acoes = None

    def __init__(self, base):
        self.base = base

    @abstractmethod
    def selecionar(self, data):
        """Devolve a lista de tickers escolhidos na data."""

    def _momentum(self, data, meses):
        janela = self.base.precos.loc[data - pd.DateOffset(months=meses):data]
        return janela.iloc[-1] / janela.iloc[0] - 1


class Defensiva(Estrategia):
    """P/L < 20 → ROIC > 10% (30 melhores) → 14 melhores em low vol (60%) e momentum (40%)."""

    peso = 0.70
    n_acoes = 14
    pl_maximo = 20
    roic_minimo = 10
    n_melhores_roic = 30
    peso_low_vol = 0.60
    anos_low_vol = 5
    meses_momentum = 12

    def selecionar(self, data):
        valor_mercado = self.base.valor_mercado.loc[:data].iloc[-1]
        lucro = self.base.ultimo_balanco(self.base.lucro, data)
        pl = (valor_mercado / lucro)[self.base.universo(data)]
        baratas = pl[(pl > 0) & (pl < self.pl_maximo)].index

        roic = self.base.ultimo_balanco(self.base.roic, data)[baratas]
        melhores = roic[roic > self.roic_minimo].nlargest(self.n_melhores_roic).index

        downside = self._downside_deviation(data)[melhores]
        momentum = self._momentum(data, self.meses_momentum)[melhores]
        nota = (self.peso_low_vol * downside.rank()
                + (1 - self.peso_low_vol) * momentum.rank(ascending=False))
        # dropna: com poucas ações, o nsmallest manteria quem não tem histórico.
        return nota.dropna().nsmallest(self.n_acoes).index.tolist()

    def _downside_deviation(self, data):
        inicio = data - pd.DateOffset(years=self.anos_low_vol)
        negativos = self.base.retornos.loc[inicio:data].clip(upper=0)
        return (negativos ** 2).mean() ** 0.5


class Agressiva(Estrategia):
    """Valor de mercado < R$ 2 bi → beta > 1 → receita +52,09% em 3 anos → 6 melhores em momentum."""

    peso = 0.30
    n_acoes = 6
    valor_mercado_maximo = 2_000_000  # R$ mil
    beta_minimo = 1
    anos_beta = 1
    crescimento_minimo = 0.5209
    anos_crescimento = 3
    meses_momentum = 6

    def selecionar(self, data):
        valor_mercado = self.base.valor_mercado.loc[:data].iloc[-1][self.base.universo(data)]
        small_caps = valor_mercado[valor_mercado < self.valor_mercado_maximo].index

        beta = self._beta(data, small_caps)
        volateis = beta[beta > self.beta_minimo].index

        crescimento = self._crescimento_receita(data)[volateis]
        crescem = crescimento[crescimento > self.crescimento_minimo].index

        momentum = self._momentum(data, self.meses_momentum)[crescem]
        # dropna: com poucas ações, o nlargest manteria quem não tem histórico.
        return momentum.dropna().nlargest(self.n_acoes).index.tolist()

    def _beta(self, data, tickers):
        inicio = data - pd.DateOffset(years=self.anos_beta)
        acoes = self.base.retornos.loc[inicio:data, tickers]
        ibov = self.base.retorno_ibov.loc[inicio:data]
        return acoes.apply(lambda retorno: retorno.cov(ibov)) / ibov.var()

    def _crescimento_receita(self, data):
        antes = data - pd.DateOffset(years=self.anos_crescimento)
        receita_antes = self.base.ultimo_balanco(self.base.receita, antes)
        receita = self.base.ultimo_balanco(self.base.receita, data)
        return receita / receita_antes.where(receita_antes > 0) - 1
