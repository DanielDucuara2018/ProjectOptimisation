FenetresTotal = 623
f = open("downloadPlan18st24hNous.txt", "r")
a = []
for x in f:    
    _,_,c,_,_ = x.split(" ")    
    a.append(c)
    print(c)  
    
newa = list(set(a))
nombreFenetreUtiliseNous = len(newa)/FenetresTotal*100
f.close()

f = open("downloadPlan18st24hOriginal.txt", "r")
a = []
for x in f:    
    _,_,c,_,_ = x.split(" ")    
    a.append(c)
    print(c)  
    
newa = list(set(a))
nombreFenetreUtiliseOrignal = len(newa)/FenetresTotal*100
f.close()

