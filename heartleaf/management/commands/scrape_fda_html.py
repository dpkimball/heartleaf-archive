from django.core.management.base import BaseCommand
from heartleaf.service.fda import FDA

import logging


class Command(BaseCommand):
    """
    The USDA does NOT contain an API for all of the information linking
    'Terms' to additives.  It will define what an additive is but does not
    connect the USDA food database (ingredients) to what the FDA has outlined
    what is a Food Additive.  There is NO API.  ONLY HTML Pages.

    For example, it will define TBHQ has a food additive
    but this needs to achieved by scraping the website for the information

    Starts off at this link
    https://www.accessdata.fda.gov/scripts/fdcc/index.cfm?set=FoodSubstances&sort=Sortterm&order=ASC&showAll=true&type=basic&search=

    This contains a table of all 'Substances' added to food.  This will
    traverse through the table and scrape the contents for each substance
    and send the data to TwinPeaks.

    TwinPeaks will now be able to iterate through each food's ingredient
    and see if the food ingredient is listed in this list.

    Essentially we are mapping every food item content to a potential food
    additive

    Command
    ------------------------------------------------------------
    Prerequisites:
        Server Environment variables:
            PYTHONUNBUFFERED=1
            TWIN_PEAKS_VERSION=<version>
            HEARTLEAF_POSTGRES_NAME=<database name>
            HEARTLEAF_POSTGRES_PORT=<port>
            HEARTLEAF_POSTGRES_HOST=<host>
            HEARTLEAF_POSTGRES_USER=<database user>
            HEARTLEAF_POSTGRES_PASSWORD=<password>
            TWIN_PEAKS_HOST=<twin peaks host>
            TWIN_PEAKS_PORT=<twin peaks port>
            TWIN_PEAKS_REST_TOKEN=<twin peaks token>

    python manage.py scrape_fda_html
    """
    help = 'Scrape FDA HTML'

    def add_arguments(self, parser):
        parser.add_argument('run_live', default=True, nargs='?', type=bool)

    def handle(self, *args, **options):
        logger = logging.getLogger("oxbow")
        scraping = FDA(logger)

        # are we running with a live scrape from the USDA
        # (the last scrape was stored locally to facilitate debugging)
        run_live = options['run_live']
        logger.info("Running live: {}".format(run_live))
        scraping.scrape(run_live)
