# lst = []
# for i in range(1,11):
#     lst.append(i)
# print(lst)
# how take the input from the user 
# lst =[ float(i) for i in input("Enter the number & sep by comma:").split(',')]
# print(lst)

# METHOD -1 : for loop

# lst = [i for i in range(1,10)]
# print(lst)

# MEthod - 2 : for loop if condition 
# for i in range(1,10):
#     if (i%2==0):
#         print('even')
#     else:
#         print('odd')

# l1 = [ f'even:{i}'  for i in range (1,10) if i % 2 == 0]
# print(l1)


# Method - 3: for loop if - else condition
# l1 = [ f'Even:{i}' if i % 2 ==0 else f'Odd:{i}' for i in range(25,50)]
# print(l1)

#Method-4 : for loop if-elif-else:

# lst = [<if output> <if cond> else <elif output> <if cond> else <else output> <for loop>]

sum = 0
# for i in range(1,11):
#     sum = sum + i
# print(sum)

lst = [sum := sum + i for i in range(1,11)]
print(sum)

