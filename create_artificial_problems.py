import os
from copy import deepcopy
from random import choice, random, shuffle, randint
from typing import List


class Size:
    def __init__(self, length: int, width: int, height: int):
        self.length = length
        self.width = width
        self.height = height


class Position:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z


class Cuboid:
    def __init__(self, size: Size, position: Position):
        self.size = size
        self.position = position

    def random_split(self):
        dimension_to_split = choice(["L", "W", "H"])
        size1 = deepcopy(self.size)
        position1 = deepcopy(self.position)
        size2 = deepcopy(self.size)
        position2 = deepcopy(self.position)
        # round dimensions to factor
        roundingfactor = 10;
        if dimension_to_split == "L":
            size1.length = int(roundingfactor * round(random() * self.size.length / roundingfactor))
            size2.length = self.size.length - size1.length
            position2.x += size1.length
            if (size1.length < 10) or (size2.length < 10):
                return  # we do not split if the remaining dimension of one of the cubes is less than 10.
            return [Cuboid(size1, position1), Cuboid(size2, position2)]
        elif dimension_to_split == "W":
            size1.width = int(roundingfactor * round(random() * self.size.width / roundingfactor))
            size2.width = self.size.width - size1.width
            position2.y += size1.width
            if (size1.width < 10) or (size2.width < 10):
                return  # we do not split if the remaining dimension of one of the cubes is less than 10.
            return [Cuboid(size1, position1), Cuboid(size2, position2)]
        else:
            size1.height = int(roundingfactor * round(random() * self.size.height / roundingfactor))
            size2.height = self.size.height - size1.height
            position2.z += size1.height
            if (size1.height < 10) or (size2.height < 10):
                return  # we do not split if the remaining dimension of one of the cubes is less than 10.
            return [Cuboid(size1, position1), Cuboid(size2, position2)]


def recursively_split_cuboid(cuboid: Cuboid, max_num_splits: int):
    cuboids = [cuboid]
    num_splits = 0
    while num_splits < max_num_splits:
        cuboid_to_split = choice(cuboids)
        split_cuboids = cuboid_to_split.random_split()
        if split_cuboids is not None:
            cuboids.remove(cuboid_to_split)
            cuboids.extend(split_cuboids)
            num_splits += 1
    
    #substract_from_dimensions(cuboids)
    shuffle(cuboids)
    return cuboids


def substract_from_dimensions(cuboids: List[Cuboid]):
    # substract amount of mm's from a split
    substract = 1;
    # with probability
    substractprobability = 0.5;
    for cuboid in cuboids:
        prob = random()
        #print("substract")
        #print(prob)
        if(prob < (substractprobability/3)):
            cuboid.size.length -= substract
        elif(prob < (2*substractprobability/3)):
            cuboid.size.width -= substract
        elif (prob < substractprobability):
            cuboid.size.height -= substract


def to_csv(cuboids: List[Cuboid], file_path: str, include_position: bool = False):
    path, _ = os.path.split(file_path)
    if not os.path.exists(path):
        os.mkdir(path)

    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, "w") as f:
        if not include_position:
            f.write(f"item,length,width,height\n")
            for index, cuboid in enumerate(cuboids):
                #shuffle the printing order of dimensions of items
                printorder = 0
                #printorder = random()
                if(printorder < 0.2):
                    printlength = cuboid.size.length
                    printwidth = cuboid.size.width
                    printheigth = cuboid.size.height
                elif(printorder < 0.3):
                    printlength = cuboid.size.length
                    printwidth = cuboid.size.height
                    printheigth = cuboid.size.width
                elif (printorder < 0.4):
                    printlength = cuboid.size.width
                    printwidth = cuboid.size.length
                    printheigth = cuboid.size.height
                elif (printorder < 0.6):
                    printlength = cuboid.size.width
                    printwidth = cuboid.size.height
                    printheigth = cuboid.size.length
                elif (printorder < 0.8):
                    printlength = cuboid.size.height
                    printwidth = cuboid.size.width
                    printheigth = cuboid.size.length
                else:
                    printlength = cuboid.size.height
                    printwidth = cuboid.size.length
                    printheigth = cuboid.size.width
                f.write(f"item{index},{printlength},{printwidth},{printheigth}\n")
        else:
            f.write(f"item,length,width,height,x,y,z\n")
            for index, cuboid in enumerate(cuboids):
                f.write(f"item{index},{cuboid.size.length},{cuboid.size.width},{cuboid.size.height},"
                        f"{cuboid.position.x},{cuboid.position.y},{cuboid.position.z}\n")


if __name__ == "__main__":
    euro_pallet_length = 800
    euro_pallet_width = 1200
    max_stacking_height = 1500

    # easy
    # remove some margin from the sides
    euro_pallet_bounding_box = Cuboid(Size(euro_pallet_length - randint(1, 50),
                                           euro_pallet_width - randint(1, 50),
                                           max_stacking_height - randint(1, 50)),
                                      Position(0, 0, 0))
    items_easy = recursively_split_cuboid(euro_pallet_bounding_box, 9)  # 9 splits is 10 items
    to_csv(items_easy, "dataset1/small.csv", include_position=False)
    to_csv(items_easy, "dataset1/small_solution.csv", include_position=True)

    # medium
    euro_pallet_bounding_box = Cuboid(Size(euro_pallet_length - randint(1, 50),
                                           euro_pallet_width - randint(1, 50),
                                           max_stacking_height - randint(1, 50)),
                                      Position(0, 0, 0))
    items_medium = recursively_split_cuboid(euro_pallet_bounding_box, 24)  # 24 splits is 25 items
    to_csv(items_medium, "dataset1/medium.csv", include_position=False)
    to_csv(items_medium, "dataset1/medium_solution.csv", include_position=True)

    # large
    euro_pallet_bounding_box = Cuboid(Size(euro_pallet_length - randint(1, 50),
                                           euro_pallet_width - randint(1, 50),
                                           max_stacking_height - randint(1, 50)),
                                      Position(0, 0, 0))
    items_large = recursively_split_cuboid(euro_pallet_bounding_box, 99)  # 99 splits is 100 items
    to_csv(items_large, "dataset1/large.csv", include_position=False)
    to_csv(items_large, "dataset1/large_solution.csv", include_position=True)


