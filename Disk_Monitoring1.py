import Kmeans_Clustering
import os
import codecs
import csv
import pandas as pd
import math

path = '/media/vivek/Personal/Vivek/Song_Fu_Research/LANL-SMART'
s = []
serial = []
file = []
serial_null = []
csv_writer = []
meta = ['disk_num', 'Serial Num', 'Device id', 'Timestamp']
meta_val = []
for root, dirs, files in os.walk(path): #walks through all your directories, folders and files
    for file1 in files:
        with codecs.open(os.path.join(root, file1), "r", encoding="utf8", errors='ignore') as full_file:
            lines = full_file.read().split('\n')
            # edit this num_new according to your path
            size = os.stat(root + '/' + file1).st_size
            if (size != 0):
                num = file1.split('-')
                # print(num_new[0])
                # print(num_new[1])
                start = 0
                end = 0
                i = 0
                header_flag = 0
                flag_serial = 0
                print("..")
                for indx,line in enumerate(lines):
                    if 'Drive ' in line:
                        dri = line.split(' ')
                    if 'DRIVE ' in line:
                        dri = line.split(' ')
                    if 'Serial Number:' in line:
                        sernum = line.split('  ')
                        # end = 0
                    elif 'Device Model:' in line:
                        devmodel = line.split('  ')
                    elif 'Local Time is:' in line:
                        time = line.split('  ')
                    if line.find("SMART Error Log Version") == 0:
                        flag_serial = 0
                        temp_writer = open('Data_CSV/'+words[-1] + '.csv', 'a')
                        csv_writer = csv.writer(temp_writer, lineterminator='\n')
                        # *********** Comment below two lines after first time execution *************
                        if (header_flag == 1):
                            csv_writer.writerow([header[i] for i in range(0, len(header))])
                            header_flag = 0
                        # ******************************************************************************
                        csv_writer.writerow([attr_val[i] for i in range(0, len(attr_val))])
                        start = 0;
                        temp_writer.close()
                        # csv_writer.close()
                        if flag_serial == 1:
                            f.close()
                    if line.find("SSMART Error Log Version") == 0:
                        flag_serial = 0
                        temp_writer = open('./Data_CSV/'+words[-1] + '.csv', 'a')
                        csv_writer = csv.writer(temp_writer, lineterminator='\n')
                        # *********** Comment below two lines after first time execution *************
                        if (header_flag == 1):
                            csv_writer.writerow(header[i] for i in range(0, len(header)))
                            header_flag = 0
                        # ******************************************************************************
                        csv_writer.writerow([attr_val[i] for i in range(0, len(attr_val))])
                        start = 0;
                        temp_writer.close()
                        # csv_writer.close()
                        if flag_serial == 1:
                            f.close()
                    if (start == 1 and line.strip() != ''):
                        # write = line[:28]
                        split = (line.split())
                        if (flag_serial == 1):
                            f.write(split[0] + ' ' + split[1])
                            header.append(split[0] + '_val')  # dynamiclly appends the SMART attributes
                            header.append(split[0] + '_raw')
                            f.write("\n")
                        try:
                            attr_val.append(split[3])
                            attr_val.append(split[9])
                        except:
                            print("out of range exception")
                    if line.find("ID#") == 0:
                        start = 1;
                        attr_val = [num[0] + '_' + dri[1], sernum[-1], devmodel[-1], time[-1]]
                        header = ['disk_num', 'Serial Num', 'Device id', 'Timestamp']
                    if 'Device Model: ' in line:
                        words = line.split(' ')
                        if (not words[-1] in serial):
                            serial.append(words[-1])
                            write_file = words[-1] + '.txt'
                            f = open('./Data_CSV/'+write_file, 'w')
                            flag_serial = 1
                            header_flag = 1


print("finding replaced disks")
# replaced disks
#serial=['SSDSC2BA100G3','ST8000AS0002-1NA17Z']

final1 = None
for name in serial:
    df = pd.read_csv('./Data_CSV/'+name + '.csv') #opening the above generated .csv file
    f = open('./Data_CSV/'+name + '.txt', 'r')
    cols = ['disk_num', 'Serial Num', 'Device id', 'Timestamp']
    for line in f:
        k = line.split(' ')
        cols.append(k[0] + '_val')
        cols.append(k[0] + '_raw')
    df = df[cols]
    #Groubby function is used to extract if there is a change

    df['index'] = df.index
    idx = df.groupby(['disk_num', 'Serial Num'], sort=False)['index'].transform(max) == df['index']
    final = df[idx]
    idx1 = final.groupby(['disk_num'], sort=False)['index'].transform(max) != final['index']
    final1 = final[idx1]
    del final1['index']
    final1.to_csv('./Data_CSV/'+name + '_replaced' + '.csv', index=False)
print(serial)

# kmeans if replaced disks are present
for name in serial:
    df = pd.read_csv('./Data_CSV/'+name + '_replaced' + '.csv')
    f = open('./Data_CSV/'+name + '.txt', 'r')
    col = []
    for line in f:
        k = line.split(' ')
        col.append(k[0] + '_val')
        col.append(k[0] + '_raw')
    # print(col)
    df = df[col]
    # if there are no replacements the following if condition is true
    if len(df) == 0:
        print("No Disk replacements in drive with Device Model:", name)
        df = pd.read_csv('./Data_CSV/'+name + '.csv')
        df['index'] = df.index
        idx = df.groupby(['disk_num', 'Serial Num'], sort=False)['index'].transform(max) == df['index']
        final = df[idx]
        del final['index']
        final.to_csv('./Data_CSV/'+name + '_withoutreplacement' + '.csv', index=False)
        df = pd.read_csv('./Data_CSV/'+name + '_withoutreplacement' + '.csv')
        df = df[col]
        test = Kmeans_Clustering.kmean(df, col)
        # In this if the replacements are 1 ---> there is no enough data to perform clustering
        if len(test) == 1:
            print("There is no enough data to clustering")
        else:
            df['kmeans'] = test
            # print(df.head())
            df.sort_values(by=['kmeans'], inplace=True)
            df.to_csv('./Data_CSV/'+name + '_kmeans' + '.csv', index=False)
            df.reset_index()
            # print(centroids)
    #if there is a replacement then else condition is true
    else:
        test = Kmeans_Clustering.kmean(df, col)

        if len(test) == 1:
            print("There is no enough data to clustering")
        else:
            df['kmeans'] = test
            df.sort_values(by=['kmeans'], inplace=True)
            df.to_csv('./Data_CSV/'+name + '_kmeans' + '.csv', index=False)
            df.reset_index()

#Calculating the Decile Values using the formula math.ceil
#serial=['SSDSC2BA100G3','ST8000AS0002-1NA17Z']
list_kmeans=[]
values_kmeans=[]
values_kmeans_new=[]

for name in serial:
    df = pd.read_csv('./Data_CSV/'+name + '_kmeans' + '.csv')
    values=df['kmeans'].value_counts()
    for i in range(len(values)):
        k=values[i]
        values_kmeans.append(k) #stores the number of files in each cluster i.e, K Values
        for j in range(1,11):
            print(j,'---',k)
            l=math.ceil(j*0.1*k)
            print(l)
            list_kmeans.append(l) # stores all the Calculated Decile values
# Since we get seperate indices for each cluster it is difficult to extract from singel file. So, here we create a list
# such that we add this to the above list to match the indices of the generated .csv file

    test1=0
    val=0
    val_len = len(values_kmeans)
    for i in range(val_len):
        val = test1+val
        test1=values_kmeans[i]
        values_kmeans_new.append(val) #stores basic Kmeans vales
    final=[]
    k=0
    fi=0
    for i in range(len(values_kmeans_new)):
        for j in range(0,10):
            kf=k+j
            fin=list_kmeans[kf]+values_kmeans_new[i] #add them to extract from .csv file
            final.append(fin-1)
        k=k+10
    print(list_kmeans)
    print(values_kmeans)
    print(values_kmeans_new)
    print(final)

# To extract the rows which are mentioned in 'final' the below logic is written. Since it is difficult
#  to extract the rows we transpose the .csv file and extract them using column names

    df = df.transpose()
    df.to_csv('./Data_CSV/'+name + '_kmeans_transpose' + '.csv', index=True)
    f = open('./Data_CSV/'+name + '.txt', 'r')
    col = []
    for line in f:
        k = line.split(' ')
        col.append(k[0] + '_val')
        col.append(k[0] + '_raw')
        # print(col)
    col.append('kmeans')

# since we use writerow function the columns which we extracted from the above .csv file are converted to row format again.

    temp_writer = open('./Data_CSV/'+name+'_kmeans_Decile_intermediatefile'+ '.csv', 'w')
    csv_writer = csv.writer(temp_writer, lineterminator='\n')
    csv_writer.writerow(col)
    for i in final:
        csv_writer.writerow(df[i])
    temp_writer.close()
    # since they are converted to rows again we need to transpose to get in required format
    df = pd.read_csv('./Data_CSV/'+name + '_kmeans_Decile_intermediatefile' + '.csv')
    df = df.transpose()
    df.to_csv('./Data_CSV/'+name + '_kmeans_Decile_Finalfile' + '.csv')
    list_kmeans = []
    values_kmeans = []
    values_kmeans_new = []
    final = []

print("\n")
print("completed")
