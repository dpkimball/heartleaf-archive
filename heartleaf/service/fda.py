import datetime
import os
import re
import time
from queue import Queue
from threading import Thread
from lxml.html.clean import Cleaner
import requests
from bs4 import BeautifulSoup

from django.conf import settings

from heartleaf.service.consts.FDA_Substance import FDASubstance, TableColumns
from heartleaf.service.twinpeaks import TwinPeaks
from heartleaf.service.consts.TwinPeakActions import TwinPeakActions as TwinAct


class FDA:

    def __init__(self, logger):
        """
        Initialize the logging and TwinPeaks service
        :param logger:
        """
        self.logger = logger

        # set the TwinPeaks service
        self.rest_api = TwinPeaks(settings)

    def _parse_fda_substance_html(self, url=None, substance_dict=None):
        """
        Parse the HTML from the USDA substance page
        Currently retrieving 'Other Names' from the page
        https://www.accessdata.fda.gov/scripts/fdcc/index.cfm?set=FoodSubstances&id=ACACIAGUM

        ToDo
        In the future we can parse the definitions section

        *Definitions
        CAS Reg. No. (or other ID): Chemical Abstract Service (CAS) Registry Number® for the substance or a numerical code assigned by CFSAN to those substances that do not have a CAS Registry Number (977nnn-nn-n series).
        Substance: The name of the ingredient as recognized by CFSAN.
        Used for (Technical Effect): The physical or technical effect(s) the substance has in or on food; see 21 CFR 170.3(o) for definitions.
        21 CFR: Title 21 of the Code of Federal Regulations.
        FEMA No.: The trade association, Flavor and Extract Manufacturers Association (FEMA), has established expert panels to evaluate and make independent determinations on the GRAS status of flavoring substances. The FEMA number is provided here as a reference to FEMA’s GRAS assessments.
        The GRAS Pub. No. is the FEMA GRAS™ publication number.
        NLFG is no longer FEMA GRAS™.
        For more information about FEMA GRAS, see About the FEMA GRAS™ Program disclaimer icon.
        JECFA: The Joint Expert Committee on Food Additives (JECFA) is an international expert scientific committee that is administered jointly by the Food and Agriculture Organization of the United Nations (FAO) and the World Health Organization (WHO). See JECFA Specifications for Flavourings disclaimer icon

        :param url: substance url
        :param substance_dict: TwinPeaks json post data object
        :return: dictionary with 'Other Names'
        """

        if not substance_dict:
            substance_dict = self._create_substance_dict()

        if not url and not substance_dict[FDASubstance.SUBSTANCE_URL]:
            raise AttributeError()

        if not url:
            url = substance_dict[FDASubstance.SUBSTANCE_URL]

        successful = False
        attempts = 0

        # The USDA site can be flaky; attempt 10 times to retrieve the HTML
        while attempts < 10 and not successful:
            attempts += 1
            try:
                res = requests.get(url, timeout=30)
                cleaner = Cleaner(page_structure=False, links=False)
                html = cleaner.clean_html(res.text)
                soup = BeautifulSoup(html, 'lxml')
                rows = soup.find(id="detailTable").find_all("tr")
                successful = True
            except Exception as e:
                #  self.logger.exception("{}-{}".format(url, str(e)))
                time.sleep(5)
                pass

        if not successful:
            self.logger.warn("Unsuccessful scrape {}".format(url))
            return

        for row in rows:
            tc_text = row.find('td').text.strip()
            th_text = row.find('th').text.strip()
            if th_text == "CAS Reg. No. (or other ID):":
                continue
            if th_text == "Substance:":
                continue
            if th_text == "Other Names:":
                other_names = tc_text.split('♦')
                substance_dict["other_names"] = [
                    re.sub(r'[^\x00-\x7f]', r'', o).strip() for o in other_names
                    if o]
                return substance_dict

    def scrape(self, run_live=False):
        """
        Main entry point to scrape the USDA Substances website.  Iterates
        through a table of substances and spawns individual threads to parse
        the page.  Makes a secondary URL request for each substance to retrieve
        the substance's other Names.
        :param run_live:
        :return:
        """
        script_dir = os.path.dirname(__file__)
        rel_path = "fda_additives.html"
        html = None
        if run_live:
            res = requests.get(FDASubstance.INDEX_URL, timeout=30)
            cleaner = Cleaner(page_structure=False, links=False)
            html = cleaner.clean_html(res.text)
            rel_path = "fda_additives_{}.html".format(
                datetime.datetime.now().strftime('%s'))
            abs_file_path = os.path.join(script_dir, rel_path)
            file = open(abs_file_path, "w")
            file.write(html)
            file.close()
            # update the main one?
            # rename file
            self.logger.debug("Retrieve USDA HTML substance index page and saved to local")
        else:
            rel_path = "fda_additives.html"
            abs_file_path = os.path.join(script_dir, rel_path)
            file = open(abs_file_path, "r")
            html = file.read()
            self.logger.info("Loading local html")

        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find(id="summaryTable").find("tbody").find_all("tr")

        q = Queue(maxsize=0)
        thread_count = 10
        for i in range(thread_count):
            worker = Thread(target=self.parse_table_row, args=(q,))
            worker.setDaemon(True)
            worker.start()

        for row in rows:
            q.put(row)

        q.join()

    def parse_table_row(self, q):
        """
        Process an table row from the HTML.  This will contain the complete
        record for a substance
        :param q: queue object
        :return: None
        """
        while True:
            row = q.get()
            try:
                cells = row.find_all("td")
                col_number = 1
                current = FDA._create_substance_dict()
                for col in cells:
                    if col_number == TableColumns.AS_REG_NO:
                        current[FDASubstance.AS_REG_NO] = col.get_text().strip()
                    elif col_number == TableColumns.SUBSTANCE:
                        anchor = col.find('a')
                        current[FDASubstance.SUBSTANCE] = FDA.clean_text(col.text.strip())
                        current[FDASubstance.SUBSTANCE_URL] = FDASubstance.CFR_URL_FORMAT.format(anchor['href'])
                    elif col_number == TableColumns.TECHNICAL_EFFECT:
                        categories = []
                        children = col.text.strip().split(',')
                        if children:
                            [categories.append(
                                {FDASubstance.CATEGORY: FDA.clean_text(c)}) for c in
                             children if c]
                        else:
                            categories_labels = col.text.strip().split(',')
                            [categories.append({FDASubstance.CATEGORY: FDA.clean_text(c)}) for c in categories_labels if c]
                        current[FDASubstance.CATEGORIES] = categories
                    elif col_number == TableColumns.CFR:
                        crfs = []
                        children = col.find_all('a')
                        if children:
                            for c in children:
                                txt = c.text.strip()
                                if txt:
                                    crf = dict()
                                    crf['code'] = txt
                                    crf['href'] = c['href']
                                    crfs.append(crf)
                        else:
                            txt = col.text.strip().replace('<br>', '').replace('\n', '')
                            if txt:
                                crfs = txt.split(',')
                                crfs = [x.strip(' ') for x in crfs]
                        current[FDASubstance.CRF_21] = crfs
                    col_number += 1
                # inspect the substance page
                self._parse_fda_substance_html(substance_dict=current)

                # persist the data by sending to TwinPeaks
                self.rest_api.post_data(TwinAct.POST_INGREDIENT, post_data=current)
                self.logger.debug("Substance inserted {}".format(current))
            except Exception:
                self.logger.exception("Unable to process FDA substance row")
            finally:
                q.task_done()

    @staticmethod
    def clean_text(text):
        """
        Cleans up the string and removes html tags and ANSI characters
        :param text:
        :return:
        """
        text = ' '.join([x.strip() for x in text.split(',') if x])
        text = ' '.join([x.strip() for x in text.split('\n') if x])
        text = ' '.join([x.strip() for x in text.split('<br>') if x])
        return text

    @staticmethod
    def _create_substance_dict():
        item = dict()
        item[FDASubstance.SUBSTANCE] = None
        item[FDASubstance.SUBSTANCE_URL] = None
        item[FDASubstance.CATEGORIES] = []
        item[FDASubstance.AS_REG_NO] = None
        item[FDASubstance.CRF_21] = []
        item[FDASubstance.OTHER_NAMES] = []

        return item
