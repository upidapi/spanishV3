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
#
# a.adopt(b)
# b.adopt(d)
# c.parallelize(b)
# a.make_head_tail()
# a.structure_image()


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

# a.adopt(d)
# a.adopt(e)
#
# b.adopt(d)
# b.adopt(e)
# b.adopt(f)
#
# c.adopt(e)
# c.adopt(f)
#
# a.make_head_tail()
# print(1, a.sectioned_list())
# a.point_simplify()
# print(1, a.sectioned_list())

a.adopt(d)
a.adopt(e)
a.sync()
a.get_head().adopt(c)
b.parallelize(a)
a.sync()
a.structure_image()
# print(a.sectioned_list())
# print(a.order_list())


# a.adopt(c)
# a.sync()
# print(a.gui_convert())
# print(1, a.sectioned_list())
# a.r_insert(z)
# print(2, a.sectioned_list())
# b.parallelize(a)
# print(3, a.sectioned_list())
# d.parallelize(c)
# print(4, a.sectioned_list())
# b.contract()
# print(5, a.sectioned_list())
# e.sync()
# print(6, a.sectioned_list())
# a.get_head().adopt(e.get_head())
# print(7, a.sectioned_list())
# a.sync()
# print(8, a.sectioned_list())


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
