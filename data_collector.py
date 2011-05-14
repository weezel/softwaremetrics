#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpy2.robjects.packages import importr
from sys import exit
from sys import stderr
from xml.dom.minidom import parseString

import commands
import csv
import os
import rpy2.robjects as robjects


# Absolute path to SourceMonitor and also runnable binary must be included
sourcemonitor_cmd = "/ABSOLUTE_PATH/SourceMonitor.exe"
i = 1
revisions = 4861


def aggregator(revnro):
    inputfile = "checkpoints.xml"
    outputfile = "metrics.csv"

    # Lists that hold the metric data
    McCabes = []
    noStatements = []
    noMethodsCalled = []
    noMethods = 0
    metricsrow = []
    metricscsv = []

    infile = open(inputfile, "r")
    data = infile.read()
    xmldoc = parseString(data)
    infile.close()
    
    method_metrics = xmldoc.getElementsByTagName("method_metrics")
    metricsTags = xmldoc.getElementsByTagName("method")
    
    # Write metrics to a CSV file
    for file in method_metrics:
        noMethods += int(file.getAttribute("method_count"))
        
    #Parse XML and ignore incorrect metrics from SourceMonitor
    boundary = 100000
    for method in metricsTags:
        complextmp = int(method.getElementsByTagName("complexity").item(0).firstChild.data)
        statementstmp = int(method.getElementsByTagName("statements").item(0).firstChild.data)
        callstmp = int(method.getElementsByTagName("calls").item(0).firstChild.data)

        # Values that will exceed boundary value, are too big
        if complextmp > boundary or statementstmp > boundary or callstmp > boundary:
            continue
        else:
            McCabes.append(int(method.getElementsByTagName("complexity").item(0).firstChild.data))
            noStatements.append(int(method.getElementsByTagName("statements").item(0).firstChild.data))
            noMethodsCalled.append(int(method.getElementsByTagName("calls").item(0).firstChild.data))

    for i in range(len(McCabes)):
        metricsrow = []
        metricsrow.append(revnro)
        metricsrow.append(noMethods)
        metricsrow.append(McCabes[i])
        metricsrow.append(noStatements[i])
        metricsrow.append(noMethodsCalled[i])
        metricscsv.append(metricsrow)

    outputline = ""
    outfile = open(outputfile, "a")
    for i in range(len(metricscsv)):
        for j in range(len(metricscsv[i])):
            outputline += str(metricscsv[i][j]) + ","
        outputline = outputline.rstrip(",")
        outputline += "\n"
        outfile.write(outputline)
        outputline = ""
    outfile.close()
    
    r = robjects.r
    ineq = importr("ineq")
    moments = importr("moments")
    
    # Aggregate metrics
    meanMcCabe = r.mean(robjects.FloatVector(McCabes))[0]
    meanNoStatements = r.mean(robjects.FloatVector(noStatements))[0]
    meanNoMethodCalls = r.mean(robjects.FloatVector(noMethodsCalled))[0]
    
    medianMcCabe = r.median(robjects.FloatVector(McCabes))[0]
    medianNoStatements = r.median(robjects.FloatVector(noStatements))[0]
    medianNoMethodCalls = r.median(robjects.FloatVector(noMethodsCalled))[0]
    
    coeffMcCabe = ineq.var_coeff(robjects.FloatVector(McCabes))[0]
    coeffNoStatements = ineq.var_coeff(robjects.FloatVector(noStatements))[0]
    coeffNoMethodCalls = ineq.var_coeff(robjects.FloatVector(noMethodsCalled))[0]
    
    skewnessMcCabe = moments.skewness(robjects.FloatVector(McCabes))[0]
    skewnessNoStatements = moments.skewness(robjects.FloatVector(noStatements))[0]
    skewnessNoMethodCalls = moments.skewness(robjects.FloatVector(noMethodsCalled))[0]
    
    giniMcCabe = ineq.Gini(robjects.FloatVector(McCabes))[0]
    giniNoStatements = ineq.Gini(robjects.FloatVector(noStatements))[0]
    giniNoMethodCalls = ineq.Gini(robjects.FloatVector(noMethodsCalled))[0]
    
    theilMcCabe = ineq.Theil(robjects.FloatVector(McCabes))[0]
    theilNoStatements = ineq.Theil(robjects.FloatVector(noStatements))[0]
    theilNoMethodCalls = ineq.Theil(robjects.FloatVector(noMethodsCalled))[0]
    
    outputAggregated = "aggregated.csv"
     # Print aggregated metrics to a CSV file
    outfile = open(outputAggregated, "a")
    
    outputline = str(revnro) + "," + str(noMethods) + "," + str(meanMcCabe) + "," + str(meanNoStatements) + "," + str(meanNoMethodCalls) + ","
    outputline += str(medianMcCabe) + "," + str(medianNoStatements) + "," + str(medianNoMethodCalls) + ","
    outputline += str(coeffMcCabe) + "," + str(coeffNoStatements) + "," + str(coeffNoMethodCalls) + ","
    outputline += str(skewnessMcCabe) + "," + str(skewnessNoStatements) + "," + str(skewnessNoMethodCalls) + ","
    outputline += str(giniMcCabe) + "," + str(giniNoStatements) + "," + str(giniNoMethodCalls) + ","
    outputline += str(theilMcCabe) + "," + str(theilNoStatements) + "," + str(theilNoMethodCalls) + "\n"
    
    outfile.write(outputline)
    outfile.close()


def getAggregateHeaders():
    outputline = "Revision Nunber,Number of Methods,"
    outputline += "Mean McCabe,Mean Number of Statements,Mean Number of Method Calls,"
    outputline += "Median McCabe,Median Number of Statements,Median Number of Method Calls,"
    outputline += "Coeffecient of Variation McCabe,Coeffecient of Variation Number of Statements,Coeffecient of Variation Number of Method Calls,"
    outputline += "Skewness McCabe,Skewness Number of Statements,Skewness Number of Method Calls,"
    outputline += "Gini McCabe,Gini Number of Statements,Gini Number of Method Calls,"
    outputline += "Theil McCabe,Theil Number of Statements,Theil Number of Method Calls\n"
    return outputline


def getMetricsHeaders():
    return "RevisionNbr,NbrMethods,McCabe,NbrStatements,NbrMethodCalls\n"


def writeHeaders2files(f1, f2):
    try:
        tofile1 = open(f1, "w")
        tofile2 = open(f2, "w")
        tofile1.write(getMetricsHeaders())
        tofile2.write(getAggregateHeaders())
    except IOERROR, e:
        print "Cannot write to file: %s" % e
    finally:
        tofile1.close()
        tofile2.close()


#################################
# Main program starts from here #
#################################

#XXX dir1 = "itext/trunk/src"
#XXX dir2 = "itext/trunk/itext/src/main"

# Check whether the svn tree is checked out and we are in the right place
if os.path.exists("itext") == 0:
    print "Are you sure 'itext' folder is checked out via svn?"
    print "Otherwise, move navigate to the directory that you can ",
    print "see 'itext' directory in your current folder."
    exit(1)

# Remove previous run results
if os.path.exists("checkpoints.xml"):
    os.remove("checkpoints.xml")
if os.path.exists("itext_metrics.smp"):
    os.remove("itext_metrics.smp")
if os.path.exists("runresults.log"):
    os.remove("runresults.log")

# Generate headers for the metrics and aggregated metrics files
writeHeaders2files("metrics.csv", "aggregated.csv")

# Need to rewind to the 'first' commit. As 0-2 revisions does not include any
# .java code (at least in under src/) we consider this as the first.
print "Starting from the revision %d, the latest revision %d" % (i, revisions)
print
# At the first, begin from here
commands.getoutput("svn update -r %d itext/" % i)

# Cook sourcemonitor_cmd arguments
sourcemonitor_cmd = "%s %s %s" % ("wine", sourcemonitor_cmd, "/C smon_command.xml")


while i <= revisions:
    changed_files = "svn diff -r %d:%d --summarize itext/ |grep '\/src\/' |grep -ci .java" % (i - 1, i)

    # Count changed files
    cfiles_output = commands.getoutput(changed_files)
    print "%d-%d revisions, files touched: %d" % (i - 1, i, int(cfiles_output))
    # Log touched files between revisions to file
    try:
        log2file = open("runresults.log", "a")
        log2file.write("%d-%d revisions, files touched: %d\n" % (i - 1, i, int(cfiles_output)))
    except IOError, e:
        print "File error: %s" % e
    finally:
        log2file.close()


    # No changed java files -> no need to generate stats.
    # Speeds ups things dramatically
    if int(cfiles_output) > 0:
        # Generate Source Monitor stats
        stderr.write("Running SourceMonitor for current revision, please wait...\n")
        commands.getoutput(sourcemonitor_cmd)

        # Metrics calculations
        aggregator(i)
        os.remove("checkpoints.xml")
        os.remove("itext_metrics.smp")

    # Move to next revision
    stderr.write("Changing to revision %d, please wait...\n" % (i + 1))
    i += 1
    commands.getoutput("svn update -r %d itext/" % i)

