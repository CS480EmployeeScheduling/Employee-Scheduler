try:
    import psyco
    psyco.full()
except ImportError:
    print 'Psyco not available'

def menza():
    sol = []
    all_digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for a in range(1000) :
        for b in range(100) :
            c = a*b
            if c > 9999:
                digits = list("%.3d%.2d%.5d" % (a, b, c))
                digits.sort()
                if digits == all_digits :
                    sol.append({'a': a, 'b': b})
                    print "%.3d x %.2d = %.5d" % (a, b, c)
    return sol

if __name__ == '__main__':
    sol = menza()
    print len(sol)
