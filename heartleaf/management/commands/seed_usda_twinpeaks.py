import logging
from django.core.management.base import BaseCommand

from heartleaf.service import usda


class Command(BaseCommand):
    help = 'Populates TwinPeaks USDA database with Index'

    """
     TwinPeaks needs USDA database food index.  Their API requires the our
     system to use their 'id'.
     This can only be achieved by crawling their API and retrieving every record
     Once TwinPeaks has an index of all foods, TwinPeaks can be a secondary
     call to the API using their ID.  This will retrieve all food meta data
     about the item

     Note: The secondary call is performed by TwinPeaks.  TwinPeaks will collect
     the data and store it into an ElasticSearch engine.  The idea is to store
     all searchable food data in a search engine.

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

    python manage.py seed_usda_twinpeaks 0

    """

    def add_arguments(self, parser):
        parser.add_argument('offset', default=0, type=int)

        parser.add_argument(
            '--seed',
            action='store_true',
            dest='seed',
            help='Retrieve the USDA Food index and push to TwinPeaks',
        )

    def handle(self, *args, **options):
        logger = logging.getLogger("oxbow")
        offset = options['offset']
        if options['seed']:
            usda.USDAManager(logger).seed_index_usda_db(current_offset=offset)
            logger.info("Successfully persisted USDA into Search")
