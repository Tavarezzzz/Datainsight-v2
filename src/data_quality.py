import pandas as pd


def get_data_quality(df: pd.DataFrame) -> dict:
    """
    Calcula métricas básicas de qualidade do dataset.
    """

    if df.empty:
        return {
            "rows": 0,
            "columns": 0,
            "missing_values": 0,
            "missing_percentage": 0,
            "duplicates": 0,
            "completeness": 0,
        }

    total_cells = df.shape[0] * df.shape[1]

    missing_values = int(
        df.isna().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    completeness = (
        100
        - (missing_values / total_cells * 100)
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": missing_values,
        "missing_percentage": round(
            missing_values / total_cells * 100,
            2
        ),
        "duplicates": duplicates,
        "completeness": round(
            completeness,
            2
        ),
    }


def detect_outliers(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    """
    Detecta outliers usando o método IQR.
    """

    if column not in df.columns:
        raise ValueError(
            f"Coluna '{column}' não encontrada."
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise TypeError(
            "A coluna precisa ser numérica."
        )

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return df[
        (df[column] < lower_bound)
        | (df[column] > upper_bound)
    ]