from src.backtest import Backtest
from src.base_dados import BaseDados
from src.estrategia import Agressiva, Defensiva
from src.relatorio import Relatorio

DATA_INICIO = "2016-10-29"
DATA_FIM = "2026-10-29"
MESES_REBAL = 3
CUSTO = 0.001  # 0,1% descontado no primeiro dia de cada rebalanceamento
DEFASAGEM_DIAS = 90  # espera até o balanço ser publicado
VOLUME_MINIMO = 1_000  # R$ mil por dia: mediana da janela de liquidez
MESES_LIQUIDEZ = 3


def main():
    base = BaseDados("data", DEFASAGEM_DIAS, VOLUME_MINIMO, MESES_LIQUIDEZ)
    backtest = Backtest(base, [Defensiva(base), Agressiva(base)], DATA_INICIO, DATA_FIM, MESES_REBAL, CUSTO)
    retornos, carteiras = backtest.rodar()
    Relatorio("output").salvar(retornos, carteiras, base.retorno_ibov, base.retorno_cdi)


if __name__ == "__main__":
    main()
