from Main import Node
from Constructor import convert
# a = convert("hello")
# b = convert("hi")
# c = convert("today")
# d = convert("uh")
# e = convert("eee")
# a = Node("a")
# b = Node("b")
# c = Node("c")
# d = Node("d")

# a.get_head().adopt(b)
# a.make_head_tail()
#
# c.get_head().adopt(d)
# a.merge(c)
# a.get_head().adopt(e)
# a.make_head_tail()
# print(a.order_list())
# a.gui_convert()
# import pygame as pg

a = Node("a")
b = Node("b")
c = Node("c")
d = Node("d")
e = Node("e")
f = Node("f")

# a.adopt(b)
# b.adopt(d)
# c.parallelize(b)
# a.make_head_tail()

# a.adopt(b)
# b.adopt(c)
# b.adopt(e)
#
# c.adopt(d)
#
# e.adopt(f)
# d.adopt(f)
# a.sync()
#
# a.structure_image(100)

# a.adopt(b)
# b.adopt(c)
#
# d.parallelize(b)
# e.parallelize(b)
# f.parallelize(c)
# a.sync()


# a.adopt(d)
# a.adopt(e)
# a.sync()
# a.get_head().adopt(c)
# b.parallelize(a)
# a.sync()
# a.structure_image()

# print(a.sectioned_list())
# print(a.order_list())


a.adopt(c)
a.sync()
a.r_insert(f)
b.parallelize(a)
d.parallelize(c)
# b.contract()
# e.sync()
# a.get_head().adopt(e.get_head())
a.sync()
a.structure_image()

# a.adopt(b)
# b.adopt(c)
# a.adopt(c)
# a.sync()
# a.structure_image()

# def bp_find_f_pars():
#     inp = "hello (wut() (nah) like)"
#     bet = ("(", ")")
#
#     pars = 1
#     for i in range(len(inp)):
#         if inp[i] == bet[0]:
#             for j in range(i, len(inp)):
#                 if inp[j] == bet[0]:
#                     pars += 1
#                 if inp[j] == bet[1]:
#                     pars -= 1
#                 if pars == 0:
#                     return i, j
#             break
