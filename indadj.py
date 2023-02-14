
def shiftsib(psn,ix):
    for par in [psn.dad,psn.mom]:
        if par is None: continue
        i = par.kids.index(psn)
        if (ix<0):
            par.kids.insert(i+ix,psn)
            par.kids.pop(i+1)
        if (ix>0):
            par.kids.insert(i+ix+1,psn)
            par.kids.pop(i)

def shift_tree(people,psn,dx,dh,dv):
    x = psn.x
    y = psn.y
    for p in people:
        if (p.x is None or p.y is None): continue
        if (dv=='u' and p.y>y): continue
        if (dv=='d' and p.y<y): continue
        if (dv=='r' and p.y!=y): continue
        if (dh=='r' and p.x<x): continue
        if (dh=='l' and p.x>x): continue
        p.x += dx


def pre_indaji(people,zpsn):
    shiftsib(people[13],-3)
    shiftsib(people[94],+5)
    if (zpsn.ix==2):
        shiftsib(people[65],-1)     # Wilhelm Robien
        shiftsib(people[66],-2)     # Heinz Robien





    
def post_indaji(people,zpsn):
    if (zpsn.ix==1):
        people[21].x += 2.0
        people[26].x -= 3.25
        shift_tree(people,people[107],0.5,'l','u')     # Soenke Blank
        shift_tree(people,people[111],0.5,'l','u')     # Lisa Onken
        shift_tree(people,people[13],0.5,'l','u')      # Herta B Blank
        people[171].x += 0.5
        people[172].x += 0.5

    if (zpsn.ix==2):
        shift_tree(people,people[88],+1,'l','u')   # Catharina Schnack
        shift_tree(people,people[45],+2,'l','u')   # Edith Robien
        shift_tree(people,people[88],-5,'l','u')   # Catharina Schnack

        people[94].x -= 3      # Hans Albrecht
        people[126].x -= 3     # Hertha Jebe
        people[122].x -= 4.5   # Otto Bock
        people[124].x -= 4.5   # Mathilde Bock
        people[125].x -= 4.5   # Georg Kuellmer
        
        shift_tree(people,people[120],-4,'l','u')   # Anna A B Albrecht
        shift_tree(people,people[69],-0.5,'l','d')  # Baerbel Jansen
        people[67].x -= 1     # Otto Jansen
        people[63].x -= 1     # Wilma Robien
        people[66].x -= 1     # Heinz Albrecht

        shift_tree(people,people[78],+1,'r','d')   # Baerbel Haltenhof
        shift_tree(people,people[72],-1,'r','d')   # Haltenhof
        shift_tree(people,people[65],-1,'r','d')   # Wilhelm Robien

        shift_tree(people,people[134],-0.5,'r','d')   # Wilhelm Robien
        people[130].x -= 0.5     # Michael Albrecht
        people[186].x -= 0.5     # Sebastian Albrecht

        people[82].x += 1.5     # Anna Marie Robien
        people[46].x -= 1.5     # Adalbert Schwandt
        people[47].x -= 1.5     # Herta Krueger
        people[52].x += 2       # Adorf Schwandt
        people[53].x += 2       # Ida

        people[87].x += 1     # Peter Soerensen
        people[88].x += 1     # Catharina Schnack
        shift_tree(people,people[142],8,'l','u')     # Anna Elisabeth Feige

        shift_tree(people,people[178],-1,'l','u')     # Catharina Muellerin
        people[140].x -= 0.5     # Johann Hupfeld
        people[141].x -= 0.5     # Anna Brill
        
        people[191].x += 5     # Hinrich Schnack
        people[192].x += 5     # Christina Heuster

        people[120].x -= 20.5   # Anna A B Albrecht
        people[121].x -= 20.5   # Karl Bock
        people[122].x -= 20.0   # Otto Bock
        people[124].x -= 20.0   # Mathilde Bock
        people[125].x -= 20.0   # Georg Kuellmer

        shift_tree(people,people[49],-0.5,'l','d')  # Martina Schwandt
        shift_tree(people,people[67],-0.5,'r','d')  # Otto Jansen
        people[1].x += 0.5     
        people[2].x += 0.5     

        people[132].x -= 0.5     
        people[133].x -= 0.5     
        people[134].x -= 0.5     







    if (zpsn.ix==45):
        shift_tree(people,people[88],-4,'l','u')   # Catharina Schnack

        shift_tree(people,people[120],-7.5,'l','u')   # Anna A B Albrecht
        people[122].x -= 7.5     # Otto Bock
        people[124].x -= 7.5     # Mathilde Bock
        people[125].x -= 7.5     # Georg Kuellmer

        shift_tree(people,people[142],6.5,'l','u')     # Anna Elisabeth Feige
        people[142].x -= 8     # Anna Elisabeth Feige
        people[143].x -= 8     # Catharina

        people[82].x += 2      # Anna Marie Robien





        '''
        people[115].x += 3
        people[116].x += 3

        people[85].x -= 2
        people[86].x -= 2
        people[144].x -= 2

        shift_tree(people,people[142],6.5,'l','u')     # Anna Elisabeth Feige
        shift_tree(people,people[142],2,'r','u')   # Anna Elisabeth Feige
        shift_tree(people,people[125],-0.5,'r','d')  # Georg Kuellmer
        people[82].x += 1.5
        shift_tree(people,people[150],1,'r','u')     # Johann C Albrecht
        shift_tree(people,people[82],-6.5,'r','u')     # Johann C Albrecht
        shift_tree(people,people[125],-6.5,'r','d')     # Johann C Albrecht

        shift_tree(people,people[131],2,'l','d')
        shift_tree(people,people[130],-0.5,'r','d')
        shift_tree(people,people[134],1,'r','d')

        shift_tree(people,people[49],-1.5,'l','d')
        shift_tree(people,people[45],3.5,'l','d')
        shift_tree(people,people[2],1,'l','r')
        shift_tree(people,people[63],1.5,'l','r')
        shift_tree(people,people[74],-0.5,'l','r')
        people[78].x += 4
        shift_tree(people,people[69],1,'l','d')
        people[71].x += 0.5
        people[65].x -= 0.5
        '''

