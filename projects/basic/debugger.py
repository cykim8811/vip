
def debug(target):
    root = target
    directory = []
    while True:
        print("/".join([str(t) for t in directory]) + "/>", end="")
        command = input().split()
        if command[0] == "cd":
            if type(target) is list:
                target = target[int(command[1])]
                directory.append(int(command[1]))
                continue
            if len(command) > 1 and command[1] == "..":
                del directory[-1]
                target = root
                for i in directory:
                    target = target.__dict__[i] if type(i) is str else target[i]
                continue
            if len(command) > 1 and command[1] in target.__dict__:
                target = target.__dict__[command[1]]
                directory.append(command[1])
        if command[0] == "ls":
            if type(target) is list:
                print('list:[')
                for l in target:
                    print("\t" + str(l))
                print(']')
                continue
            for l in target.__dict__:
                print("\t" + str(l))
        if command[0] == "pwd":
            print(target)
        if command[0] == "exit":
            return