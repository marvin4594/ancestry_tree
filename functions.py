from ged4py.parser import GedcomReader
import cairocffi as cairo
from billtrees import *
from kidsinlaw import *
import glob
import math

def nextx(x):
    if (x>0): return math.ceil(2*x)/2
    if (x<=0): return math.floor(2*x)/2


def shifttree(psn):
    #if psn is None: return
    
    if (psn.dad is not None and psn.mom is not None):
        xm = nextx(0.5*(psn.dad.x+psn.mom.x))
        psn.dad.x = xm-0.5
        psn.mom.x = xm+0.5
        shifttree(psn.dad)
        shifttree(psn.mom)
    else:
        for p in [psn.dad]+[psn.mom]:
            if p is None: continue
            p.x = nextx(p.x)
            shifttree(p)


class Person:
    def __init__(self, name, ix, indi):
        self.name = name
        self.givn = None
        self.surn = None
        self.ix = ix
        self.indi = indi
        self.sex = None
        self.dob = None
        self.yob = None
        self.pob = None
        self.dod = None
        self.yod = None
        self.pod = None
        self.x = None
        self.y = None
        self.dad = None
        self.mom = None
        self.husb = []
        self.wife = []
        self.spouse = []
        self.kids = []
        self.flag = 0
        self.pic = None

        

def gcom_to_year(gdate):
    yr = str(gdate).split(' ')[-1]
    if (yr[-1] == ')'): yr = yr[:-1]
    if not yr.isdigit(): yr = None
    return yr



def add_person(people,indi):
    ix = len(people)
    psn = Person(indi.name.format(),ix,indi)
    psn.givn = indi.sub_tag_value("NAME/GIVN")
    psn.surn = indi.sub_tag_value("NAME/SURN")
    psn.sex = indi.sub_tag_value("SEX")
    psn.dob = indi.sub_tag_value("BIRT/DATE")
    psn.pob = indi.sub_tag_value("BIRT/PLAC")
    psn.dod = indi.sub_tag_value("DEAT/DATE")
    psn.pod = indi.sub_tag_value("DEAT/PLAC")
    psn.yob = gcom_to_year(psn.dob)
    psn.yod = gcom_to_year(psn.dod)
    people.append(psn)

    

def set_picfiles(people):
    
    files = glob.glob('../Portraits/*')

    for i in range(len(files)):
        files[i] = files[i].replace('a'+'̈','ä').replace('o'+'̈','ö').replace('u'+'̈','ü')
    
    for fle in files:
        
        fl = fle[13:-4].split('_')
        
        if (len(fl)>2 and fl[-2]=='geb'): fl = fl[:-3]+fl[-1:]
        
        if (fl[0].isdigit()):
            yob = fl[0]
            givn = fl[1]
        else:
            yob = None
            givn = fl[0]
            
        if (len(fl)>1): surn = fl[-1]
        else: surn = None
    
        f = False
        
        for psn in people:
            c1 = (yob is None or psn.yob==yob)
            c2 = (givn is None or givn==str(psn.givn).split(' ')[0])
            c3 = (surn is None or surn==str(psn.surn))

            if (c1 and c2 and c3):
                psn.pic = fle
                f = True
                break
            
        if not f: print('Person NOT FOUND',fle)
        
        

def get_people(fname):
    parser=GedcomReader(fname)
    people = []

    for indi in parser.records0("INDI"):
        add_person(people,indi)

    for psn in people:
        indi=psn.indi
        if (indi.father):
            for psn2 in people:
                if(psn2.indi.xref_id==indi.father.xref_id): psn.dad = psn2
        if (indi.mother):
            for psn2 in people:
                if(psn2.indi.xref_id==indi.mother.xref_id): psn.mom = psn2

    for i, fam in enumerate(parser.records0("FAM")): 
        husb_, wife_ = fam.sub_tag('HUSB'), fam.sub_tag('WIFE')
        if husb_: 
            for psn in people:
                if(psn.indi.xref_id==husb_.xref_id): husb = psn
        if wife_: 
            for psn in people:
                if(psn.indi.xref_id==wife_.xref_id): wife = psn

        if (husb_ and wife_):
            husb.wife.append(wife)
            wife.husb.append(husb)
            husb.spouse.append(wife)
            wife.spouse.append(husb)

        children = fam.sub_tags("CHIL")
        kids = []
        for child in children: 
            for psn in people:
                if(psn.indi.xref_id==child.xref_id): kids.append(psn)

        if husb_: husb.kids+=kids
        if wife_: wife.kids+=kids

    return people



def plot_person(ctx,psn,box_x,box_y,box_y_small,line_width,font_size):

    if (psn.pic is None): box_y = box_y_small

    crd_x = psn.x-0.5*box_x
    crd_y = psn.y-0.5*box_y

    # draw box
    ctx.move_to(crd_x, crd_y)
    ctx.line_to(crd_x, crd_y+box_y)
    ctx.line_to(crd_x+box_x, crd_y+box_y)
    ctx.line_to(crd_x+box_x, crd_y)
    ctx.line_to(crd_x-0.5*line_width, crd_y)
    
    # draw line below picture
    if (psn.pic is not None): 
        ctx.move_to(crd_x, crd_y + box_x)
        ctx.line_to(crd_x + box_x, crd_y + box_x)

    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.stroke()

    
    ##### draw picture
    
    if psn.pic is not None:
        ims = cairo.ImageSurface.create_from_png(psn.pic)
        imh = ims.get_height()
        imw = ims.get_width()

        ctx.save()
        ctx.translate(crd_x+0.5*line_width,crd_y+0.5*line_width)

        sc = min((box_x-line_width)/imw, (box_y-line_width)/imh)

        ctx.scale(sc,sc)
        ctx.set_source_surface(ims)
        ctx.paint()
        ctx.restore()
        
        
    ##### Text

    ctx.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)

    if (psn.pic is None): fac=0
    else: fac=1
    
    if psn.givn is not None:
        name = psn.givn.split(' ')
        givn = name[0]
        for i in range(1,len(name)):
            let = name[i][0]
            if let=='"': let = name[i][1]
            givn += ' '+let+'.'
        (x, y, width, height, dx, dy) = ctx.text_extents(givn)
        ctx.move_to(crd_x+0.5*(box_x-width),crd_y + fac*box_x + font_size)
        ctx.show_text(givn)
    if psn.surn is not None:
        name2 = psn.surn
        (x, y, width, height, dx, dy) = ctx.text_extents(name2)
        ctx.move_to(crd_x+0.5*(box_x-width),crd_y + fac*box_x + 2*font_size)
        ctx.show_text(name2)
        
    if (False):
        if psn.yob is not None:
            born = '*'+psn.yob
            if psn.pob is not None: born+=' '+psn.pob.split(',')[0].split(' ')[0]
            (x, y, width, height, dx, dy) = ctx.text_extents(born)
            ctx.move_to(crd_x+0.5*(box_x-width),crd_y + fac*box_x + 3*font_size)
            ctx.show_text(born)
        if psn.yod is not None:
            died = '\u2020'+psn.yod
            if psn.pod is not None: died+=' '+psn.pod.split(',')[0].split(' ')[0]
            (x, y, width, height, dx, dy) = ctx.text_extents(died)
            ctx.move_to(crd_x+0.5*(box_x-width),crd_y + fac*box_x + 4*font_size)
            ctx.show_text(died)
    elif (True):
        dates = ''
        if psn.yob is not None:
            dates += '*'+psn.yob
        if psn.yod is not None:
            dates += ' \u2020'+psn.yod
        if (len(dates)>0):
            (x, y, width, height, dx, dy) = ctx.text_extents(dates)
            ctx.move_to(crd_x+0.5*(box_x-width),crd_y + fac*box_x + 3*font_size)
            ctx.show_text(dates)

        
    ##### End Text



# get a subtree from person psn: 'c': only children, 'p': only parents
def subTree(psn,d):
    if (d=='c'):
        c_trees = [subTree(kid,d) for kid in psn.kids]
    elif (d=='p'):
        c_trees = []
        if (psn.dad): c_trees.append(subTree(psn.dad,d))
        if (psn.mom): c_trees.append(subTree(psn.mom,d))
    else: print('ERROR')
    return Tree(str(psn.ix),*c_trees)


# x,y: desired position of zeroperson
def setxyfromDtree(people,dtree,x=0,y=0,f=1):
    dx = x - dtree.x
    dy = y - dtree.y
    setxyfromDtree_sub(people,dtree,dx,dy,f)

# dx,dy: shift all people in dtree by these values
def setxyfromDtree_sub(people,dtree,dx,dy,f):
    people[int(dtree.tree.node)].x = dtree.x + dx
    people[int(dtree.tree.node)].y = f*(dtree.y + dy)
    for i in range(len(dtree.children)):
        setxyfromDtree_sub(people,dtree.children[i],dx,dy,f)

        
        
        
def realign(people,box_x,box_y,box_y_small,margin_y,minpiclevel,minlvlpic,maxlvlpic):
    
    # border margins:
    bmarg_x = 0.5*box_x
    if minlvlpic is not None:
        bmarg_up = 0.5*box_y
    else:
        bmarg_up = 0.5*box_y_small
    if maxlvlpic is not None:
        bmarg_do = 0.5*box_y
    else:
        bmarg_do = 0.5*box_y_small

    bmarg_x += 0.5*box_x
    bmarg_up += 0.5*box_x
    bmarg_do += 0.5*box_x

    # ###
    dist1 = box_y + margin_y
    dist2 = box_y_small + margin_y
    
#    for psn in people:
#        if (psn.y is not None): psn.y = (psn.y - minpiclevel)*stretch1

    for psn in people:
        if psn.y is None: continue
        if psn.y > minpiclevel: psn.y = minpiclevel + (psn.y - minpiclevel)*dist1
        elif (minpiclevel > psn.y): psn.y = minpiclevel - ((minpiclevel - psn.y)*dist2 + 0.5*(box_y - box_y_small))
        
    x_all = list(filter(None, [psn.x for psn in people]))
    y_all = list(filter(None, [psn.y for psn in people]))
    x1 = min(x_all)
    x2 = max(x_all)
    y1 = min(y_all)
    y2 = max(y_all)
    
    for psn in people:
        if (psn.x is not None): psn.x = psn.x - x1 + bmarg_x
        if (psn.y is not None): psn.y = psn.y - y1 + bmarg_up

    Dx = (x2-x1)+2*bmarg_x
    Dy = (y2-y1)+(bmarg_up+bmarg_do)
    
    # adjust to din norm
    sq2 = 1.414213562373095
    if (Dx < sq2*Dy):     #make image wider
        delx = sq2*Dy - Dx
        for psn in people:
            if psn.x is not None: psn.x += delx/2
        Dx = sq2*Dy
    elif (Dx > sq2*Dy):     #make image higher
        dely = Dx/sq2 - Dy
        for psn in people:
            if psn.y is not None: psn.y += dely/2
        Dy = Dx/sq2

    return Dx, Dy



def plottree(people,zpsn,Dx,Dy,ppmm,box_x,box_y,box_y_small,line_width,font_size,outp):
    
    ### calc resolution
    lx = 1189
    ly = 841

    mm_p_unit = 0.5*(lx/Dx + ly/Dy)

    res_x = ppmm * mm_p_unit
    res_y = ppmm * mm_p_unit

    if (outp == 'pdf'):
        surface = cairo.PDFSurface("tree.pdf", Dx*res_x, Dy*res_y)
    elif (outp == 'png'):
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24,int(Dx*res_x),int(Dy*res_y))
        
    ctx = cairo.Context(surface)
    
    ctx.scale(res_x, res_y)
   
    ctx.rectangle(0,0,Dx,Dy)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    for psn in people:
        if (psn.x): plot_person(ctx,psn,box_x,box_y,box_y_small,line_width,font_size)
    

    plot_famlist(ctx,people,box_x,box_y,box_y_small,line_width)

    
    
    #####
    nodes = []

    if (zpsn.ix == 2):
        nodes.append([10.8,9.6824134])

    node_l = 0.1
    
    for node in nodes:
        x = node[0]
        y = node[1]
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(x-0.5*node_l, y-0.5*node_l, node_l, node_l)
        ctx.fill()

        ctx.arc(x, y, 0.5*(node_l + line_width), math.pi, 0)

        ctx.move_to(x, y-0.5*node_l)
        ctx.line_to(x, y+0.5*node_l)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width)
        ctx.stroke()    
    #####

    
    
    if (outp == 'pdf'):
        ctx.show_page() 
    elif (outp == 'png'):
        surface.write_to_png('tree.png')
    
    
    

def correct(dtree):
    if (len(dtree.children)==2):
        dx = 0.5*(abs(dtree.children[1].x-dtree.children[0].x) -1)
        if (dtree.children[1].x > dtree.children[0].x):
            dtree.children[1].x -= dx
            dtree.children[0].x += dx
        else:
            dtree.children[0].x -= dx
            dtree.children[1].x += dx
#    elif (len(dtree.children)==1):
#        dtree.children[0].x = dtree.x
    for ch in dtree.children:
        correct(ch)


        
# x,y: desired position of zeroperson
def set_desc_spouse(people,psn,x=0,y=0,spouse=True):
    mytree = subTree(psn,'c')
    dtree = buchheim(mytree)

    if (spouse and len(psn.spouse)==1):
        if (psn.sex=='M'): dtree.x -= 0.5
        elif (psn.sex=='F'): dtree.x += 0.5
 
    setxyfromDtree(people,dtree,x,y)
    
    if (spouse):
        for sp in psn.spouse:
            sp.y = psn.y
        if (len(psn.spouse)==2):
            psn.spouse[0].x = psn.x-1
            psn.spouse[1].x = psn.x+1
        elif (len(psn.spouse)==1):
            if (psn.sex=='M'): psn.spouse[0].x = psn.x+1
            elif (psn.sex=='F'): psn.spouse[0].x = psn.x-1
            else: print('ERROR 65',psn.sex)  
    
    addkidsinlaw(people,psn,psn.y)



'''    
def set_descendents(people,psn):
    mytree = subTree(psn,'c')
    dtree = buchheim(mytree)
    setxyfromDtree(people,dtree)
    
    for sp in psn.spouse:
        sp.y = psn.y
    if (len(psn.spouse)==2):
        psn.spouse[0].x = psn.x-1
        psn.spouse[1].x = psn.x+1
    elif (len(psn.spouse)==1):
        if (psn.sex=='M'): dx = +1
        elif (psn.sex=='F'): dx = -1
        else: print('ERROR 65',psn.sex)  
        for p in people:
            if (p.x is not None): p.x += 0.5*dx
        psn.x=0
        psn.spouse[0].x = psn.x+dx        

    addkidsinlaw(people,psn,psn.y)
'''


    
def set_ancestors(people,psn,x=0,y=0):
    mytree = subTree(psn,'p')
    dtree = buchheim(mytree)
    #correct(dtree)
    setxyfromDtree(people,dtree,x,y,-1)
    shifttree(psn)


def get_famlist(people,box_y,box_y_small):
    
    famlist = []
    
    for psn in people:
        if (psn.x is None or psn.y is None): continue
        psn.flag = 1
        for sp in psn.spouse:
            if (sp.x is None or sp.y is None): continue
            if sp.flag == 1: continue
            kls = []
            sp.flag = 1
            for kid in psn.kids:
                if (kid.x is None or kid.y is None): continue
                if (kid in sp.kids): kls.append(kid)
            famlist.append([[psn,sp],kls])
        kls = []
        for kid in psn.kids:
            if (kid.x is None or kid.y is None): continue
            bla = False
            for sp in psn.spouse:
                if (sp.x is None or sp.y is None): continue
                if kid in sp.kids: bla = True
            if (bla): continue
            kls.append(kid)
        if (len(kls)>0): famlist.append([[psn],kls])

    resetflags(people)
 
    for i in range(len(famlist)):
        #print([l.name for l in ls[0]],[l.name for l in ls[1]])
        if (len(famlist[i][1])==0): continue
        xs = [k.x for k in famlist[i][1]]
        if (len(famlist[i][0])==2):
            xs.append(0.5*(famlist[i][0][0].x+famlist[i][0][1].x))
        elif (len(famlist[i][0])==1):
            xs.append(famlist[i][0][0].x)
        xmin = min(xs)
        xmax = max(xs)
        # calc y-pos
        if (famlist[i][0][0].pic is None):
            dy_par = 0.5*box_y_small
        else: dy_par = 0.5*box_y
        if (famlist[i][1][0].pic is None):
            dy_kid = 0.5*box_y_small
        else: dy_kid = 0.5*box_y
        y = 0.5*((famlist[i][0][0].y + dy_par) + (famlist[i][1][0].y - dy_kid))       
#        y = 0.5*(famlist[i][0][0].y + famlist[i][1][0].y)    #famlist[i][1][0].y-0.5
#        print(i,famlist[i][0][0].name,xmin,xmax,y)
        famlist[i] += [xmin,xmax,y]
#        print(famlist[i][2:5])
    
    for i in range(len(famlist)):
        if (len(famlist[i][1])==0): continue
        xmin1 = famlist[i][2]
        xmax1 = famlist[i][3]
#        if (xmin1==xmax1): continue
        y = famlist[i][4]
        for j in range(i+1,len(famlist)):
            if (len(famlist[j][1])==0): continue
            if (y != famlist[j][4]): continue
            xmin2 = famlist[j][2]
            xmax2 = famlist[j][3]
#            if (xmin2==xmax2): continue
#            print('O',famlist[i][0][0].name,famlist[j][0][0].name,xmin1,xmax1,xmin2,xmax2)
            if (xmax1>=xmin2 and xmin1<=xmax2):     # overlap
                xpar1 = sum([psn.x for psn in famlist[i][0]])/len(famlist[i][0])
                xkid1 = sum([psn.x for psn in famlist[i][1]])/len(famlist[i][0])
                xpar2 = sum([psn.x for psn in famlist[j][0]])/len(famlist[j][0])
                xkid2 = sum([psn.x for psn in famlist[j][1]])/len(famlist[j][0])
                if (xpar1 < xpar2 and xkid1 < xkid2):
                    famlist[i][4] -= 0.1
                    famlist[j][4] += 0.1
                else:
                    famlist[i][4] += 0.1
                    famlist[j][4] -= 0.1
                #print('H',i,j,xmin1,xmax1,xmin2,xmax2, '---', xpar1,xkid1,xpar2,xkid2)
                #if (xmin2>xmin1 and xmax2<xmax1):
                #    famlist[i][4] -= 0.05
                #    famlist[j][4] += 0.05
                #else: 


    return famlist



def plot_famlist(ctx,people, box_x, box_y, box_y_small, line_width):

    famlist = get_famlist(people,box_y,box_y_small)
    
    for fam in famlist:
        pa = fam[0]
        kds = fam[1]

        # draw line connecting spouses:
        if (len(pa)==2):
            if (pa[0].x<pa[1].x):
                ctx.move_to(pa[0].x+0.5*box_x, pa[0].y)
                ctx.line_to(pa[1].x-0.5*box_x, pa[1].y)
            else:
                ctx.move_to(pa[1].x+0.5*box_x, pa[1].y)
                ctx.line_to(pa[0].x-0.5*box_x, pa[0].y)
                
        if (len(kds)==0): continue
        
        x1 = fam[2]
        x2 = fam[3]
        y = fam[4]

        if (len(pa)==2):
            ctx.move_to(0.5*(pa[0].x+pa[1].x), pa[0].y)
            ctx.line_to(0.5*(pa[0].x+pa[1].x), y)
        elif (len(pa)==1):     # single parents line
            if (pa[0].pic is None):
                ctx.move_to(pa[0].x, pa[0].y+0.5*box_y_small)
            else:
                ctx.move_to(pa[0].x, pa[0].y+0.5*box_y)
            ctx.line_to(pa[0].x, y)
        # kid lines:
        for kd in kds:
            if kd.pic is None:
                ctx.move_to(kd.x,kd.y-0.5*box_y_small)
            else:
                ctx.move_to(kd.x,kd.y-0.5*box_y)

            ctx.line_to(kd.x,y)            
            
        # connect siblings:
        ctx.move_to(x1, y)
        ctx.line_to(x2, y)

    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.stroke()

        


def get_mypeople(zpsn):

    def get_anc(psn):
        ppl = [psn]
        if psn.dad is not None: ppl += get_anc(psn.dad)
        if psn.mom is not None: ppl += get_anc(psn.mom)
        return ppl

    def get_desc(psn):
        ppl = [psn]
        for sp in psn.spouse: ppl += [sp]
        for kid in psn.kids: ppl += get_desc(kid)
        return ppl
  
    anc = get_anc(zpsn)
    mypeople = []
    for psn in anc:
        mypeople += get_desc(psn)

    return(list(set(mypeople)))


def piclevels(people):
    
    minpiclevel = None     # lowest level that has pictures
    minlvlpic = None       # has the lowest level pictures?
    maxlvlpic = None       # has the highest level pictures?

    minlvl = None          # lowest level of all people
    maxlvl = None          # highest level of all people

    for psn in people:
        if psn.y is None: continue
    
        if psn.pic is not None:
            # set minpiclevel to person's y-coord if person has picture and y-coord is smallest
            if minpiclevel is None: minpiclevel = psn.y
            else: minpiclevel = min(minpiclevel,psn.y)
            
        # set lowest and highest level
        if (minlvl is None or psn.y < minlvl): minlvl = psn.y
        if (maxlvl is None or psn.y > maxlvl): maxlvl = psn.y

    # set minlvlpic and maxlvlpic to 'YES' if lowest or highest level has picture
    for psn in people:
        if psn.y is not None and psn.y == minlvl and minlvlpic is None and psn.pic is not None:
            minlvlpic = 'YES'
        if psn.y is not None and psn.y == maxlvl and maxlvlpic is None and psn.pic is not None:
            maxlvlpic = 'YES'

    for psn in people:
        if (psn.pic is None and psn.y is not None and psn.y >= minpiclevel):
            if (psn.sex == 'M'): psn.pic = '../default_m.png'
            if (psn.sex == 'F'): psn.pic = '../default_f.png'
        
    return minpiclevel,minlvlpic,maxlvlpic

