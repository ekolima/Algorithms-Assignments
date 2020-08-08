import argparse
import random

#r=given radius/min-max: range for random radius
def get_r(r,min,max):
    radius = r
    if min is not None and max is not None:
        radius = random.randint(min,max)
    return radius

def dist(a,b): #a = [ax,ay], b = [bx,by]
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**(1/2)

def initialize(r,min,max): #first 2 circles
    g={}
    path={}
    live=[]
    g[1]=[0,0,int(get_r(r,min,max))]
    path[1]=2
    live.append(1)
    r2=get_r(r,min,max)
    g[2]=[g[1][0]+g[1][2]+r2,0,int(r2)]
    path[2]=1
    live.append(2)
    return (g,path,live)

def calc_ci(cn,cm,r): #cn=[cnx,cny,rn], cm=[cmx,cmy,rm], ri
    dx=cn[0]-cm[0]
    dy=cn[1]-cm[1]
    d=dist(cn,cm)
    r1=cm[2]+r
    r2=cn[2]+r
    l=(r1*r1-r2*r2+d*d)/(2*d*d)
    e=abs((r1*r1)/(d*d)-l*l)**(1/2)
    kx=round(cm[0]+l*dx+e*dy,2)
    ky=round(cm[1]+l*dy-e*dx,2)
    return [kx,ky,int(r)]

def find_cm(g,path,live):
    min_dist = min([round(dist(g[c][:2],[0,0]),2) for c in path if c in live])
    r = [c for c in path if c in live and round(dist(g[c][:2],[0,0]),2) == min_dist]
    return min(r)

#distance between 2 circles (start, end) in the path
def dist_path(path,start,end):
    current = start
    c = 0
    while current != end:
        current = path[current]
        c+=1
    return c

def intersect(g,path,ci,cm,cn):
    int_circles=[]
    current = path[cn]
    while current != cm:
        if round(dist(g[current],ci),2) < round((g[current][2]+ci[2]),2):
            int_circles.append(current)
        current = path[current]
    if len(int_circles) > 2:
        return [int_circles[0],int_circles[len(int_circles)-1]]
    elif len(int_circles) == 1:
        return [int_circles[0],int_circles[0]]
    else:
        return int_circles

#circles to remove from path given the start and the end circle
def to_pop(path,start,end):
    current = start
    remove = []
    while current != end:
        remove.append(current)
        current = path[current]
    return remove

def circle_line(u,v,c): #[ux,uy],[vx,vy],[cx,cy,cr]
    l2=(u[0]-v[0])**2+(u[1]-v[1])**2
    if l2 == 0:
        d=dist(u[:2],c[:2])
    else:
        t=((c[0]-u[0])*(v[0]-u[0])+(c[1]-u[1])*(v[1]-u[1]))/l2
        t = max(0,min(1,t))
        px=u[0]+t*(v[0]-u[0])
        py=u[1]+t*(v[1]-u[1])
        d=dist([px,py],c[:2])
    return round(d,2)

def check_all_boundaries(boundaries,circle):
    check = True
    for b in boundaries:
        if circle_line([b[0],b[1]],[b[2],b[3]],circle) - circle[2] < 0:
            check = False
            break
    return check

def find_previous(path,circle):
    return [i for i in path if path[i] == circle][0]

def undo(path,live,cms,to_undo):
    while len(to_undo) > 0:
        for undo in reversed(to_undo):
            if undo[0] in path:
                if undo[0] not in cms:
                    live.append(undo[1])
                path[undo[1]]=path[undo[0]]
                path[undo[0]]=undo[1]
                to_undo.remove(undo)
    return (path,live)

def place_circles(n,r,minimum,maximum,boundary):
    init=initialize(r,minimum,maximum)
    g=init[0]
    path=init[1]
    live=init[2]
    i = 2

    while live and ((n is None) or (i < n)):
        i += 1
        cms=list()
        rd=get_r(r,minimum,maximum)
        failure_boundary=True

        while failure_boundary and live:
            cm = find_cm(g,path,live)
            cn = path[cm]
            removed_step_4 = []
            failure_intersects_circle = True

            while failure_intersects_circle:
                cms.append(cm)
                ci=calc_ci(g[cm],g[cn],rd)
                t = intersect(g,path,ci,cm,cn)
                if t:
                    cnloop = dist_path(path,cn,t[0])
                    cmloop = dist_path(path,t[1],cm)
                    if cmloop<=cnloop:
                        cj = t[1]
                        cm = cj
                        to_remove = to_pop(path,path[cj],cn)
                    else:
                        cj = t[0]
                        cn = cj
                        to_remove = to_pop(path,path[cm],cj)
                    for tr in to_remove:
                        prev_tr=find_previous(path,tr)
                        removed_step_4.append([prev_tr,tr,path[tr]])
                        path[prev_tr]=path[tr]
                        if tr in live:
                            live.remove(tr)
                        path.pop(tr)
                else:
                    check = check_all_boundaries(boundary,ci)
                    if check:
                        g[i]=ci
                        path[cm]=i
                        path[i]=cn
                        live = [circle_in_path for circle_in_path in path.keys()]
                        failure_boundary = False
                    else:
                        prev_cm = find_previous(path,cm)
                        undone = undo(path,live,cms,removed_step_4)
                        path = undone[0]
                        live = undone[1]
                        cms=[]
                        live.remove(cm)
                    failure_intersects_circle = False
    return g

def write_results(circles,output_file,boundaries):
    print(len(circles))
    with open(output_file,"w") as file:
        for c in circles.values():
            file.write('{:.2f} {:.2f} {}\n'.format(c[0],c[1],c[2]))
        file.write("\n".join('{} {} {} {}'.format(b[0],b[1],b[2],b[3]) for b in boundaries))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--items", type=int, help="give number of circles to add")
    parser.add_argument("-r", "--radius", type=float, help="give radius")
    parser.add_argument("-min_radius", "--min_radius", type=float, help="give min radius between people")
    parser.add_argument("-max_radius", "--max_radius", type=float, help="give max radius between people")
    parser.add_argument("-b", "--boundary_file", help="give the boundary, in a txt file")
    parser.add_argument("-s", "--seed", type=float, help="give the seed")
    parser.add_argument("output_file", help="txt file to save results")

    args = parser.parse_args()
    if args.seed is not None: random.seed(args.seed)
    boundaries=[]
    if args.boundary_file is not None:
        with open(args.boundary_file) as boundaries_file:
            for line in boundaries_file:
                boundaries.append([float(x) for x in line.split()])

    write_results(place_circles(args.items,args.radius,args.min_radius,args.max_radius,boundaries),args.output_file,boundaries)

main()
