from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import pylab
import numpy as np
import mpmath
from sympy import (I, oo, Sum, exp, pi, factorial, zeta, im, re)
from sympy.abc import n, x, k

mpmath.dps = 5

#B = oo  # infinity
B = 10
bounds = (k,1,B)

Riesz_expr = Sum(
    ((-1)**(k+1) * (-x)**k)
    / (factorial(k-1)*zeta(2*k)), bounds)

Riesz = lambda z: Riesz_expr.evalf(subs={'x':z})

Max = 2
fig = pylab.figure()
ax = Axes3D(fig)
X = np.arange(-Max, Max, 0.125)
Y = np.arange(-Max, Max, 0.125)
X, Y = np.meshgrid(X, Y)
xn, yn = X.shape
W = X*0
for xk in range(xn):
    for yk in range(yn):
        try:
            z = X[xk,yk] + I*Y[xk,yk]
            w = Riesz(z)
            w = im(w)
            if w != w:
                raise ValueError
            W[xk,yk] = w
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            # can handle special values here
            raise exc
    print (xk, " of ", xn)

# can comment out one of these
ax.plot_surface(X, Y, W, rstride=1, cstride=1, cmap=cm.jet)
ax.plot_wireframe(X, Y, W, rstride=5, cstride=5)

pylab.show()