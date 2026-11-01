import pandas as pd


class Backtest:
    """Loop da Aula 2: em cada rebalanceamento, escolhe as ações e mede o retorno até o próximo."""

    def __init__(self, base, estrategias, data_inicio, data_fim, meses_rebal, custo):
        self.base = base
        self.estrategias = estrategias
        self.data_inicio = pd.Timestamp(data_inicio)
        self.data_fim = pd.Timestamp(data_fim)
        self.rebal_time = pd.DateOffset(months=meses_rebal)
        self.custo = custo

    def rodar(self):
        retornos, carteiras = [], []
        data_atual = self.data_inicio
        while data_atual + self.rebal_time <= self.data_fim:
            data_prox_rebal = data_atual + self.rebal_time
            pregao = self.base.ultimo_pregao(data_atual)
            selecao = {estrategia: estrategia.selecionar(pregao) for estrategia in self.estrategias}

            retornos.append(self._retorno_periodo(selecao, pregao, self.base.ultimo_pregao(data_prox_rebal)))
            carteiras += [{"data": pregao.date(), "carteira": type(estrategia).__name__, "n_acoes": len(tickers),
                           "tickers": " ".join(tickers)} for estrategia, tickers in selecao.items()]
            data_atual = data_prox_rebal
        return pd.concat(retornos).rename("Estrategia"), pd.DataFrame(carteiras)

    def _retorno_periodo(self, selecao, pregao, prox_pregao):
        acoes = self.base.retornos.loc[pregao:prox_pregao].iloc[1:]
        cdi = self.base.retorno_cdi.loc[acoes.index]
        retorno = 0
        for estrategia, tickers in selecao.items():
            # Cada vaga sem ação que passe nos filtros fica aplicada no CDI.
            vagas_vazias = estrategia.n_acoes - len(tickers)
            retorno_carteira = (acoes[tickers].sum(axis=1) + vagas_vazias * cdi) / estrategia.n_acoes
            retorno = retorno + estrategia.peso * retorno_carteira
        retorno.iloc[0] -= self.custo
        return retorno
