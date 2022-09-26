# %%

#new addition
"""
from overview file in each of the excel we read what all clusters are there in that excel
Then we loop over the list of above found clusters and add them to a dict with the key of cluster name. This helps us bring together the common clusters. So there can be none common thus one cluster in the list. Or if two excel has the same cluster we'll have 
two cluster in the list
{
"cluster_name": [list of found clusters from each excel]
}
We also create another dict that has the cluster name as key but the value has the project name where the cluster was found. This dict will be used to add project names in the final csv as a column,
"""
import os,copy
import pandas as pd
import xlrd
from collections import defaultdict


folder = '.'
files = os.listdir(folder)
clustered_list = defaultdict(list)
projects = defaultdict(list)
for file in files:
     
    if file.endswith('.xls'):
        print(f"reading file {file}")
        df = pd.read_excel(os.path.join(folder,file),sheet_name='Overview')
        clusters = df['Component'].to_list()
        for sheet in clusters[2:-1]:
            df1 = pd.read_excel(os.path.join(folder,file),sheet_name=sheet,skiprows=4)
            # print(df)

            df1 = df1[df1['Action'] == 'Unset Unreviewed']
            # df1["Cluster"]= sheet
            df1.insert(0,'Cluster',sheet)
            # df1["Project"] = '_'.join([file.split('_')[0],file.split('_')[1]])
            clustered_list[sheet].append(df1)
            projects[sheet].append('_'.join([file.split('_')[0],file.split('_')[1]]))
    # projects.append('_'.join([file.split('_')[0],file.split('_')[1]]))

        

       

# %%
#find out unique elements
print("finding unique deviations")
final_df = pd.DataFrame(columns=['Cluster','Project','File', 'Warning Type', 'Red', 'Grey', 'Orange', 'Priority Class',
       'Line', 'Column', 'Details', 'Comment', 'Action', 'ASIL System',
       'Third Party File', 'Auto Code', 'Critical Orange Check',
       'Solution Provided', 'Clarifications'])
for cluster,values in clustered_list.items():
    print(cluster,len(values))
    copy_val = copy.deepcopy(values)
    for idx,df in enumerate(copy_val):
    #    df['Project'] = projects[cluster][idx]
       df.insert(1,'Project', projects[cluster][idx])
    if len(copy_val)>1:
       temp = pd.concat(copy_val).drop_duplicates(['File','Line','Column'],keep=False).reset_index(drop=True)
       final_df= pd.concat([final_df,temp]).reset_index(drop=True)
    elif len(copy_val) == 1:
        final_df= pd.concat([final_df,temp]).reset_index(drop=True)
        final_df=final_df[final_df.File != "SFL_manual_stubs.c"]
       # print(temp)
# final_df.to_csv("polyspace_results/unique.csv")
# with pd.ExcelWriter("blah.xls") as writer:
#     final_df.to_excel(writer, sheet_name="unique_dev")

# %%
#new addition
"""
we loop over the cluster dict and find out the common column and line.
we also add a column that project names
"""
print("finding common deviations")
from functools import reduce
final_df_1 = pd.DataFrame(columns=['Cluster','File', 'Warning Type', 'Red', 'Grey', 'Orange', 'Priority Class',
       'Line', 'Column', 'Details', 'Comment', 'Action', 'ASIL System',
       'Third Party File', 'Auto Code', 'Critical Orange Check',
       'Solution Provided', 'Clarifications'])
li = []
for cluster,values in clustered_list.items():
    #print(cluster,len(values))
    if len(values)>1:
        df = (reduce(lambda x,y: pd.merge(x,y, on=['File','Column','Line'], how='inner',suffixes=('', '_y')), values))
        # print(df.filter(regex='.*(?!Project)_y$').columns)
        df.drop(df.filter(regex='_y$').columns, axis=1, inplace=True)
        # df['projects'] = '|'.join(projects[cluster])
        df.insert(1,'Projects','|'.join(projects[cluster]))
        li.append(df)
    # print(df.index)
final_df_1 = pd.concat(li,axis=0,ignore_index=True)
final_df_1=final_df_1[final_df_1.File != "SFL_manual_stubs.c"]
# final_df['Projects'] = '|'.join(projects)
# final_df.to_csv(f'polyspace_results/final_parsed.csv')
with pd.ExcelWriter("./deviations.xls") as writer:
    final_df_1.to_excel(writer, sheet_name="common_dev")
    final_df.to_excel(writer, sheet_name="unique_dev")


# %%



