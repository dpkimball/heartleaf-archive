import logging
import requests
from string import Formatter
from heartleaf.service.consts.TwinPeakActions import TwinPeakActions as TwinAct
from heartleaf.service.consts.TwinPeaksUrls import TwinPeaksUrls as TwinUrl
from heartleaf.service.exceptions.TwinPeaksException import (
    TwinPeaksServiceError, TwinPeaksServiceAuthError, TwinPeaksService404)

logger = logging.getLogger("oxbow")


class _UnseenFormatter(Formatter):
    def get_value(self, key, args, keywords):
        """
        Retrieves a value for a given key
        :param key: attribute name
        :param args:
        :param keywords: keywords
        :return:
        """
        if isinstance(key, str):
            try:
                return keywords[key]
            except KeyError:
                return key
        else:
            return Formatter.get_value(key, args, keywords)


class TwinPeaks:

    def __init__(self, settings):
        """
        Initializes a singleton instance to make calls the TwinPeaks server
        :param settings:
        """
        self.host = settings.TWIN_PEAKS_REST
        self.token_dic = {
            'Authorization': 'Bearer {}'.format(settings.TWIN_PEAKS_REST_TOKEN)}
        self.urls = {}
        self._load_urls()

    def _get_url(self, action, **kwargs):
        """
        Returns a twin peaks url based on an action
        :param action:
        :return:
        """
        kwargs['twinpeaks'] = self.host
        if action:
            fmt = _UnseenFormatter()
            return fmt.format(self.urls[action], **kwargs)
        else:
            return self.urls[action].format(twinpeaks=self.host)

    def get_data(self, action, **kwargs):
        """
        Attempts to retrieve data from the TwinPeaks application filtered by
        the action
        :param action:
        :return:
        """
        try:
            url = self._get_url(action, **kwargs)
            r = requests.get(url, headers=self.token_dic, timeout=30)
        except Exception as e:
            logger.exception(str(e))
            raise TwinPeaksServiceError("Unable to connect to TwinPeaks")

        if r.status_code == 500:
            logger.error(str("Server Error returned by TwinPeaks"))
            raise TwinPeaksServiceError("Server Error returned by TwinPeaks")
        if r.status_code == 403:
            logger.error(str("Unable to authorize to TwinPeaks"))
            raise TwinPeaksServiceAuthError("Unable to authorize to TwinPeaks")
        if r.status_code == 404:
            logger.warning(str("Unable to locate receipt {}".format(kwargs)))
            raise TwinPeaksService404("Unable to locate receipt")

        html = r.json()

        return html

    def post_data(self, action, post_data, **kwargs):
        """
        Posts data to the TwinPeaks API
        :param action:
        :param post_data:
        :param kwargs:
        :return:
        """
        try:
            url = self._get_url(action, **kwargs)
            r = requests.post(url, headers=self.token_dic, json=post_data, timeout=30)
        except Exception as e:
            logger.exception(str(e))
            raise TwinPeaksServiceError("Unable to connect to TwinPeaks")

        if r.status_code == 403:
            raise TwinPeaksServiceAuthError("Unable to authorize to TwinPeaks")
        if r.status_code not in (200, 201):
            logger.error(
                "Unsuccessful request to post data to TwinPeaks {}".format(
                    r.status_code))
            raise TwinPeaksService404(
                "Unsuccessful request to post data to TwinPeaks")

    def _load_urls(self):

        self.urls = {
            TwinAct.GET_ALL_RECEIPTS: TwinUrl.ALL_RECEIPTS_URL,
            TwinAct.GET_RECEIPT_BY_ID: TwinUrl.RECEIPTS_BY_ID,
            TwinAct.GET_RECEIPT_ITEM_BY_ID: TwinUrl.GET_RECEIPT_ITEM_BY_ID,
            TwinAct.GET_USDA_FOOD_INFO: TwinUrl.GET_USDA_FOOD_INFO,
            TwinAct.GET_USDA_FOOD_INFO_BY_UPC: TwinUrl.GET_USDA_FOOD_BY_UPC,
            TwinAct.GET_ALL_CATEGORIES: TwinUrl.GET_ALL_CATEGORIES,
            TwinAct.POST_INGREDIENT: TwinUrl.POST_INGREDIENT,
            TwinAct.POST_USDA_FOOD: TwinUrl.POST_USDA_FOOD
        }
