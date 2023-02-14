
# returns person, its spouses and its decendents (including descendents spouses)
def allkids(psn):
    ret = [psn]
    for hb in psn.husb:
        if hb.x is not None: ret += [hb]
    for wf in psn.wife:
        if wf.x is not None: ret += [wf]
    for kid in psn.kids:
        ret += allkids(kid)
    return ret


# returns the left and right contours of the descendents tree:
# contl (r) : min (max) x values of the tree, index 0: psn, index 1: psn's kids and their spouses, etc
def contour_kids(ppl):
    allkds = []
    for psn in ppl: allkds += allkids(psn)
    xyd = []
    allkds += ppl
    for kid in allkds:
        if kid.x is None or kid.y is None: continue
        xyd.append([kid.x,kid.y])
    for i in range(len(xyd)):
        xyd[i][1] = int(xyd[i][1]-psn.y)
    
    yd = list(set([xyd[i][1] for i in range(len(xyd))]))

    xval = [[] for i in range(len(yd))]
    for i in range(len(xyd)):
        xval[xyd[i][1]].append(xyd[i][0])

    contl=[min(x) for x in xval]
    contr=[max(x) for x in xval]
    return contl,contr


def spouses(p1,p2):
    for hb in p1.husb:
        if (hb==p2): return True
    for wf in p1.wife:
        if (wf==p2): return True
    return False

# assume p1 is left of p2: returns minimal distance between their descendent's trees (distance from node CENTER)
# i.e. =1 means ok, <1 means slight overlap, <0 means large overlap
# i.e. p2 has to be shifted 1-dx to the right 

def distance_contours(c1l, c1r, c2l, c2r):
    n=min(len(c1r),len(c2l))
    dxs = [c2l[i]-c1r[i] for i in range(n)]
    return min(dxs)


def shiftcontour(p1,p2):
    if spouses(p1[-1],p2[0]): return p2[0].x-p1[-1].x
    c1l, c1r = contour_kids(p1)
    c2l, c2r = contour_kids(p2)
    return distance_contours(c1l, c1r, c2l, c2r)
#    n=min(len(c1r),len(c2l))
#    dxs = [c2l[i]-c1r[i] for i in range(0,n)]
#    return min(dxs)

    
# ppl is an array of people, for dr='r' (right), the algorithm checks if the first person encroaches on the second person,
# and if so shifts the second person, it then continues to check if first OR second person encroach on the third person, etc.
# dr='l': same but for the left
    
def shift_old(ppl,dr,mode,stoplv):
    if (len(ppl)<2): return
    if dr=='r':
        dx = shiftcontour(ppl[:1],ppl[1:])
        if(dx<1):
            shiftx(ppl[1],1-dx,mode,stoplv)
        shift(ppl[1:],dr,mode,stoplv)
    elif dr=='l':
        dx = shiftcontour(ppl[:(len(ppl)-1)],ppl[(len(ppl)-1):])
        if(dx<1):
            shiftx(ppl[-2],-(1-dx),mode,stoplv)
        shift(ppl[:len(ppl)-1],dr,mode,stoplv)
    else: print('ERROR 3',dr)


    
def shift(ppl,ix,dr,mode,stoplv):
    if (len(ppl)<2 or ix==len(ppl)): return
    if dr=='r':
        dx = shiftcontour(ppl[:ix],[ppl[ix]])
        if(dx<1):
            shiftx(ppl[ix],1-dx,mode,stoplv)
        shift(ppl,ix+1,dr,mode,stoplv)
    elif dr=='l':
        dx = shiftcontour([ppl[(len(ppl)-ix-1)]],ppl[(len(ppl)-ix):])
        if(dx<1):
            shiftx(ppl[len(ppl)-ix-1],-(1-dx),mode,stoplv)
        shift(ppl,ix+1,dr,mode,stoplv)
    else: print('ERROR 3',dr)


    
# get all people left or right of person psn
'''
def getsibsandcous(people,psn,dr):
    res = []
    for p in people:
        if (p.x is None or p.y is None or p.y!=psn.y): continue
        if (dr=='r' and p.x<=psn.x): continue
        if (dr=='l' and p.x>=psn.x): continue
        res.append(p)
    return res
'''

def getsibsandcous(psn,dr,lv=-10):
    steps = psn.y-lv
    ppl = [[] for i in range(steps+1)]
    ppl[0] += [psn]+psn.spouse
    for i in range(steps):
        for p in ppl[i]:
            if (p.dad is not None): ppl[i+1].append(p.dad)
            if (p.mom is not None): ppl[i+1].append(p.mom)

    for i in range(steps+1):
        ix = len(ppl)-1-i
        for p in ppl[ix]: ppl[ix-1] += [c for c in p.kids]
        ppl[ix-1] = list(set(ppl[ix-1]))

    sp = []
    for p in ppl[0]: sp+=p.spouse
    
    res = []
    for p in list(set(ppl[0]+sp)):
        if (p.x is None or p.y is None or p.y!=psn.y): continue
        if (dr=='r' and p.x<=psn.x): continue
        if (dr=='l' and p.x>=psn.x): continue
        res.append(p)
    return res


def shiftx(psn,dx,mode,stoplv,stoppsn=None):
    if (psn.flag==1 or psn.y is None or psn.y<=stoplv): return
    if (psn==stoppsn): return
    psn.flag=1
    psn.x += dx
    if (mode=='all' or mode=='p'):
        if (psn.dad): shiftx(psn.dad,dx,mode,stoplv,stoppsn)
        if (psn.mom): shiftx(psn.mom,dx,mode,stoplv,stoppsn)
        # also shift everyone left or right of you:
        if (dx>0): dr='r'
        else: dr = 'l'
        ppl = getsibsandcous(psn,dr,stoplv)
        for p in ppl:
            shiftx(p,dx,mode,stoplv,stoppsn)
    if (mode=='po'):
        if (psn.dad): shiftx(psn.dad,dx,mode,stoplv,stoppsn)
        if (psn.mom): shiftx(psn.mom,dx,mode,stoplv,stoppsn)
    if (mode=='all' or mode=='c'):
        for kid in psn.kids:
            shiftx(kid,dx,mode,stoplv,stoppsn)
        for sp in psn.spouse:
            shiftx(sp,dx,mode,stoplv,stoppsn)
    if (mode=='f'):
        for kid in psn.kids:
            shiftx(kid,dx,'c',stoplv,stoppsn)


def resetflags(people):
    for psn in people:
        psn.flag=0

        
        
def addkidsinlaw(people,psn,stoplv):
    sm = 0
    for kid in psn.kids:
        sm += len(kid.husb+kid.wife)
    if (sm==0): return
    if (len(psn.kids)==0): return
    allkids = [kid for kid in psn.kids]
    
    ### find left and right cousins of the kids:
    c_l = getsibsandcous(allkids[0],'l',stoplv)
    c_r = getsibsandcous(allkids[-1],'r',stoplv)

    for kid in psn.kids:
        if (len(kid.husb+kid.wife)==0): continue

        # get left and right siblings, assume they are sorted according to x coord
        sib_l = []
        sib_r = []
        for p in allkids:
            if (p == kid): continue
            if (p.x>kid.x): sib_r.append(p)
            if (p.x<kid.x): sib_l.append(p)

        if (len(kid.husb)>0):
            kid_x = kid.x                     # x-coord of kid
            kid.husb[0].y = kid.y             # kid's spouse has same level as kid
            kid.husb[0].x = kid_x-0.5         # set kid's spouse 0.5 left of kid
            kid.x += 0.5                      # shift kid 0.5 to the right (i.e. we don't have to shift their children)
            shift([kid]+sib_r,1,'r','c',stoplv)        # shift right siblings (and their children) to the right if necessary
            shift(sib_l+[kid.husb[0]],1,'l','c',stoplv)   # shift left siblings (and their children) to the left if necessary
                
            resetflags(people)
            allkids.insert(allkids.index(kid),kid.husb[0])   # add kid's spouse to allchild array

        if (len(kid.wife)>0):
            kid_x = kid.x                     # x-coord of kid
            kid.wife[0].y = kid.y
            kid.wife[0].x = kid_x+0.5         # set kids spouse 0.5 right of kid
            kid.x -= 0.5                      # shift kid 0.5 to the left (i.e. we don't have to shift their children)
            #
            shift([kid.wife[0]]+sib_r,1,'r','c',stoplv)   # shift right siblings (and their children) to the right if necessary
            shift(sib_l+[kid],1,'l','c',stoplv)           # shift left siblings (and their children) to the left if necessary

            resetflags(people)
            allkids.insert(allkids.index(kid)+1,kid.wife[0])   # add kid's spouse to allchild array
    
    ### look for encroachment
    kids_xmin = min([kid.x for kid in allkids])
    kids_xmax = max([kid.x for kid in allkids])

    if len(c_r)>0:     # do we have right cousins?
        c_r_xmin = min([p.x for p in c_r])     # x-coord of closest one
        dr = c_r_xmin-kids_xmax-1               # distance to leftmost child (boundary-boundary distance, not center-center)
    else: dr = None
    if len(c_l)>0:     # do we have left cousins?
        c_l_xmax = max([p.x for p in c_l])     # x-coord of closest one
        dl = kids_xmin-c_l_xmax-1                # distance to rightmost child (boundary-boundary distance, not center-center)
    else: dl = None
    
    if (dr is None and dl is not None and dl<0):
        # shift kids right by dl/2
        for kid in allkids:
            shiftx(kid,0.5*abs(dl),'all',stoplv)
        # shift left cousins left by dl/2
        for csn in c_l:
            shiftx(csn,-0.5*abs(dl),'all',stoplv)
    if (dl is None and dr is not None and dr<0):
        # shift kids left by dr/2
        for kid in allkids:
            shiftx(kid,-0.5*abs(dr),'all',stoplv)
        # shift right cousins right dl/2
        for csn in c_r:
            shiftx(csn,0.5*abs(dr),'all',stoplv)
    if (dl is not None and dr is not None):
        if (dl+dr>=0):     # kids fit between the cousins, i.e. only shift kids if needed
            if (dl<0):    # shift kids right by dl
                for kid in allkids:
                    shiftx(kid,abs(dl),'all',stoplv)
            if (dr<0):    # shift kids left by dr
                for kid in allkids:
                    shiftx(kid,-abs(dr),'all',stoplv)                
        else:    # overlap on left and right side, just shift cousins
            for csn in c_r:     # shift right cousins right by dr
                if (psn.name[0:4]=='Kirs'): print('DD',people[4].x,people[51].x)
                shiftx(csn,abs(dr),'all',stoplv,psn)
                if (psn.name[0:4]=='Kirs'): print('DD',people[4].x,people[51].x)
            for csn in c_l:     # shift left cousins left by dl
                shiftx(csn,-abs(dl),'all',stoplv)
    resetflags(people)

    ###
    for kid in psn.kids:
        addkidsinlaw(people,kid,stoplv)


