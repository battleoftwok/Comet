
with open("src/table.txt", "r", encoding='utf-8') as file:
    data = file.read()

for i in data:
    print(i)
