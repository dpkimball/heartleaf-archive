
class TwinPeaksUrls:
    ALL_RECEIPTS_URL = "{twinpeaks}/Receipts/?page=0"
    RECEIPTS_BY_ID = "{twinpeaks}/Receipts/{receipt_id}"
    GET_RECEIPT_ITEM_BY_ID = "{twinpeaks}/ReceiptItems/{receipt_id}/{receipt_item_id}"
    GET_USDA_FOOD_INFO = "{twinpeaks}/food/{usda_food_id}"
    POST_USDA_FOOD = "{twinpeaks}/food"
    GET_USDA_FOOD_BY_UPC = "{twinpeaks}/food/search/{barcodevalue}"
    GET_ALL_CATEGORIES = "{twinpeaks}/fc"
    POST_INGREDIENT = "{twinpeaks}/food/ingredient"
