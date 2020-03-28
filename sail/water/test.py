from multiprocessing import Pool

def F(x):
    return x * x

class SeriesInstance(object):
    def __init__(self):
        self.numbers = [1,2,3]
        self.F = F

    def run(self):
        p = Pool()
        out = p.map(self.F, self.numbers)
        p.close()
        p.join()
        return out

if __name__ == '__main__':
    print(SeriesInstance().run())