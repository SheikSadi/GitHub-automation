def messyfunc(x,y):
 z= [ ]
 for i in range(x):
  if i%2==0:z.append(i)
  else:
   z.append(i**2)
  for j in range(y):
     if j%3==0: z.append(j)
     else: z.append(j+i)
  if i>y:
    z.append("over")
   # comment without space
  if x>y:z.append([x,y])
 return z

class Cls:
    def __init__(self,a=3):
     self.a=a
     self.b=[ ]
    def add(self,v):
     self.b.append(v)
     for i in range(v):
         self.b.append(i)
    def __str__(self):
        return str(self.b)

def foo(bar):
 for k in range(5):
  if k==2: bar+=k
  elif k==3: bar*=k
  else:
   bar-=k
  if k>1: bar=str(bar)
 return bar

X=messyfunc(4,3)
print(X)
obj=Cls()
obj.add(2)
print(obj)
print(foo(7))
