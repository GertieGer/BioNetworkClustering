import numpy as np
import pandas as pd
import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'allLinuxRess.csv')
df = pd.read_csv(filename)

# methods = ['Louvain', 'GN_modularity', 'GN_conductance']
# random, remerge, relative = "TRUE", "FALSE", "FALSE"
# # df.groupby(["size", "method", "random"])["modularity", "conductance", "jaccard"].mean().to_csv(os.path.join(dirname, 'random_mean.csv'))
# # df.groupby(["size", "method", "random"])["modularity", "conductance", "jaccard"].var().to_csv(os.path.join(dirname, 'random_var.csv'))


# RANDOM
no_rnd = df.query('(random == False) & (remerge == False) & (relative == False)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
rnd = df.query('(random == True) & (remerge == False) & (relative == False)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
no_rnd = no_rnd.rename(columns={"modularity": "modularity no RND", "conductance": "conductance no RND","jaccard": "jaccard no RND"})
no_rnd["modularity with RND"] = rnd["modularity"]
no_rnd["conductance with RND"] = rnd["conductance"]
no_rnd["jaccard with RND"] = rnd["jaccard"]
no_rnd.to_csv(os.path.join(dirname, 'RANDOM.csv'))


# REMERGE
no_rnd = df.query('(random == False) & (remerge == False) & (relative == False)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
rnd = df.query('(random == False) & (remerge == True) & (relative == False)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
no_rnd = no_rnd.rename(columns={"modularity": "modularity no RMRG", "conductance": "conductance no RMRG","jaccard": "jaccard no RMRG"})
no_rnd["modularity with RMRG"] = rnd["modularity"]
no_rnd["conductance with RMRG"] = rnd["conductance"]
no_rnd["jaccard with RMRG"] = rnd["jaccard"]
no_rnd.to_csv(os.path.join(dirname, 'REMERGE.csv'))


# RELATIVE
no_rnd = df.query('(random == True) & (remerge == False) & (relative == False)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
rnd = df.query('(random == True) & (remerge == False) & (relative == True)').groupby(["method", "size"])[["modularity", "conductance", "jaccard"]].mean()
no_rnd = no_rnd.rename(columns={"modularity": "modularity no RLTV", "conductance": "conductance no RLTV","jaccard": "jaccard no RLTV"})
no_rnd["modularity with RLTV"] = rnd["modularity"]
no_rnd["conductance with RLTV"] = rnd["conductance"]
no_rnd["jaccard with RLTV"] = rnd["jaccard"]
no_rnd.to_csv(os.path.join(dirname, 'RELATIVE.csv'))



# for method in methods:
#     for size in [1000,10000]:
#         #mean = df.loc[(df["method"]==method) & (df["random"]==random), "random"]
#         filter = (df["method"]==method) & (df["random"]==random)
  
#         # filtering data
#         df.where(filter)
  
#         print(mean)





