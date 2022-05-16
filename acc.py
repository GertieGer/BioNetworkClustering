

def acc(G,arr):
    m=0
    N=0
    I=0
    m2=0
    N2=0
    for A in arr:
        m=0
        for B in arr:
            if (A!=B):
                h= A.intersection(B)
                if(m<len(h)):
                    m=len(h)
                    m2=len(B)
        N+=len(A)
        I+=m
        N2+=m2
    sen=I/N
    p=I/N2
    res=sen*p
    res=res**0.5
    return res
                    
        
        
