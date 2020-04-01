#! /usr/bin/env python2
from __future__ import absolute_import
import sys
sys.path.append("/home/umcg-jprofijt/analysis-metrics-prediction-display/src/scripts/python/")
import xml.etree.ElementTree as ET
import subprocess

import QualityParser as QP

import argparse

def parseRun(xml):
    tree = ET.parse(xml)

    root = tree.getroot()


    run = root.find("Run")
    number = root.get("Number")
    FlowCell = run.find("Flowcell")
    Sequencer = run.find("Instrument")
    Date = run.find("Date")
    return QP.SequencingRun(run.attrib["Id"], run.attrib["Number"], FlowCell.text, Sequencer.text, dateParser(Date.text.strip()))
    
def getInteropSummary(interop, summaryApplication):
    summary = subprocess.check_output([summaryApplication, interop, '--level=0', '--csv=1'])
    summaryList = summary.strip().split("\n")[3].split(",")[1:]
    QP.Summary
    sumarryObj = QP.Summary(
        float(summaryList[0]),
        float(summaryList[1]),
        float(summaryList[2]),
        summaryList[3],
        int(summaryList[4]),
        float(summaryList[5])
    )
    return sumarryObj


def insertToDB(runInfo, summary, database):
    RunID = database.addSequencingRun(runInfo)[0]
    database.addRunSummary(RunID, summary)

def createQuickParser(args, description):
    parser = argparse.ArgumentParser(description=description)
    for item in args:
        parser.add_argument(u"-{0}".format(item[0]), u"--{0}".format(item), type=unicode, required=True)
    
    return parser

def main():
    
    parser = createQuickParser(["runxml", "interop", "database", "executable"], "Parser for interop folders, inserts run summary to database")
    args = parser.parse_args()
    runInfo = parseRun(args.runxml)
    summary = getInteropSummary(args.interop, args.executable)
    database = QP.sqlite3Database(args.database)
    insertToDB(runInfo, summary, database)
    return 0

if __name__ == "__main__":
    sys.exit(main())