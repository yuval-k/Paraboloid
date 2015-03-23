import math
import argparse
import svgwrite
from svgwrite import cm

# all numbers are in CM
def main():

    import argparse   # only supported on python 2.7, rest of this script may be used with python 2.6
    parser = argparse.ArgumentParser(description='Creates petals for parabolic reflectors')
    parser.add_argument('--number', '-n', dest='numpetals', type=int, default=16,
        help='How many petals are going to be in a circle. 16 is default')
    parser.add_argument('--focal-length','-fl', dest='focallength', type=int, required = True,
        help='The focal length in CM')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--max-x','-x', dest='maxx', type=int,
                help='Max x (the x value of the parabolla)')
    group.add_argument('--max-r','-r', dest='maxr', type=int,
                help='Approximage length of petal.')
    parser.add_argument('--screw-offset', dest='screwrad', type=float, default = 5*.8,
                help='Offset of screw hole from petal\support circle center')
    parser.add_argument('--support-circle-size', '-scs', dest='supportsize', type=int, default = 6,
                help='Size of the support circle size')
    parser.add_argument('--screw-hole-size', '-shs', dest='screwhole', type=float, default = .3,
    help='Size of the screw hole in CM')

    args = parser.parse_args()
    if args.maxr is not None:
        maxx = args.maxr
        maximize_r = True
    else:
        maxx = args.maxx
        maximize_r = False
    save_files(args.numpetals, args.focallength, maxx ,maximize_r, args.screwrad, args.supportsize, args.screwhole)

def save_files(num_petals, focal_length, maxx, maximize_r, screwrad, supportcirclesize, screwhole):
    pr = ParabolicReflector(num_petals, focal_length, maxx, maximize_r, screwrad, supportcirclesize, screwhole)
    pr.draw_svg()
    pr.draw_circle()


def draw_parabola_in_free_cad():
    x =1
    delta = 1
    points = 20
    fx = f(x)
    gem = App.ActiveDocument.Sketch002.addGeometry(Part.Line(App.Vector(0,0,0),App.Vector(x,fx,0)))

    for i in range(points - 1):
        prevx = x
        fprevx = fx
        x = x + delta
        fx = f(x)
        prevgem = gem
        gem = App.ActiveDocument.Sketch002.addGeometry(Part.Line(App.Vector(prevx,fprevx,0),App.Vector(x,fx,0)))
        App.ActiveDocument.Sketch002.addConstraint(Sketcher.Constraint('Coincident',prevgem,2,gem,1))


class ParabolicReflector(object):
    def __init__(self, num_petals, focal_length, maxx, maximize_r, screwrad, supportcirclesize, screwhole):
        self.num_petals = num_petals
        self.focal_length = focal_length
        self.maxx = maxx
        self.maximize_r = maximize_r
        self.screwrad = screwrad
        self.supportcirclesize = supportcirclesize
        self.screwhole = screwhole

    def get_r_or_x(self, r, x):
        if self.maximize_r:
            return r
        return x

    def f(self, x):
        return x*x/(4*self.focal_length)

    def r1(self, x):
        # arch length from 0 to x
        xyroot = (x**2+4*(self.focal_length**2))**.5
        log_term = (x + xyroot )/(2*self.focal_length)
        return (  x*xyroot + 4*(self.focal_length**2)*math.log(log_term)   )/(4*self.focal_length)
        #return x+((x**3)/(24*(self.focal_length**2)))

    def deltaw(self, x, r1):
        w = 2*math.pi*(r1-x)
	return w / (2*self.num_petals)
        # return (math.pi/self.num_petals)*((x**3)/(24*self.focal_length**2))

    def r_l(self,x):
        r1_ = self.r1(x)
        deltaw_ = self.deltaw(x, r1_)
        return r1_, math.pi*r1_/self.num_petals - deltaw_
        return r1_*math.cos(math.pi/self.num_petals)-deltaw_*math.sin(math.pi/self.num_petals), r1_*math.sin(math.pi/self.num_petals)-deltaw_*math.cos(math.pi/self.num_petals)

    def generate_points(self, delta = .5):
        list_of_ponts = [(0,0)]
        list_of_ponts_reverse = []

        x = delta
        r = 0
        while self.get_r_or_x(r,x) <= self.maxx:
            r,l = self.r_l(x)
            list_of_ponts.append((l,r))
            list_of_ponts_reverse.insert(0,(-l,r))
            x+=delta
        print "Max x is ", (x-delta), "max y is", self.f(x)
        return list_of_ponts + list_of_ponts_reverse

    def draw_svg(self, name = "petal.svg"):
        factor = 1
        generated_points =  self.generate_points()
        # some of the points are negative... adding this offset will move them to be non-negative.
        offset = max([x for x,y in generated_points])
        max_y = max([y for x,y in generated_points])
        print "Max L is:",offset, "Max R is", max_y, "(width is", offset*2, ")"
        height  = max_y + 10
        width = offset*2+10
        offset_y = 5
        offset += 5
        dwg = svgwrite.Drawing(filename=name, size=(width*cm,  height*cm), viewBox=('0 0 %d %d'%(width, height)), debug=True)
        shapes = dwg.add(dwg.g(id='shapes'))
        generated_points = [(x*factor, y*factor) for x,y in generated_points]
        points = [(x+offset, y+offset_y) for x,y in  generated_points]
        # set presentation attributes at object creation as SVG-Attributes
        polygon = shapes.add(dwg.polygon(points=points, stroke='blue', fill="none",
                              stroke_width=.1))

        circle = shapes.add(dwg.circle(center = (0+offset, self.screwrad +offset_y), r = self.screwhole,  stroke='blue', fill="none",
                      stroke_width=.1))
        dwg.save()


    def draw_circle(self, name = "discs.svg"):

        rad = self.supportcirclesize

        height  = rad*2
        width = rad*2
        dwg = svgwrite.Drawing(filename=name, size=(width*cm,  height*cm), viewBox=('0 0 %d %d'%(width, height)), debug=True)
        shapes = dwg.add(dwg.g(id='shapes'))
        # set presentation attributes at object creation as SVG-Attributes
        circle = shapes.add(dwg.circle(center = (rad,rad), r = rad, stroke='blue', fill="none", stroke_width=.1))
        circle = shapes.add(dwg.circle(center = (rad,rad), r = self.screwhole,  stroke='blue', fill="none",
                              stroke_width=.1))
        for i in range(self.num_petals):
            x = self.screwrad*math.sin(2*math.pi*i/self.num_petals)
            y = self.screwrad*math.cos(2*math.pi*i/self.num_petals)
            circle = shapes.add(dwg.circle(center = (rad+x,rad+y), r = self.screwhole,  stroke='blue', fill="none",
                              stroke_width=.1))

        dwg.save()

if __name__ == '__main__':
    main()
