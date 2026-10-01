from datetime import datetime
from zoneinfo import ZoneInfo


SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")


def to_local_datetime(value: datetime) -> datetime:
    """
    Converte um datetime armazenado em UTC
    para o horário de São Paulo.
    """

    utc_datetime = value.replace(
        tzinfo=ZoneInfo("UTC")
    )

    local_datetime = utc_datetime.astimezone(
        SAO_PAULO_TZ
    )

    return local_datetime.strftime(
        "%d/%m/%Y %H:%M"
    )