import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import re

class Task:
    """Tasks"""
    def __init__(self, description, activity, predecessors, days):
        self.description = description
        self.activity = activity.upper()
        self.predecessors = predecessors
        self.days = days
        self.earlyStart = 0
        self.earlyFinish = 0
        self.successors = []
        self.latestStart = 0
        self.latestFinish = 0
        self.slack = 0
        self.critical = 0
        
    def computeSlack(self):
        self.slack = self.latestFinish - self.earlyFinish
        if self.slack > 0:
            self.critical = 'no'
        else:
            self.critical = 'yes'


def readData(filename):
    """Read data function Get data and return a pandas data frame"""
    sheet = pd.read_csv(filename)
    return (sheet)

# create task object from pandas data frame
def createTask(mydata):
    """dfdd"""
    taskObject = []  
    for i in range(len(mydata)):
        taskObject.append(Task(mydata['description'][i], mydata['activity'][i], mydata['predecessors'][i], mydata['days'][i]))
    print(taskObject)
    return (taskObject)

def forwardPass(taskObject):
    """dfdd"""
    for task in taskObject:
        if type(task.predecessors) is str: #type string
            task.predecessors = task.predecessors.upper()
            ef=[]
            for j in task.predecessors:
                for t in taskObject:
                    if t.activity == j:
                        ef.append(t.earlyFinish) #changed
                task.earlyStart = max(ef)
            del ef
        else:
            task.earlyStart = 0
        task.earlyFinish = task.earlyStart + task.days

        
def backwordPass(taskObject):
    pred = []
    eF =[]
    for task in taskObject:
        if type(task.predecessors) is str: #type string
            for j in task.predecessors:
                print(j)
                pattern = re.compile(r'[A-Z]')

                match = pattern.finditer(j)
                for r in match:
                    pred.append(j)
                    for m in taskObject:
                        if m.activity == j:
                            m.successors.append(task.activity)
        eF.append(task.earlyFinish)
    for task in reversed(taskObject):
        if task.activity not in pred:
            task.latestFinish = max(eF)
        else:
            minLs = []
            for x in task.successors:
                for t in (taskObject):
                    if t.activity == x:
                        minLs.append(t.latestStart)
            task.latestFinish = min(minLs)
            del minLs
        task.latestStart = task.latestFinish - task.days


def slack(taskObject):
    for task in taskObject:
        task.computeSlack()
        
def updateDataFrame(df, TaskObject):
    df2 = pd.DataFrame({
        'description': df['description'],
        'activity': df['activity'],
        'predecessors': df['predecessors'],
        'days': df['days'],
        'es': pd.Series([task.earlyStart for task in TaskObject]),
        'ef': pd.Series([task.earlyFinish for task in TaskObject]),
        'ls': pd.Series([task.latestStart for task in TaskObject]),
        'lf': pd.Series([task.latestFinish for task in TaskObject]),
        'slack': pd.Series([task.slack for task in TaskObject]),
        'critical': pd.Series([task.critical for task in TaskObject]),
    })
    return (df2)
           
def main():
    os.system('clear')
    df = readData('critical_path_data.csv')
    taskObject = createTask(df)
    forwardPass(taskObject)
    backwordPass(taskObject)
    slack(taskObject)
    finaldf = updateDataFrame(df, taskObject)
    print(finaldf)
    
main()