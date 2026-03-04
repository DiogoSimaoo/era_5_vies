import pandas as pd
import numpy as np
from climQMBC.methods import QDM


era5_file = ""          # CSV de entrada ERA5 
obs_file = ""       # CSV: date + colunas = estações
coords_file = ""      # CSV: station, lat, lon
saida_file = "ERA5_corrigido.csv"

periodo_calib = ("1960-01-01", "2010-12-31")  # período para calibrar QDM
frq = "D"  # D=diário, M=mês
idw_p = 2  #  ponderação IDW


era5 = pd.read_csv(era5_file, parse_dates=["date"])
obs = pd.read_csv(obs_file, parse_dates=["date"])
coords = pd.read_csv(coords_file)  

era5.set_index("date", inplace=True)
obs.set_index("date", inplace=True)


era5_base = era5.loc[periodo_calib[0]:periodo_calib[1]]
obs_base = obs.loc[periodo_calib[0]:periodo_calib[1]]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


era5_corr = pd.DataFrame(index=era5.index)

for cell in era5.columns:
    lat_cell, lon_cell = map(float, cell.split("_"))

    dist = coords.apply(lambda row: haversine(lat_cell, lon_cell, row.lat, row.lon), axis=1).values

    pesos = 1 / (dist ** idw_p)
    pesos /= pesos.sum()

    ref_cell = np.zeros(len(obs_base))
    for i, station in enumerate(obs_base.columns):
        ref_cell += pesos[i] * obs_base[station].values

    print(f"Corrigindo célula: {cell}")
    era5_corr[cell] = QDM(era5[cell].values, ref_cell, frq=frq)


era5_corr.reset_index(inplace=True)
era5_corr.to_csv(saida_file, index=False)
print("Correção concluída! CSV guardado em:", saida_file)
