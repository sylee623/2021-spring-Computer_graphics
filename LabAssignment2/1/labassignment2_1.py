import numpy as np

#Create a 1d array M with values ranging from 2 to 26 and print M.
M = np.arange(2,26+1)
print(M) #[ 2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25]

#Reshape M as a 5x5 matrix and print M.
M = M.reshape(5,5)
print(M)

#Set the value of “inner” elements of the matrix M to 0 and print M.
M[1:4,1:4]=0
print(M)

#Assign M2 to the M and print M.
M = M@M
print(M)

#Let’s call the first row of the matrix M a vector v. Calculate the magnitude of the vector v and print it
v = M[0]
magnitude = np.sqrt(sum(v*v))
print(magnitude)
