a = {}
a[0] = ("test",0)
a[0] = (a.get(0)[0],a.get(0)[1]+1)
print(a.get(1))
