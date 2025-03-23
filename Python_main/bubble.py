
def timsort(arr):
    min_run = 32
    n = len(arr)

    for i in range(0, n, min_run):
        insertion_sort(arr, i, min((i + min_run - 1), n - 1))

    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = left + size - 1
            right = min((left + 2 * size - 1), (n - 1))
            merge(arr, left, mid, right)
        size = 2 * size

def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def merge(arr, left, mid, right):
    if arr[mid] <= arr[mid + 1]:
        return
    left_half = arr[left:mid + 1]
    right_half = arr[mid + 1:right + 1]
    k = left
    i = j = 0
    while i < len(left_half) and j < len(right_half):
        if left_half[i] <= right_half[j]:
            arr[k] = left_half[i]
            i += 1
        else:
            arr[k] = right_half[j]
            j += 1
        k += 1
    arr[k:right + 1] = left_half[i:] + right_half[j:]

# Example usage
arr = [64, 34, 25, 12, 22, 11, 90]
timsort(arr)
print("Sorted array:", arr)
