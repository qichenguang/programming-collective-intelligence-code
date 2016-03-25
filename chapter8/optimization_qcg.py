
# coding: utf-8

# In[1]:

import time
import random
import math




# In[5]:

def getminutes(t):
    x=time.strptime(t,'%H:%M')
    return x[3]*60+x[4]





# In[6]:

def printschedule(r):
    for d in range(len(r)/2):
        name=people[d][0]
        origin=people[d][1]
        out=flights[(origin,destination)][int(r[d*2])]
        ret=flights[(destination,origin)][int(r[d*2+1])]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,
                                                      out[0],out[1],out[2],
                                                      ret[0],ret[1],ret[2])




# In[7]:

def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60

    for d in range(len(sol)/2):
        # Get the inbound and outbound flights
        origin=people[d][1]
        outbound=flights[(origin,destination)][int(sol[d*2])]
        returnf=flights[(destination,origin)][int(sol[d*2+1])]

        # Total price is the price of all outbound and return flights
        totalprice+=outbound[2]
        totalprice+=returnf[2]

        # Track the latest arrival and earliest departure
        if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
        if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])
  
    # Every person must wait at the airport until the latest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait=0  
    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound=flights[(origin,destination)][int(sol[d*2])]
        returnf=flights[(destination,origin)][int(sol[d*2+1])]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep  

    # Does this solution require an extra day of car rental? That'll be $50!
    if latestarrival>earliestdep: totalprice+=50

    return totalprice + totalwait




# In[22]:

def randomoptimize(domain,costf):
    best = 999999999
    bestr = None
    for pos in range(0,10000):
        # Create a random solution
        r = [float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]
    
        # Get the cost
        cost = costf(r)
        # Compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r 
    print 'cost:',cost
    return r




# In[29]:

def hillclimb(domain,costf):
    # Create a random solution
    sol = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
    # Main loop
    while 1:
        # Create list of neighboring solutions
        neighbors=[]
    
        for j in range(len(domain)):
            # One away in each direction
            if sol[j] > domain[j][0] and sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j]+1] + sol[j+1:])
            if sol[j] < domain[j][1] and sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j]-1] + sol[j+1:])

        # See what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # If there's no improvement, then we've reached the top
        if best == current:
            print 'cost:',best
            break
    return sol



# In[38]:

def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
    # Initialize the values randomly
    vec = [float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]
  
    while T > 0.1:
        # Choose one of the indices
        i = random.randint(0,len(domain)-1)

        # Choose a direction to change it
        dir = random.randint(-step,step)

        # Create a new list with one of the values changed
        vecb = vec[:]
        vecb[i] += dir
        
        if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1]

        # Calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e,(-eb-ea)/T)

        # Is it better, or does it make the probability
        # cutoff?
        if (eb < ea or random.random() < p):
            vec = vecb      

        # Decrease the temperature
        T = T * cool
        if T <= 0.1:
            print 'cost:',ea , eb
        
    return vec


# In[105]:

def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):
    # Mutation Operation
    def mutate(vec):
        i = random.randint(0,len(domain)-1)
        
        if 0 == int(domain[i][1]):
            return vec
        
        if random.random() < 0.5:
            if vec[i] == domain[i][0]:
                return vec[0:i] + [vec[i] + step] + vec[i+1:] 
            else:
                return vec[0:i] + [vec[i] - step] + vec[i+1:]
        else:
            if vec[i] == domain[i][1]:
                return vec[0:i] + [vec[i] - step] + vec[i+1:] 
            else:
                return vec[0:i] + [vec[i] + step] + vec[i+1:]
            
    # Crossover Operation
    def crossover(r1,r2):
        i = random.randint(1,len(domain) - 2)
        return r1[0:i] + r2[i:]

    # Build the initial population
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        pop.append(vec)
  
    # How many winners from each generation?
    topelite = int(elite * popsize)
  
    # Main loop 
    for i in range(maxiter):
        for i in range(len(pop)):
            try:
                posit = pop[i]
                if len(posit) != 12:
                    pass
                    #print posit
            except  Exception,ex:
                print 'pos i error=',i,ex
                #print pop
                
        scores = [(costf(v),v) for v in pop]
        scores.sort()
        ranked = [v for (s,v) in scores]
        #print 'len(ranked):',len(ranked)
        # Start with the pure winners
        pop = ranked[0:topelite]
        #print 'before len(pop):',len(pop)
        # Add mutated and bred forms of the winners
        while len(pop) < popsize:
            if random.random() < mutprob:
                # Mutation
                c = random.randint(0,topelite - 1)
                pop.append(mutate(ranked[c]))
            else:
                # Crossover
                c1 = random.randint(0,topelite - 1)
                c2 = random.randint(0,topelite - 1)
                pop.append(crossover(ranked[c1],ranked[c2]))
    
        #print 'len(pop):',len(pop)
        # Print current best score
        #print scores[0][0]
    
    print 'cost:',scores[0][0]
    return scores[0][1]



# ##  Drom 

# In[12]:

import random
import math


# In[18]:

def printsolution(vec):
    slots = []
    # Create two slots for each dorm
    for i in range(len(dorms)): slots += [i,i]

    # Loop over each students assignment
    for i in range(len(vec)):
        x = int(vec[i])

        # Choose the slot from the remaining ones
        dorm = dorms[slots[x]]
        # Show the student and assigned dorm
        print prefs[i][0],dorm
        # Remove this slot
        del slots[x]



# In[107]:

def dormcost(vec):
    cost=0
    # Create list a of slots
    slots=[0,0,1,1,2,2,3,3,4,4]
    #slots = []
    # Create two slots for each dorm
    #for i in range(len(dorms)): slots += [i,i]

    # Loop over each student
    #print 'vec:',vec
    for i in range(len(vec)):
        x = int(vec[i])
        try:
            dorm = dorms[slots[x]]
        except Exception,ex:
            print 'x=',x,ex
            print 'slots=',slots
        pref_dorms = prefs[i][1]
        # First choice costs 0, second choice costs 1
        if pref_dorms[0] == dorm: cost+=0
        elif pref_dorms[1] == dorm: cost+=1
        else: cost+=3
        # Not on the list costs 3

        # Remove selected slot
        del slots[x]
    return cost


# # Cross Lines

# In[141]:

import math


# In[144]:

def crosscount(v):
    # Convert the number list into a dictionary of person:(x,y)
    loc = dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))])
    total=0
  
    # Loop through every pair of links
    for i in range(len(links)):
        for j in range(i+1,len(links)):
            # Get the locations 
            (x1,y1),(x2,y2) = loc[links[i][0]],loc[links[i][1]]
            (x3,y3),(x4,y4) = loc[links[j][0]],loc[links[j][1]]

            den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)

            # den==0 if the lines are parallel
            if den == 0: continue

            # Otherwise ua and ub are the fraction of the
            # line where they cross
            ua=((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))/den
            ub=((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3))/den
      
            # If the fraction is between 0 and 1 for both lines
            # then they cross each other
            if ua > 0 and ua < 1 and ub > 0 and ub < 1:
                total+=1
                
        for i in range(len(people)):
            for j in range(i+1,len(people)):
                # Get the locations of the two nodes
                (x1,y1),(x2,y2) = loc[people[i]],loc[people[j]]

                # Find the distance between them
                dist = math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))
                # Penalize any nodes closer than 50 pixels
                if dist < 50:
                    total += (1.0-(dist/50.0))
        
    return total





# In[154]:

from PIL import Image,ImageDraw


# In[164]:

def drawnetwork(sol):
    # Create the image
    img=Image.new('RGB',(400,400),(255,255,255))
    draw=ImageDraw.Draw(img)

    # Create the position dict
    pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])

    for (a,b) in links:
        draw.line((pos[a],pos[b]),fill=(255,0,0))

    for n,p in pos.items():
        draw.text(p,n,(0,0,0))

    img.save('netword.jpg','JPEG')  
    #img.show()






