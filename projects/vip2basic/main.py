import vip
import numpy

import elements.numpy.array

server = vip.Server()

server.addClass(numpy.ndarray, elements.numpy.array.ndarrayWrap)

server.serve('0.0.0.0', 80)