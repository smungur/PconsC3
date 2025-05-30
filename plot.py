import csv
import statistics
import matplotlib.pyplot as plt
import numpy as np


def load_csv(path):
    rows = []
    precisions = []
    precisions_plus = []
    length_family = []
    color = []

    csv_file = open(path)
    csv_reader = csv.reader(csv_file, delimiter=',')
    fields = next(csv_reader)
    
    to_add = True
    color.append('red')
    color.append('blue')
    color.append('green')
    color.append('yellow')
    # extracting each data row one by one
    for row in csv_reader:
        if to_add == True:
            for i in range(4):
                precisions.append(float(row[1]))
                precisions_plus.append(float(row[2]))
                length_family.append(float(row[4]))
            to_add=False
        rows.append(row)
        precisions.append(float(row[1]))
        precisions_plus.append(float(row[2]))
        length_family.append(float(row[4]))
        if row[-1] == "αβ":
            color.append('green')
        elif row[-1] == "α":
            color.append('red')
        elif row[-1] == "β":
            color.append('blue')
        else:
            color.append('yellow')

    return precisions,precisions_plus, length_family, color


def get_average(precisions, length_family):
    stop = False
    while not stop:#SORT
        stop = True
        for i in range(len(length_family)-1):
            if length_family[i] > length_family[i+1]:
                tmp = length_family[i]
                length_family[i] = length_family[i+1]
                length_family[i+1] = tmp
                tmp = precisions[i]
                precisions[i] = precisions[i+1]
                precisions[i+1] = tmp
                stop = False

    #Cut into small set and get the average
    number_of_cut = 10
    chunks= len(length_family)/number_of_cut
    i = 0
    averagelist=[]
    size = []
    for j in range(number_of_cut):
        averagelist.append(np.mean(precisions[i:int(i+chunks)]))
        size.append(length_family[i])
        i = int(i+chunks)
    return averagelist, size




def pointPlot(precisions,length_family, color):
    av_point, size = get_average(precisions,length_family)


    fig, ax = plt.subplots()

    for i in range(len(precisions)):
        ax.plot(length_family[i], precisions[i], 'o', color=color[i])
    
    ax.plot(size,av_point,color="black")


    ax.legend(["α","β","αβ","Rest"])
        
    ax.set_xticks([1, 10, 100, 200, 500, 1000, 2000, 5000, 10000])
    ax.set_xscale('log')
    ax.set_ylabel("PPV")
    ax.set_xlabel("Size of the family in the a3m file")
    plt.show()

def tablePlot(precisions,color):
    alpha=[]
    beta=[]
    alphabeta=[]
    rest=[]
    for i in range(len(color)):
        if color[i] == "green":
            alphabeta.append(precisions[i])
        elif color[i] == "red":
            alpha.append(precisions[i])
        elif color[i] == "blue":
            beta.append(precisions[i])
        else:
            rest.append(precisions[i])

    print("Global: ", np.mean(precisions)," and length: ", len(precisions))
    print("Alpha: ", np.mean(alpha)," and length: ", len(alpha))
    print("Beta: ", np.mean(beta)," and length: ", len(beta))
    print("AlphaBeta: ", np.mean(alphabeta)," and length: ", len(alphabeta))
    print("Rest: ", np.mean(rest)," and length: ", len(rest))




path_to_csv = "csv/results_summary.csv" #Modify if needed
precisions, precisions_plus, length_family, color = load_csv(path_to_csv)
pointPlot(precisions,length_family,color)
pointPlot(precisions_plus,length_family,color)
tablePlot(precisions,color)
tablePlot(precisions_plus,color)
