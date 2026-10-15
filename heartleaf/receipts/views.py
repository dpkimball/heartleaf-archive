from django.conf import settings
from django.http import (HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseServerError)
from django.template import loader
from django.shortcuts import render, Http404
from heartleaf.service.twinpeaks import TwinPeaks
from heartleaf.service.consts.TwinPeakActions import TwinPeakActions as TwinAct
from heartleaf.service.exceptions.TwinPeaksException import (
    TwinPeaksService404,
    TwinPeaksServiceError,
    TwinPeaksServiceAuthError)

rest_api = TwinPeaks(settings)


def index(request):

    html = rest_api.get_data(TwinAct.GET_ALL_RECEIPTS)
    if html:
        html = html['content']

    template = loader.get_template('heartleaf/index.html')
    context = {
        'latest_receipt_list': html,
    }
    return HttpResponse(template.render(context, request))


def receipt_detail(request, receipt_id):
    """
    Render the Receipts page listing all of the items in a receipt
    :param request:
    :param receipt_id:
    :return:
    """
    def extract_category(json):
        """
        Retrieve the category id if available
        :param json:
        :return:
        """
        try:
            return int(json['category'])
        except KeyError:
            return 0

    # get the receipt from TwinPeaks
    receipt = rest_api.get_data(TwinAct.GET_RECEIPT_BY_ID, receipt_id=receipt_id)

    # get all of the categories from TwinP
    all_categories = rest_api.get_data(TwinAct.GET_ALL_CATEGORIES)
    if all_categories:
        categories = {}
        for c in all_categories['content']:
            categories[c['id']] = c['category']

    if receipt:
        food_items = receipt['receiptItems']
        food_items.sort(key=extract_category, reverse=True)

    return render(request, 'heartleaf/receipt.html',
                  {'settings': settings,
                   'receipt': receipt,
                   'receipt_items': food_items,
                   'categories': categories})


def receipt_item(request, receipt_id, receipt_item_id):
    """
    Render the receipt item: an Object with a barcode (hopefully)
    :param request:
    :param receipt_id:
    :param receipt_item_id:
    :return:
    """
    try:
        receipt_json = rest_api.get_data(
            TwinAct.GET_RECEIPT_ITEM_BY_ID,
            receipt_id=receipt_id,
            receipt_item_id=receipt_item_id)
        score = {'health': 'A', 'environment': 'B'}
    except TwinPeaksService404:
        raise Http404("Receipt does not exist")
    except TwinPeaksServiceAuthError:
        return HttpResponseForbidden("Unable to authorize")
    except TwinPeaksServiceError:
        return HttpResponseServerError("TwinPeaks returned a 500")
    return render(request, 'heartleaf/item.html',
                  {'food': receipt_json, 'score': score, })
