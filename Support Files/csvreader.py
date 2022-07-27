import csv
files = {}
with open('res.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i==0: continue # ingnore header
        net, method, secs, mod, cond, acc = row
        if net=="***": continue
        if not net in files:
            files[net] = {}
        if not "remerge" in method:
            files[net][method]={"unmerged":[float(secs), float(mod), float(cond), float(acc)], "merged":[]}
        else:
            files[net][method[:-8]]["merged"]=[float(secs), float(mod), float(cond), float(acc)]

# how many times did merge help modularity?
merge_per_method = {}
method_help = {} # method_help[girvna][merged][mod] = [3%, -5%..] help 
method_res = {} # method_help[girvna][merged][mod] = [0.45, 0.123..]  
count={}

for file in files:
    if not "1000" in file: continue
    l_secs, l_mod, l_cond, l_acc = files[file]["normal louvain"]["unmerged"]
    for method in files[file]:
        if not method in count:
            count[method] = {1000:0, 10000:0}
        if "10000" in file:
            count[method][10000]+=1
        else: count[method][1000]+=1

        if not method in method_help:
            method_help[method]={"merged":{"secs":[], "mod":[], "cond":[], "acc":[]}, 
            "unmerged":{"secs":[], "mod":[], "cond":[], "acc":[]}}
            method_res[method]={"merged":{"secs":[], "mod":[], "cond":[], "acc":[]}, 
            "unmerged":{"secs":[], "mod":[], "cond":[], "acc":[]}}

        if not method in merge_per_method:
            merge_per_method[method] = [] 
        no_merge = files[file][method]["unmerged"][1]
        if len(files[file][method]["merged"])>0:
            merge = files[file][method]["merged"][1]
            merge_per_method[method].append(100*(merge-no_merge)/no_merge) 

        for merge_type in files[file][method]:
            if len(files[file][method][merge_type])>0:
                secs, mod, cond, acc = files[file][method][merge_type]
                method_help[method][merge_type]["secs"].append(100*(secs-l_secs)/l_secs)
                method_help[method][merge_type]["mod"].append(100*(mod-l_mod)/l_mod)
                method_help[method][merge_type]["cond"].append(100*(cond-l_cond)/l_cond)
                method_help[method][merge_type]["acc"].append(100*(acc-l_acc)/l_acc)
                method_res[method][merge_type]["secs"].append(secs)
                method_res[method][merge_type]["mod"].append(mod)
                method_res[method][merge_type]["cond"].append(cond)
                method_res[method][merge_type]["acc"].append(acc)

# print("average merge help by method:")
# tot_sum = 0
# tot_len = 0
# for method in merge_per_method:
#     if len(merge_per_method[method]):
#         avg_help = sum(merge_per_method[method])/len(merge_per_method[method])
#         tot_sum += sum(merge_per_method[method])
#         tot_len += len(merge_per_method[method])
#         print("\t"+method+": "+str(round(avg_help, 3))+"%")
    
# print("\t"+"total: "+str(round(tot_sum/tot_len, 3))+"%")

# method_help[girvna][merged][mod] = [3%, -5%..] help 
print("compared to louvain (no merge):")
for method in merge_per_method:
    if method == "normal louvain": continue
    
    for mergetype in ["unmerged"]:
        print("\t"+method+" "+mergetype+f": (ran on {count[method][1000]} 1000 nets, and {count[method][10000]} 10000 nets)")
        for atr in method_res[method][mergetype]:
            stats = method_help[method][mergetype][atr]
            avg_help = sum(stats)/len(stats)
            print("\t\t"+atr+": "+str(round(avg_help, 5))+"%")

# print("average sizes:")
# for method in merge_per_method:
#     for mergetype in ["unmerged", "merged"]:
#         if method == "normal louvain" and mergetype=="merged": continue
#         line=method+" "+mergetype
#         for atr in ["secs", "mod", "cond", "acc"]:
#             stats = method_res[method][mergetype][atr]
#             avg = sum(stats)/len(stats)
#             line+=","+str(avg)
#         print(line)
            
    
 

