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
sourcemonitor_cmd = "/home/weezel/apps/SourceMonitor/SourceMonitor.exe"
i = 0
revisions = 4860
#revisions = 53


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
    for method in metricsTags:
        if int(method.getElementsByTagName("complexity").item(0).firstChild.data) != 1550214256:
            McCabes.append(int(method.getElementsByTagName("complexity").item(0).firstChild.data))
        if int(method.getElementsByTagName("statements").item(0).firstChild.data) != 1550214256:
            noStatements.append(int(method.getElementsByTagName("statements").item(0).firstChild.data))
        if int(method.getElementsByTagName("calls").item(0).firstChild.data) != 1550214256:
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
    meanMcCabe = r.mean(robjects.IntVector(McCabes))[0]
    meanNoStatements = r.mean(robjects.IntVector(noStatements))[0]
    meanNoMethodCalls = r.mean(robjects.IntVector(noMethodsCalled))[0]
    
    medianMcCabe = r.median(robjects.IntVector(McCabes))[0]
    medianNoStatements = r.median(robjects.IntVector(noStatements))[0]
    medianNoMethodCalls = r.median(robjects.IntVector(noMethodsCalled))[0]
    
    coeffMcCabe = ineq.var_coeff(robjects.IntVector(McCabes))[0]
    coeffNoStatements = ineq.var_coeff(robjects.IntVector(noStatements))[0]
    coeffNoMethodCalls = ineq.var_coeff(robjects.IntVector(noMethodsCalled))[0]
    
    skewnessMcCabe = moments.skewness(robjects.IntVector(McCabes))[0]
    skewnessNoStatements = moments.skewness(robjects.IntVector(noStatements))[0]
    skewnessNoMethodCalls = moments.skewness(robjects.IntVector(noMethodsCalled))[0]
    
    giniMcCabe = ineq.Gini(robjects.IntVector(McCabes))[0]
    giniNoStatements = ineq.Gini(robjects.IntVector(noStatements))[0]
    giniNoMethodCalls = ineq.Gini(robjects.IntVector(noMethodsCalled))[0]
    
    theilMcCabe = ineq.Theil(robjects.IntVector(McCabes))[0]
    theilNoStatements = ineq.Theil(robjects.IntVector(noStatements))[0]
    theilNoMethodCalls = ineq.Theil(robjects.IntVector(noMethodsCalled))[0]
    
    #print "Mean McCabe: " + str(meanMcCabe)
    #print "Mean number of statements: " + str(meanNoStatements)
    #print "Mean number of methods called: " + str(meanNoMethodCalls)
    #
    #print
    #
    #print "Median McCabe: " + str(medianMcCabe)
    #print "Median number of statements: " + str(medianNoStatements)
    #print "Median number of methods called: " + str(medianNoMethodCalls)
    #
    #print
    #
    #print "Coeffecient of Variation McCabe: " + str(coeffMcCabe)
    #print "Coeffecient of Variation number of statements: " + str(coeffNoStatements)
    #print "Coeffecient of Variation number of methods called: " + str(coeffNoMethodCalls)
    #
    #print
    #
    #print "Skewness of McCabe: " + str(skewnessMcCabe)
    #print "Skewness of number of statements: " + str(skewnessNoStatements)
    #print "Skewness of number of methods called: " + str(skewnessNoMethodCalls)
    #
    #print 
    #
    #print "Gini McCabe: " + str(giniMcCabe)
    #print "Gini number of statements: " + str(giniNoStatements)
    #print "Gini number of methods called: " + str(giniNoMethodCalls)
    #
    #print
    #
    #print "Theil McCabe: " + str(theilMcCabe)
    #print "Theil number of statements: " + str(theilNoStatements)
    #print "Theil number of methods called: " + str(theilNoMethodCalls)
    
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

log2file = open("runresults.log", "a")

while i <= revisions:
    changed_files = "svn diff -r %d:%d --summarize itext/ |grep '\/src\/' |grep -ci .java" % (i - 1, i)

    # Count changed files
    cfiles_output = commands.getoutput(changed_files)
    print "%d-%d revisions, files touched: %d" % (i - 1, i, int(cfiles_output))
    log2file.write("%d-%d revisions, files touched: %d\n" % (i - 1, i, int(cfiles_output)))


    # No changed java files -> no need to generate stats.
    # Speeds ups things dramatically
    if int(cfiles_output) > 0:
        # Generate Source Monitor stats
        stderr.write("Running SourceMonitor for current revision, please wait...\n")
        commands.getoutput(sourcemonitor_cmd)

        # Code from Matias comes here
        aggregator(i)
        os.remove("checkpoints.xml")
        os.remove("itext_metrics.smp")

    # Move to next revision
    stderr.write("Changing to revision %d, please wait...\n" % (i + 1))
    i += 1
    commands.getoutput("svn update -r %d itext/" % i)

log2file.close()
