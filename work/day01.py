a = [1, 2, 3]
b = a
b.append(4)
# print(a)  # [1,2,3,4]
# print(tuple(a) == (1, 2, 3, 4))  # True
# print({1, 2, 2, 3})  # {1, 2, 3}
# print({"x": 1}.get("y", 0))  # 0

"""
1. `dedupe_preserve_order(items)` 
- return a list with duplicates removed, 
keeping the first occurrence of each item 
and the original order.
   `dedupe_preserve_order([3, 1, 3, 2, 1])` 
   -> `[3, 1, 2]`
"""


def dedupe_preserve_order(items: list) -> list:
    # read the list, create a dict

    seen_set = set()
    result = []
    for item in items:
        if item not in seen_set:
            seen_set.add(item)
            result.append(item)

    return result

    # return list(dict.fromkeys(items))


if __name__ == "__main__":

    dedup_list = dedupe_preserve_order([3, 1, 3, 2, 1])
    print(dedup_list)
