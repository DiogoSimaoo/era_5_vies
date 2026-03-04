import pandas as pd
from climQMBC.methods import QDM

era5_file = ""          # CSV de entrada ERA5
obs_file = ""        # CSV da estação
saida_file = ""  # CSV de saída

periodo_calib = ("1960-01-01", "2010-12-31")  # período para calibrar QDM
frq = "D"  # D=diário, M=mês


era5 = pd.read_csv(era5_file, parse_dates=["date"])
obs = pd.read_csv(obs_file, parse_dates=["date"])

era5.set_index("date", inplace=True)
obs.set_index("date", inplace=True)


era5_base = era5.loc[periodo_calib[0]:periodo_calib[1]]
obs_base = obs.loc[periodo_calib[0]:periodo_calib[1]]


ref_base = obs_base.iloc[:, 0].values


era5_corr = pd.DataFrame(index=era5.index)

for cell in era5.columns:
    print(f"Corrigindo célula: {cell}")
    era5_corr[cell] = QDM(era5[cell].values, ref_base, frq=frq)


era5_corr.reset_index(inplace=True)
era5_corr.to_csv(saida_file, index=False)

print("Correção concluída! CSV guardado em:", saida_file)
