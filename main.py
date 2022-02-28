import numpy as np
from itertools import combinations
from itertools import chain

import time

order = ['Book', 'Watch', 'Shirt', 'Jeans', 'Charger', 'Jacket', 'Headphone', 'Knife', 'Perfume', 'Cap', 'Laptop',
         'Shoes', 'Smartwatch', 'Purfume', 'Mask', 'Smartphone', 'Rings', 'Bottle', 'Cable', 'Curtains', 'Bag', 'Table',
         'Chair', 'Plates', 'Tent', 'Bulb', 'Pan', 'Bowl', 'Cooker', 'Bicycle', 'Scooter']


def load_transaction(filecode, order):
    transactions = []
    with open(filecode) as file:
        for lines in file:
            item_list = list(lines.strip().split(','))
            item_uniq = list(np.unique(item_list))
            item_uniq.sort(key=lambda x: order.index(x))
            transactions.append(item_uniq)
    return transactions


print(
    "Please choose the dataSet you want: \n 1. Amazon Store \n 2. D-mart \n 3. Instacart \n 4. Walmart \n 5. Cosco \n \n\n")
while True:
    choice_of_data = input()
    if (choice_of_data == '1'):
        transact = load_transaction('shopping.txt', order)
        print('You selected Amazon dataset')
        print(transact)
        break
    elif (choice_of_data == '2'):
        transact = load_transaction('dMart_list.txt', order)
        print('You selected D-mart dataset')
        print(transact)
        break
    elif (choice_of_data == '3'):
        transact = load_transaction('instacart_list.txt', order)
        print('You selected Instacart dataset')
        print(transact)
        break
    elif (choice_of_data == '4'):
        transact = load_transaction('Walmart_list.txt', order)
        print('You selected walmart dataset')
        print(transact)
        break
    elif (choice_of_data == '5'):
        transact = load_transaction('Cosco_list.txt', order)
        print('You selected Cosco dataset')
        print(transact)
        break
    else:
        print("Invalid selection, please enter the number corresponding to the data")
        break

print("enter minimum support value")
min_support = float(input())
print("enter minimum confidence value")
min_confidence = float(input())
start = time.time()
print(start)
c = {}  # set of candidates as dictionary
l = {}
discarded = {}
itemsize = 1
c.update({itemsize: [[f] for f in order]})
supp_count_l = {}


def count_occurences(itemsets, transaction):
    count = 0
    for i in range(len(transaction)):
        if set(itemsets).issubset(set(transaction[i])):
            count += 1
    return count


def get_frequent(itemsets, transaction, min_supp, pre_deiscarded):
    l = []
    supp_count = []
    new_discarded = []
    num_trans = len(transaction)
    print(num_trans)
    k = len(pre_deiscarded.keys())

    for s in range(len(itemsets)):
        discrd_before = False
        if k > 0:
            for m in pre_deiscarded[k]:
                if set(m).issubset(set(itemsets[s])):
                    discrd_before = True
                    break
        if not discrd_before:
            count = count_occurences(itemsets[s], transaction)
            if count / num_trans >= min_supp:
                l.append(itemsets[s])
                supp_count.append(count)
            else:
                new_discarded.append(itemsets[s])
    return l, supp_count, new_discarded


f, sup, new_discarded = get_frequent(c[1], transact, min_support, discarded)
discarded.update({itemsize: new_discarded})
l.update({itemsize: f})
supp_count_l.update({itemsize: sup})


def print_table(t, supp_con):
    print("Itemset | frequency")
    for k in range(len(t)):
        print("{} : {}".format(t[k], supp_con[k]))
    print("\n\n")


print("l1:\n")
print_table(l[1], supp_count_l[1])


def join_two_itemsets(i1, i2, order):
    i1.sort(key=lambda x: order.index(x))
    i2.sort(key=lambda x: order.index(x))

    for i in range(len(i1) - 1):
        if i1[1] != i2[i]:
            return []
    if order.index(i1[-1]) < order.index(i2[-1]):
        return i1 + [i2[-1]]
    return []


def join_set_itemsets(sets, order):
    c = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            item_set_out = join_two_itemsets(sets[i], sets[j], order)
            if len(item_set_out) > 0:
                c.append(item_set_out)
    return c


k = itemsize + 1

convergence = False
while not convergence:
    c.update({k: join_set_itemsets(l[k - 1], order)})
    print("table C{}: \n".format(k))
    print_table(c[k], [count_occurences(i, transact) for i in c[k]])
    f, sup, new_discarded = get_frequent(c[k], transact, min_support, discarded)
    discarded.update({k: new_discarded})
    l.update({k: f})
    supp_count_l.update({k: sup})
    if len(l[k]) == 0:
        convergence = True
    else:
        print("table l{}: \n".format(k))
        print_table(l[k], supp_count_l[k])
    k += 1


def powerset(s):
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def write_rules(X, X_S, S, confidence, supp, num_trnsactions):
    out_rules = ""
    out_rules += "frequent itemsets:{}\n".format(X)
    out_rules += "       Rule: {} --> {}\n".format(list(S), list(X_S))
    out_rules += "      Conf: {0:2.3f}".format(confidence)
    out_rules += "      Support: {0:2.3f}\n".format(supp / num_trnsactions)
    return out_rules


associate_rule = ""
for i in range(1, len(l)):
    for j in range(len(l[i])):
        s = list(powerset(set(l[i][j])))
        # print(s)
        s.pop()
        for z in s:
            S = set(z)
            # print("1")
            # print(S)
            X = set(l[i][j])
            # print("2")
            # print(X)
            X_S = set(X - S)
            # print("3")
            # print(X_S)
            sup_x = count_occurences(X, transact)
            sup_x_s = count_occurences(X_S, transact)
            confidence = sup_x / count_occurences(S, transact)
            if confidence >= min_confidence and sup_x >= min_support:
                associate_rule += write_rules(X, X_S, S, confidence, sup_x, len(transact))
print("Association Rules using Apriori")
print(associate_rule)
end = time.time()
AprioriTime = end - start
print("AprioriTime: ")
print(AprioriTime)

for i in range(1, len(transact)):
    for j in range(i, len(transact[i])):
        s = list(powerset(set(transact[i][j])))
        # print(s)
        s.pop()
        for z in s:
            S = set(z)
            X = set(transact[i][j])
            X_S = set(X - S)
            sup_x = count_occurences(X, transact)
            sup_x_s = count_occurences(X_S, transact)
            if count_occurences(S, transact) != 0:
                confidence = sup_x / count_occurences(S, transact)
                if confidence >= min_confidence and sup_x >= min_support:
                    associate_rule += write_rules(X, X_S, S, confidence, sup_x, len(transact))
print("Association Rules using Brute Force")
print(associate_rule)
end_brute = time.time()
bruteTime = end_brute - start
print("bruteTime: ")
print(bruteTime)

while True:
    if (choice_of_data == '1'):
        print('Result for Amazon Database are: ')
        print("For Minimum Support: ", min_support)
        print("For Minimum Confidence: ", min_confidence)
        print("Time taken by Apriori algorithm is: ", AprioriTime)
        print("Time taken by Brute Force is :", bruteTime)
        print("Apriori Algorithm is ", bruteTime / AprioriTime, " times faster than Brute-Force Algorithm")
        break
    elif (choice_of_data == '2'):
        print('Result for D-mart Database are: \n')
        print("For Minimum Support: ", min_support)
        print("For Minimum Confidence: ", min_confidence)
        print("Time taken by Apriori algorithm is: ", AprioriTime)
        print("Time taken by Brute Force is :", bruteTime)
        print("Apriori Algorithm is ", bruteTime / AprioriTime, " times faster than Brute-Force Algorithm")
        break
    elif (choice_of_data == '3'):
        print('Result for Instacart Database are: \n')
        print("For Minimum Support: ", min_support)
        print("For Minimum Confidence: ", min_confidence)
        print("Time taken by Apriori algorithm is: ", AprioriTime)
        print("Time taken by Brute Force is :", bruteTime)
        print("Apriori Algorithm is ", bruteTime / AprioriTime, " times faster than Brute-Force Algorithm")
        break
    elif (choice_of_data == '4'):
        print('Result for Walmart Database are: \n')
        print("For Minimum Support: ", min_support)
        print("For Minimum Confidence: ", min_confidence)
        print("Time taken by Apriori algorithm is: ", AprioriTime)
        print("Time taken by Brute Force is :", bruteTime)
        print("Apriori Algorithm is ", bruteTime / AprioriTime, " times faster than Brute-Force Algorithm")
        break
    elif (choice_of_data == '5'):
        print('Result for Cosco Database are: \n')
        print("For Minimum Support: ", min_support)
        print("For Minimum Confidence: ", min_confidence)
        print("Time taken by Apriori algorithm is: ", AprioriTime)
        print("Time taken by Brute Force is :", bruteTime)
        print("Apriori Algorithm is ", bruteTime / AprioriTime, " times faster than Brute-Force Algorithm")
        break
    else:
        print("Invalid selection, please enter the number corresponding to the data")
        break
