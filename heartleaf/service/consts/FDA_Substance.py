class FDASubstance:
    SUBSTANCE = "substance"
    SUBSTANCE_URL = "substance_url"
    CATEGORIES = "categories"
    CATEGORY = "category"
    AS_REG_NO = "as_reg_no"
    CRF_21 = "crf_21"
    OTHER_NAMES = "other_names"
    INDEX_URL = "https://www.accessdata.fda.gov/scripts/fdcc/index.cfm?set=FoodSubstances&sort=Sortterm&order=ASC&showAll=true&type=basic&search="
    CFR_URL_FORMAT = "https://www.accessdata.fda.gov/scripts/fdcc/index.cfm{}"


class TableColumns:
    """
    Table columns for the substance page
    https://www.accessdata.fda.gov/scripts/fdcc/index.cfm?set=FoodSubstances&sort=Sortterm&order=ASC&showAll=true&type=basic&search=
    """
    AS_REG_NO = 1
    SUBSTANCE = 2
    TECHNICAL_EFFECT = 3
    CFR = 4
