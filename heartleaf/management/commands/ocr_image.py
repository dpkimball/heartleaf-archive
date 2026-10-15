import datetime
import re
import string
from cStringIO import StringIO

from django.core.management.base import BaseCommand

import logging


class Command(BaseCommand):

    def __init__(self):
        self.__categories__ = ['Meat', 'Deli', 'Produce', 'Dairy', 'Bakery',
                               'Grocery']
        self.foundMeat = False
        self.foundDeli = False
        self.foundProduce = False
        self.foundDairy = False
        self.foundBakery = False
        self.foundGrocery = False
        self.foundDate = False
        self.foundStore = False

        self.store_id = None
        self.address = None
        self.Telephone = None
        self.StoreDirectory = None

        self.Meats = []
        self.Deli = []
        self.Produce = []
        self.Dairy = []
        self.Bakery = []
        self.Grocery = []

        self.n1 = None
        self.n1Stripped = None
        self.receiptStringIO = None

        self.find_name = None

    @staticmethod
    def find_store(text="Store:  77"):
        return re.findall(r'Store:.* (\d+)', text)

    @staticmethod
    def find_desc(line):
        # 1.67 lb @ 1 1b / 1.69
        m = None
        m1 = re.search(r'(\d*\.\d{1,2}) lb @ .* (\d+) lb / .* (\d*\.\d{1,2})',
                       line)
        m2 = re.search(r'(\d+) @ (\d+)/ .* (\d*\.\d{1,2})', line)
        description = None
        if m1:
            m = m1
        elif m2:
            m = m2
        if m:
            description = '%s \t %s \t %s' % (
                m.group(1).strip(string.whitespace),
                m.group(2).strip(string.whitespace),
                m.group(3).strip(string.whitespace))
        else:
            line2 = line.replace(' 0 ', ' @ ')
            line2 = line2.replace(' O ', ' @ ')
            line2 = line2.replace(' Tb ', ' lb ')
            m1 = re.search(
                r'(\d*\.\d{1,2}) lb @ .* (\d+) lb / .* (\d*\.\d{1,2})', line2)
            m2 = re.search(r'(\d+) @ (\d+)/ .* (\d*\.\d{1,2})', line)
            if m1:
                m = m1
            elif m2:
                m = m2
            if m:
                description = '%s \t %s \t %s' % (
                    m.group(1).strip(string.whitespace),
                    m.group(2).strip(string.whitespace),
                    m.group(3).strip(string.whitespace))

        return description

    def read_line(self):
        self.n1 = self.receiptStringIO.readline()
        self.n1Stripped = self.n1.strip(string.whitespace)

    def read_file(self):
        with open(self.file_name, "r") as ocr_receipt:
            receiptIO = ocr_receipt.read()
            self.receiptStringIO = StringIO(receiptIO)

    def parse(self, file):
        self.find_name = file
        self.read_file()
        self.read_line()
        while self.n1:
            if not self.foundStore:
                self.store_id = self.findStore(self.n1Stripped)
                if self.store_id:
                    self.foundStore = True
                    self.read_line()

            if not self.foundDate:
                matchObj = re.search(r'(\d+/\d+/\d+) .* (\d+:\d+:\d+)',
                                     self.n1Stripped)
                if matchObj:
                    self.foundDate = True
                    date_object = matchObj.group(1) + " " + matchObj.group(2)
                    purchaseDate = datetime.datetime.strptime(date_object,
                                                              "%d/%m/%y %H:%M:%S")
                    self.readLine()

            if self.foundDate:
                if self.n1Stripped in self.__categories__:
                    print
                    30 * '-'
                    print
                    self.n1Stripped
                    currentCategory = self.n1Stripped
                    self.readLine()

            # determine if the line item is two lines
            description = self.findDesc(self.n1Stripped)
            if description:
                self.readLine()

            itemMatch1 = re.search(r'(.*) (\d*\.\d{1,2}).*([FT])([FT])',
                                   self.n1Stripped)
            itemMatch2 = re.search(r'(.*) (\d*\.\d{1,2}).*([FT])',
                                   self.n1Stripped)
            itemMatch = None
            itemFound = None
            if itemMatch1:
                itemMatch = itemMatch1
                print
                itemMatch.group(1).strip(
                    string.whitespace), "\t", itemMatch.group(2).strip(
                    string.whitespace), "\t", itemMatch.group(3).strip(
                    string.whitespace), "\t", itemMatch.group(4).strip(
                    string.whitespace), "\t", description
            elif itemMatch2:
                itemMatch = itemMatch2
                print
                itemMatch.group(1).strip(
                    string.whitespace), "\t", itemMatch.group(2).strip(
                    string.whitespace), "\t", itemMatch.group(3).strip(
                    string.whitespace), "\t", description

            if itemMatch:
                # print '<--- item or description found --->'
                # print itemFound
                self.readLine()
            elif self.foundDate and description:
                print
                '<--- item or description missing --->', self.n1Stripped
                self.n1Stripped2 = self.n1Stripped.replace(' 0 ', ' @ ')
                self.n1Stripped2 = self.n1Stripped.replace(' O ', ' @ ')
                self.n1Stripped2 = self.n1Stripped2.replace(' Tb ', ' lb ')
                print
                self.n1Stripped2
                self.readLine()
            elif not self.n1Stripped:
                self.readLine()
            else:
                print
                '<--- help --->\t', self.n1Stripped
                self.readLine()
