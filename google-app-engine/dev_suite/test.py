a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
a = [sum(x)/len(x) for x in zip(*a)]
print(a)
