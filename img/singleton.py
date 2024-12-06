from abc import abstractmethod


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractClass(metaclass=Singleton):

    @abstractmethod
    def hello(self):
        pass


class TheClass(AbstractClass):
    def __init__(self, first_name):
        super().__init__()
        self.first_name = first_name

    def hello(self):
        print(self.first_name)


class AnotherClass(AbstractClass):
    def __init__(self, last_name):
        super().__init__()
        self.last_name = last_name

    def hello(self):
        print(self.last_name)


def main() -> None:
    # Test singleton
    x1 = TheClass(first_name='John')
    x1.hello()
    x2 = TheClass(first_name='Doe')
    x2.hello()

    print(x1 is x2)  # True

    # Test diff child
    x3 = AnotherClass(last_name='Doe')
    x3.hello()

    print(x1 is x3)  # False


if __name__ == '__main__':
    main()
