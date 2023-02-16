# What does this package do?
This package contains the dataclasses used for ensuring the qulity of the data received after scraping.

## What are the classes supposed to do?
Every class present in this package is supposed to implement the __post__init__ method. With in this method, every
classes' writer is responsible for implementing the respective checks that define the correctness of the object.