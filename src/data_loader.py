from io import BytesIO

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".parquet",
}


def load_dataset(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Carrega um dataset a partir de CSV, Excel ou Parquet.
    """

    file_name = file_name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(
            BytesIO(file_bytes),
            low_memory=False
        )

    elif file_name.endswith(".parquet"):
        df = pd.read_parquet(
            BytesIO(file_bytes)
        )

    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(
            BytesIO(file_bytes)
        )

    else:
        raise ValueError(
            "Formato de arquivo não suportado."
        )

    return df


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Otimiza tipos de dados para reduzir o consumo de memória.
    """

    df = df.copy()

    # Otimização de colunas numéricas
    for column in df.select_dtypes(
        include=["int64", "float64"]
    ).columns:

        if df[column].dtype == "int64":
            df[column] = pd.to_numeric(
                df[column],
                downcast="integer"
            )

        elif df[column].dtype == "float64":
            df[column] = pd.to_numeric(
                df[column],
                downcast="float"
            )

    # Conversão de strings de baixa cardinalidade
    for column in df.select_dtypes(
        include=["object"]
    ).columns:

        if len(df) > 0:

            cardinality_ratio = (
                df[column].nunique(dropna=False)
                / len(df)
            )

            if cardinality_ratio < 0.5:
                df[column] = df[column].astype("category")

    return df


def load_and_optimize_data(
    file_bytes: bytes,
    file_name: str
) -> pd.DataFrame:

    df = load_dataset(
        file_bytes,
        file_name
    )

    return optimize_dataframe(df)