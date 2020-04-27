import math
import numpy
import matplotlib.pyplot as plt


def bs_inv(si, sf, H=250, B=0.0, G=1.0, verbose=False):

    # coefficients
    a = 0.0000003480061091
    b = 250.
    c = 0.000003091619094
    d = 0.0000682775184551527
    e = -0.0301431777

    # stat cap
    sc = 50000000

    # states coefficients
    alpha = (a * numpy.log(H + b) + c) * (1 + B) * G
    beta = (d * (H + b) + e) * (1 + B) * G

    # shortcuts
    minf = min(sc, sf)
    mini = min(sc, si)
    maxf = max(sc, sf)
    maxi = max(sc, si)
    ratio = numpy.divide(beta, alpha)
    slope = alpha * sc + beta

    # energy before cap
    dE_bc = numpy.divide(numpy.log(numpy.divide(minf + ratio, mini + ratio)), alpha)
    # print(dE_bc[0], numpy.log((minf + ratio) / (mini + ratio))[0], alpha[0])
    # energy after cap
    dE_ac = numpy.divide(maxf - minf, slope)
    # energy total
    dE = dE_bc + dE_ac

    if verbose == 1:
        print(f"h = {H:.4g}, b = {B:.4g}, g = {G:.4g}")
    elif verbose == 2:
        print("=== Battle stats formula ===")
        print("")
        print("= States variables =")
        print(f"Happy: {H:.4g}")
        print(f"Bonus: {B:.4g}")
        print(f"Gym dot: {G:.4g}")
        print("")
        print("= States coefficients =")
        print(f"alpha: {alpha:.4g}")
        print(f"beta: {beta:.4g}")
        print("")
        print("= Energy =")
        print(f"Before CAP: {dE_bc:,.1f}")
        print(f"After CAP: {dE_ac:,.1f}")
        print(f"Total: {dE:,.1f}")

    return dE


# Minimal energy for normalisation
Hmax = 5025
Bmax = 1.02 * 1.1 * 1.02 - 1.
Gmax = 7.5
Emin = bs_inv(si, sf, H=Hmax, B=Bmax, G=Gmax)

# Happy
x_tab = numpy.arange(250, 5026, 25)
e_tab = bs_inv(si, sf, H=x_tab, B=Bmax, G=Gmax)
eta = e_tab / Emin

plt.xlabel("Happy")
plt.ylabel("Energy factor")
plt.plot(x_tab, eta)
plt.savefig("happy.png")
plt.clf()

# Gym
x_tab = numpy.arange(2.0, 7.6, 0.1)
e_tab = bs_inv(si, sf, H=Hmax, B=Bmax, G=x_tab)
eta = e_tab / Emin

plt.xlabel("Gym")
plt.xlabel("Energy factor")
plt.plot(x_tab, eta)
plt.savefig("gym.png")
plt.clf()

# # Bonus
# x_tab = numpy.arange(2.0, 7.6, 0.1)
# e_tab = bs_inv(si, sf, H=Hmax, B=Bmax, G=x_tab)
# eta = e_tab / Emin
#
# plt.xlabel("Gym")
# plt.xlabel("Energy factor")
# plt.plot(x_tab, eta)
# plt.savefig("gym.png")
# plt.clf()
