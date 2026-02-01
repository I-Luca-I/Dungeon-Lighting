import time

class timer:
    def __init__(self) -> None:
        self.data = []

    def reset(self) -> None:
        self.printable = {}
        for i in range(1, len(self.data)):
            self.printable.update({self.title[i] : self.data[i]-self.data[i-1]})
        
        self.data = []
        self.title = []
        self.add_breakpoint()

    def add_breakpoint(self, title:str="default") -> None:
        self.data.append(time.time())
        self.title.append(title)
