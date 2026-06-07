from pwn import *
import re, pulp
context.log_level = 'error'

def parse(s):
    s=s.strip().lstrip('[').rstrip(']'); d={}
    if not s.strip(): return d
    for part in s.split(','):
        k,v=part.rsplit(':',1); d[k.strip()]=int(v.strip())
    return d

r=remote('challenge.404ctf.fr',10201)
data=b''
while b'/30000]' not in data: data+=r.recv(timeout=2)
text=data.decode(errors='ignore'); print(text); lines=text.splitlines()

ol=next(l for l in lines if 'Objectif' in l)
GJ=int(re.search(r'Joules == (\d+)',ol).group(1))
MA,RA=map(int,re.search(r'Angle mod (\d+) == (\d+)',ol).groups())
MC,RC=map(int,re.search(r'Couple mod (\d+) == (\d+)',ol).groups())

RES=['Energie potentielle','Moment','Angle','Couple','Joules','Catalyseur']
state={}
for res in RES:
    for l in lines:
        m=re.match(r'\s*'+re.escape(res)+r'\s+(\d+)\s*$',l)
        if m: state[res]=int(m.group(1)); break

T={}
for l in lines:
    m=re.match(r'\s*(p\d+)\s+(\[.*\])\s*->\s*(\[.*\])',l)
    if m: T[m.group(1)]=(parse(m.group(2)),parse(m.group(3)))

def can(p,st): return all(st.get(k,0)>=v for k,v in T[p][0].items())
def app(p,st):
    st=dict(st); c,pr=T[p]
    for k,v in c.items(): st[k]-=v
    for k,v in pr.items(): st[k]=st.get(k,0)+v
    return st
def done(st): return st['Joules']==GJ and st['Angle']%MA==RA and st['Couple']%MC==RC

def solve_from(st,budget):
    prob=pulp.LpProblem("p",pulp.LpMinimize)
    nv={p:pulp.LpVariable(f"n_{p}",lowBound=0,cat='Integer') for p in T}
    def net(p,res): c,pr=T[p]; return pr.get(res,0)-c.get(res,0)
    fin={res:st[res]+pulp.lpSum(nv[p]*net(p,res) for p in T) for res in RES}
    prob+=fin['Joules']==GJ
    ka=pulp.LpVariable("ka",0,cat='Integer'); prob+=fin['Angle']==RA+MA*ka
    kc=pulp.LpVariable("kc",0,cat='Integer'); prob+=fin['Couple']==RC+MC*kc
    for res in RES: prob+=fin[res]>=0
    prob+=pulp.lpSum(nv.values())<=budget
    prob+=pulp.lpSum(nv.values())
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status]!='Optimal': return None
    return {p:int(round(nv[p].value())) for p in T}

cur=dict(state); seq=[]
while not done(cur):
    budget=30000-len(seq)
    tg=solve_from(cur,budget)
    if tg is None:
        print("ILP infaisable depuis",cur); break
    rem=dict(tg); prog_total=False
    # phase 1 : suivre les comptes ILP autant que possible
    while sum(rem.values())>0:
        progressed=False
        for p in T:
            while rem[p]>0 and can(p,cur):
                cur=app(p,cur); rem[p]-=1; seq.append(p); progressed=True; prog_total=True
        if not progressed: break
    if sum(rem.values())==0:
        continue  # devrait être done
    # phase 2 : bloqué -> tirer UNE transition activable qui produit ce qui manque
    need={}
    for p in T:
        if rem[p]>0:
            for k,v in T[p][0].items():
                if cur.get(k,0)<v: need[k]=need.get(k,0)+v-cur.get(k,0)
    best=None;bg=0
    for p in T:
        if not can(p,cur): continue
        c,pr=T[p]; g=sum(max(0,pr.get(k,0)-c.get(k,0)) for k in need)
        if g>bg: bg=g; best=p
    if best is None:
        # aucune production possible : tirer n'importe quoi d'activable pour changer l'état
        for p in T:
            if can(p,cur): best=p; break
    if best is None:
        print("Totalement bloqué:",cur); break
    cur=app(best,cur); seq.append(best)

print("done?",done(cur),"len",len(seq),"etat",cur)

# envoi par paquets
B=300
for i in range(0,len(seq),B):
    r.sendline(' '.join(seq[i:i+B]).encode())
    r.recvuntil(b']>',timeout=15)
r.sendline(b'validate')
print(r.recvall(timeout=10).decode(errors='ignore'))