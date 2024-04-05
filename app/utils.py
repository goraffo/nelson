import pandas as pd

def cargar_datos():
    # Asegúrate de usar el path correcto a tu archivo Excel
    data_path = 'data/240401_edec_indexDOM.xlsx'
    df = pd.read_excel(data_path)

    # Convertir la columna 'lanzamiento' a datetime
    df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')

    # Opcional: Verificar el tipo de dato de la columna después de la conversión
    print(df['inicio'].dtype)

    return df
