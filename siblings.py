from functions import *
from kidsinlaw import *



def getsiblings(psn):
    sl = []; sm = []; sml = []; smr = []; sr = []
    if psn.dad is not None and psn.mom is not None:
        for kid in psn.dad.kids:
            if not kid in psn.mom.kids: sl.append(kid)
            else: sm.append(kid)
        for kid in psn.mom.kids:
            if not kid in psn.dad.kids: sr.append(kid)
    elif psn.dad is None and psn.mom is not None:
        sm = psn.mom.kids
    elif psn.dad is not None and psn.mom is None:
        sm = psn.dad.kids
    elif psn.dad is None and psn.mom is None:
        sm = [psn]
    
    i = sm.index(psn)
    sml = sm[:i]
    smr = sm[i+1:]
    return sl, sml, smr, sr
#    return sm[:i], sm[i+1:]




def set_zpsn_siblings(people,zpsn,mode='c'):
    sl, sml, smr, sr = getsiblings(zpsn)
    sl = sl+sml
    sr = smr+sr

    if (mode=='r'):
        sr = sl+sr; sl=[]
    elif (mode=='l'):
        sl = sl+sr; sr=[]
    if (len(zpsn.spouse)==2):
        xl = -2; xr = 2
    elif (len(zpsn.spouse)==1):
        if (zpsn.sex=='M'): xl = -1; xr = 2
        elif (zpsn.sex=='F'): xl = -2; xr = 1
        else: print('ERROR 65',zpsn.sex)
    else: xl = -1; xr = 1
    xl += zpsn.x; xr += zpsn.x
    

    for s in sr:
        ddx=0
        if (len(s.spouse)==2 or (len(s.spouse)==1) and s.sex=='F'): ddx =1
        set_desc_spouse(people,s,x=xr+ddx,y=zpsn.y)
        xr += (1+len(s.spouse))

    for s in reversed(sl):
        xl -= len(s.spouse)
        ddx=0
        if (len(s.spouse)==2 or (len(s.spouse)==1) and s.sex=='F'): ddx =1
        set_desc_spouse(people,s,x=xl+ddx,y=zpsn.y)
        xl -= 1
    
    # insert person and/or spouses to the siblings:
    if (len(zpsn.spouse)==2):
        if (zpsn.spouse[0].x < zpsn.spouse[1].x): il = 0; ir = 1
        else:  il = 1; ir = 0
        sl += [zpsn.spouse[il]]
        sr.insert(0,zpsn.spouse[ir])
    elif (len(zpsn.spouse)==1):
        if (zpsn.sex=='M'):
            sl += [zpsn]
            sr.insert(0,zpsn.spouse[0])
        elif (zpsn.sex=='F'):
            sl += [zpsn.spouse[0]]
            sr.insert(0,zpsn)
    else: # single
        sl.insert(len(sl),zpsn)
        sr.insert(0,zpsn)


    shift(sr,1,'r','c',zpsn.y-1)
    resetflags(people)
    shift(sl,1,'l','c',zpsn.y-1)
    resetflags(people)



