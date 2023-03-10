from enum import Enum


class FORMATS_SUPPORTED(Enum):
    CSV = "csv"
    TSV = "tsv"
    JSON = "json"


VK_GENDERS = {
    0: "Пол не указан",
    1: "Женский",
    2: "Мужской",
}
