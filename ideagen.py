import random
import io
with io.open("industries.txt",'r',encoding='utf8') as f:
    i_file = f.read()
n_file = open("nounlist.txt", "r")
industries = i_file.split('\n')
nouns = n_file.read().split('\n')
for i in range (1, 100):
    i_random = random.choice (industries)
    n_random = random.choice (nouns)
    print (i_random + ", but for " + n_random)
    

