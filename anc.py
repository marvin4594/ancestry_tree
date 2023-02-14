from functions import *
from kidsinlaw import *
from siblings import *



def shift_simp(ppl,dr,mode,stoplv):
    if (len(ppl)<2): return
    if dr=='r':
#        dx = shiftcontour(ppl[:1],ppl[1:])
        dx = ppl[1].x-ppl[0].x
        if(dx<1):
            shiftx(ppl[1],1-dx,mode,stoplv)
        shift_simp(ppl[1:],dr,mode,stoplv)
    elif dr=='l':
#        dx = shiftcontour(ppl[:(len(ppl)-1)],ppl[(len(ppl)-1):])
        dx = ppl[(len(ppl)-1)].x-ppl[(len(ppl)-2)].x
        if(dx<1):
            shiftx(ppl[-2],-(1-dx),mode,stoplv)
        shift_simp(ppl[:len(ppl)-1],dr,mode,stoplv)
    else: print('ERROR 3',dr)



    
def get_kidsnlaw(ppl):
    kids = []; sps = []
    for psn in ppl:
        for kid in psn.kids:
            if (kid.x is not None and kid.y is not None):
                kids.append(kid)
    for kid in kids:
        for sp in kid.spouse:
            if (sp.x is not None and sp.y is not None):
                sps.append(sp)
    return list(set(kids+sps))



def set_anc_sib(people,zpsn):
    ymin = min(list(filter(None, [psn.y for psn in people])))

    anc_d = [[] for i in range(abs(ymin))]
    anc_m = [[] for i in range(abs(ymin))]


    def getanc(psn,arr):
        arr[psn.y].append(psn)
        if psn.dad is not None: getanc(psn.dad,arr)
        if psn.mom is not None: getanc(psn.mom,arr)

    getanc(zpsn.dad,anc_d)
    getanc(zpsn.mom,anc_m)
    # they are already sorted

    set_anc_sib_half(people,anc_d,'l')
    set_anc_sib_half(people,anc_m,'r')



def set_anc_sib_half(people,anc_arr,dr):

    for i in range(1,len(anc_arr)+1):
       
        ancs = anc_arr[-i]
        if (len(ancs)==0): continue
        if (dr=='r'): outer_anc = ancs[-1]
        elif (dr=='l'): outer_anc = ancs[0]
        
        ancs4 = [a for a in ancs]
        if (dr=='l'): ancs4 = list(reversed(ancs4))
        
        for anc in ancs4:
            sl, sml, smr, sr = getsiblings(anc)
            if (anc.sex=='M'): sibs = sl+sr+sml+smr
            elif (anc.sex=='F'): sibs = sml+smr+sl+sr

            ### insert 2nd spouse
            sp2 = None
            if (len(anc.spouse)==2):
                for s in anc.spouse:
                    if (s.x is None): sp2 = s
            if sp2 is not None:
                if (anc.sex=='M'): sibs += [sp2]
                elif (anc.sex=='F'): sibs = [sp2]+sibs
                if (sp2.sex=='M'): sp2.x = anc.x+1
                elif (sp2.sex=='F'): sp2.x = anc.x-1

            ###
            if (len(sibs)==0): continue
            for sib in sibs:
                sib.x = anc.x
                sib.y = anc.y
            
            k = ancs.index(anc)
            if anc.sex=='M': ancs2 = ancs[0:k]+sibs+ancs[k:]
            elif anc.sex=='F': ancs2 = ancs[0:k+1]+sibs+ancs[k+1:]
            shift_simp(ancs2,dr,'p',-100)     # shift 
            resetflags(people)
            
            
            # go through siblings again and place their families
            sibs4 = sibs
            if (dr=='l'): sibs4 = list(reversed(sibs4))
            
            
            for sib in sibs4:

                if (len(sib.spouse)==0 and len(sib.kids)==0): continue
                if (sib==sp2): continue

                dx = 0
                if (len(sib.spouse)==1):
                    if (sib.sex=='M' and dr=='l'): dx = -1
                    elif (sib.sex=='F' and dr=='r'): dx = 1
                elif (len(sib.spouse)==2): dx = 1
                    
                k = ancs2.index(sib)


                set_desc_spouse(people,sib,x=sib.x+dx,y=sib.y)
                #continue
                
                if (dr=='r'):
                    if (k > ancs2.index(outer_anc)):
                        dx = shiftcontour(ancs2[:k],[sib])
                        if(dx<1): shiftx(sib,(1-dx),'c',-100)
                        shift_simp(ancs2[k:],dr,'x',-100)
                        resetflags(people)
                    else:
                        k1 = get_kidsnlaw(ancs2[:k]+ancs2[k+1:])
                        c1l, c1r = contour_kids(k1)
                        k2 = get_kidsnlaw([sib])
                        if not (len(k1)==0 or len(k2)==0):
                            ##
                            #if spouses(p1[-1],p2[0]): return p2[0].x-p1[-1].x
                            c2l, c2r = contour_kids(k2)
                            dx = distance_contours(c1l, c1r, c2l, c2r)
                            ## dx = shiftcontour(k1,k2)
                            if(dx<1):
                                for kid in sib.kids:
                                    shiftx(kid,1-dx,'c',-100)
                elif (dr=='l'):
                    if (k < ancs2.index(outer_anc)):     # we are left of all the ancestors, so we can shift sib as well
                        dx = shiftcontour([sib],ancs2[k+1:])
                        if(dx<1): shiftx(sib,-(1-dx),'c',-100)
                        shift_simp(ancs2[:k+1],dr,'x',-100)
                        resetflags(people)
                    else:     # there are ancestors left of sib, so don't shift sib, only kids
                        k1 = get_kidsnlaw(ancs2[:k]+ancs2[k+1:])
                        c1l, c1r = contour_kids(k1)
                        k2 = get_kidsnlaw([sib])
                        if not (len(k1)==0 or len(k2)==0):
                            ##
                            #if spouses(p1[-1],p2[0]): return p2[0].x-p1[-1].x
                            c2l, c2r = contour_kids(k2)
                            dx = distance_contours(c1l, c1r, c2l, c2r)
                            #dx = shiftcontour(k1,k2)
                            if(dx<1):
                                for kid in sib.kids:
                                    shiftx(kid,-(1-dx),'c',-100)
                            
                k = ancs2.index(sib)
                # insert spouse into ancs2 array:
                if (len(sib.spouse)==2):
                    ancs2.insert(k+1,sib.spouse[1])
                    ancs2.insert(k,sib.spouse[0])
                elif (len(sib.spouse)==1):
                    if (sib.sex=='F'): ancs2.insert(k,sib.spouse[0])
                    elif (sib.sex=='M'): ancs2.insert(k+1,sib.spouse[0])

                if (dr=='r'):
                    shift_simp(ancs2[k:],dr,'x',-100)
                elif(dr=='l'):
                    shift_simp(ancs2[:k+1],dr,'x',-100)
                resetflags(people)    

