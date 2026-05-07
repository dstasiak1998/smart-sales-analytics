import sys
from loguru import logger
from src.pipeline.extract import generate_sales, save_raw
from src.pipeline.transform import transform, save_processed
from src.pipeline.validate import validate_df
from src.pipeline.load import get_engine, init_db, load, get_row_count


logger.remove()
logger.add(
    sys.stdout,
    format="{time:HH:mm:ss} | {level:<8} | {message}",
    colorize=True,
)
logger.add(
    "data/pipeline.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="10 MB",
    retention="30 days",
)


def run_pipeline(
    n_records: int = 1000,
    mode: str = "replace",
    save_files: bool = True,
) -> None:
    """
    Uruchamia kompletny pipeline ETL.

    Args:
        n_records:  liczba rekordów do wygenerowania
        mode:       tryb zapisu do bazy — replace lub append
        save_files: czy zapisywać pliki CSV na dysk
    """
    logger.info("=" * 50)
    logger.info(f"START PIPELINE — {n_records} rekordów")
    logger.info("=" * 50)

    try:
        logger.info("[1/4] EXTRACT — generowanie danych")
        df_raw = generate_sales(n_records)
        if save_files:
            save_raw(df_raw)
        logger.success(f"Extract OK — {len(df_raw)} rekordów")

        logger.info("[2/4] TRANSFORM — czyszczenie i wzbogacanie")
        df_clean = transform(df_raw)
        if save_files:
            save_processed(df_clean)
        logger.success(f"Transform OK — {len(df_clean)} rekordów")

        logger.info("[3/4] VALIDATE — walidacja schematów")
        df_valid = validate_df(df_clean)
        logger.success(f"Validate OK — {len(df_valid)} rekordów")

        logger.info("[4/4] LOAD — zapis do bazy danych")
        engine = get_engine()
        init_db(engine)
        load(df_valid, engine, mode=mode)
        count = get_row_count(engine)
        logger.success(f"Load OK — {count} rekordów w bazie")

        logger.info("=" * 50)
        logger.success("PIPELINE ZAKOŃCZONY SUKCESEM")
        logger.info("=" * 50)

    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"PIPELINE BŁĄD: {e}")
        logger.error("=" * 50)
        raise


if __name__ == "__main__":
    run_pipeline(
        n_records=1000,
        mode="replace",
        save_files=True,
    )