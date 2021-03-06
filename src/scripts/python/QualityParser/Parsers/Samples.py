#! /usr/bin/env python
# pylint: disable=relative-beyond-top-level

from __future__ import with_statement
from __future__ import absolute_import
import csv, os, argparse, sys, shutil
from io import open
import datetime
from ..DataTypes import Files, Sample

class FilesAndFailDir(Files):
    def __init__(self, input, output, fail):
        Files.__init__(self, input, output)
        self.fail = fail
    
    def getFailLocation(self):
        return self.fail

class NoStartDateException(Exception):
    pass
    
    

def getItem(row, columnID):
    u"""
    Tries to get the item from column, If that fails enter NA

    :param row: dict with items in a row
    :param columnID: Column to parse from row
    :returns: item parsed from row
    :rtype: str
    """
    try:
        item = row[columnID]
        if len(item) == 0:
            item = u'NA'
    except KeyError:
        item = u'NA'
    return item

def appendToFile(newRow, file):
    u"""
    Adds a row of items to the file

    :param newRow: list of items to add in order
    :param file: file path
    :rtype: void
    """
    with open(file,'ab') as csvfile:
        csv.writer(csvfile).writerow(newRow)

def createFile(file, header = ['externalSampleID', 'Gender', 'sequencingStartDate', 'sequencer', 'prepKit', 'capturingKit', 'project']):
    u"""
    creates a new output file if it doesn't exist

    :param file: file path
    :param header: header to use for file, list of header names
    :rtype void
    """
    if not os.path.isfile(file):
        with open(file, 'wb') as newCsv:
            writer = csv.writer(newCsv, delimiter=',', quotechar='#', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
    
def parseSampleSheet(infile):
    u"""
    moves wanted columns from samplesheet to output csv

    :param infile: input sample sheet csv
    :param outfile: output sample sheet csv
    :param columns: columns to parse, list of column names
    :rtype: void
    """
    with open(infile, mode=u'r', errors='replace') as sampleSheet:
        reader = csv.DictReader(sampleSheet, delimiter=",")
        outList = []
        for row in reader:
            startDate = getItem(row, "sequencingStartDate")
            try:
                startDateAsDate = datetime.datetime.strptime(startDate.strip(), "%y%m%d").date()
            except ValueError:
                raise NoStartDateException()


            sample = Sample(getItem(row, "externalSampleID"), getItem(row, "sequencer"), getItem(row, "run"), getItem(row, "flowcell"), startDateAsDate, getItem(row, "project"), getItem(row, "capturingKit"))
            outList.append(sample)
    
    return outList
            

def writeDataToCsv(rows, outputfile):
    for sample in rows:
        appendToFile(sample.toList(), outputfile)


def parseArguments():
    # Python 2, disable unicode error
    # pylint: disable=undefined-variable
    u"""
    Uses argparse to parse input and output file from commandline
    
    :returns: file locations
    :rtype: class Files
    """
    parser = argparse.ArgumentParser(description=u'Parses sample sheet and adds to output file')
    parser.add_argument(u'-i', u'--input', type=unicode, metavar="path/to/input", help=u'Sample sheet to read', required=True)
    parser.add_argument(u'-o', u'--output', type=unicode, metavar="path/to/output", help=u'file to add results to', required=True)
    parser.add_argument(u'-f', u'--faildirectory', type=unicode, metavar="path/to/failedSamplesDirectory", help=u'directory to store failed samples', required=True)
    args = parser.parse_args()
    files = FilesAndFailDir(args.input, args.output, args.faildirectory)
    return files

def copyToFailed(input, storageDir):
    if not os.path.isdir(storageDir):
        os.mkdir(storageDir)
    shutil.copy(input, storageDir)


def IndexSamples():
    u"""
    Main function, calls argparser, then checks output file by calling createFile, and finally proccesses Sample sheet

    :returns: exit code
    :rtype: int
    """
    fileContainer = parseArguments()

    createFile(fileContainer.getOutput())
    try:
        samples = parseSampleSheet(fileContainer.getInput())
        writeDataToCsv(samples, fileContainer.getOutput())
    except (UnicodeEncodeError, NoStartDateException):
        copyToFailed(fileContainer.getInput(), fileContainer.getFailLocation())

    return 0

if __name__ == u"__main__":
    sys.exit(IndexSamples())
    

