# v1.0
class CLI:
    def __init__(self, startSymb, bye):
        self.byeMsg = bye
        self.startSymb = startSymb
        self.commands = {}
        self.commands.keys
        self.addCommand('help','show all commands', 0, self.help)
        self.addCommand('exit','exit',0, self.leave)

    def addCommand(self, name: str, description: str, argsAmount: int, func: any):
        self.commands[name] = {'args':argsAmount, 'function':func, 'description':description}

    def hasCommand(self, cmd: str):
        if(self.commands.get(cmd) == None):
            return False
        return True
    def leave(self):
        raise KeyboardInterrupt()
    def help(self):
        print("------------------------CLI-----------------------")
        print("                  Made by Possiug!                ")
        print("--------------------------------------------------")
        values = list(self.commands.values())
        keys = list(self.commands.keys())
        for i in range(0,values.__len__()):
            print(f"\t{keys[i]} - args amount: {values[i]['args']} - {values[i]['description']}")

    def cmdProc(self, cmd: str):
        
        cmd = cmd.split(' ')
        if(not self.hasCommand(cmd[0])):
            print('command not found!')
            return
        command = self.commands.get(cmd[0])
        if(not cmd.__len__() - 1 == command.get('args')):
            print('incorrect args amount!')
            return
        cmd.remove(cmd[0])
        args = ()
        for i in cmd:
            args += (i,)
        command.get('function')(*args)

    def mainLoop(self):
        while(True):
            try:
                cmd = input(self.startSymb)
                self.cmdProc(cmd)
            except KeyboardInterrupt:
                print(self.byeMsg)
                break
            except Exception as err:
                print('err in CLI mainLoop!', err)