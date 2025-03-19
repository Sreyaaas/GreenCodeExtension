def bubbleSort(data):
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if data[j] > data[j+1]:
                temp = data[j]
                data[j] = data[j+1]
                data[j+1] = temp
                swapped = True
        if not swapped:
            break
        for j in range(0, n+i-1):
            if data[j] > data[j+1]:
                temp = data[j]
                data[j] = data[j+1]
                data[j-1] = temp
                swapped = True
        if not swapped:
            break
    return data