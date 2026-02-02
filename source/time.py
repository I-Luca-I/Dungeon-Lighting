import time

class timer:
    def __init__(self) -> None:
        self.data = []
        self.sum = [0 for _ in range(100)]
        self.count = 0

    def reset(self) -> None:
        self.count += 1
        self.printable = {}
        self.mid_printable = {}
        for i in range(1, len(self.data)):
            self.printable.update({self.title[i] : int((self.data[i]-self.data[i-1])*1000)})
            self.sum[i] += (self.data[i]-self.data[i-1])
            self.mid_printable.update({self.title[i] : int((self.sum[i]/self.count)*1000)})
        
        self.data = []
        self.title = []
        self.add_breakpoint()

    def add_breakpoint(self, title:str="default") -> None:
        self.data.append(time.time())
        self.title.append(title)
        
