import contextlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # salva os gráficos sem abrir janela

import quantstats as qs

FONTE = "DejaVu Sans"


class Relatorio:
    """Salva os retornos, as carteiras, as métricas e os gráficos da Aula 2."""

    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.pasta.mkdir(exist_ok=True)

    def salvar(self, retornos, carteiras, retorno_ibov, retorno_cdi):
        ibov = retorno_ibov.loc[retornos.index].rename("Ibovespa")
        cdi = retorno_cdi.loc[retornos.index].rename("CDI")

        retornos.to_csv(self.pasta / "retornos_diarios.csv")
        carteiras.to_csv(self.pasta / "carteiras.csv", index=False)
        self._salvar_metricas(retornos, ibov, cdi)

        qs.plots.returns(retornos.to_frame("Estratégia").join(cdi), ibov, fontname=FONTE, show=False,
                         savefig=self.pasta / "retorno_acumulado.png")
        qs.plots.drawdown(retornos, fontname=FONTE, show=False,
                          savefig=self.pasta / "underwater.png")
        qs.plots.drawdowns_periods(retornos, title="Estratégia", fontname=FONTE, show=False,
                                   savefig=self.pasta / "piores_drawdowns.png")

    def _salvar_metricas(self, retornos, ibov, cdi):
        cdi_anual = qs.stats.cagr(cdi)

        # Uma tabela por benchmark: com os dois juntos, o quantstats perde a duração dos drawdowns.
        with open(self.pasta / "metricas.txt", "w") as arquivo, contextlib.redirect_stdout(arquivo):
            for benchmark in (ibov, cdi):
                print(f"\n===== Estratégia vs {benchmark.name} =====")
                qs.reports.metrics(retornos, benchmark=benchmark, rf=cdi_anual, mode="full", display=True,
                                   strategy_title="Estratégia", benchmark_title=benchmark.name)
