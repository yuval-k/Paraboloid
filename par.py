import math
import svgwrite
from svgwrite import cm

# all numbers are in CM
def main():

    import argparse   # only supported on python 2.7, rest of this script may be used with python 2.6
    parser = argparse.ArgumentParser(description='Creates petals for parabolic reflectors. this will create two files: petal.svg with the drawing of the petal, and discs.svg that draws the disks that can be used to attach all the petals together.')
    parser.add_argument('--number', '-n', dest='numpetals', type=int, default=8,
        help='How many petals are going to be in a circle. is default')
    parser.add_argument('--focal-length','-fl', dest='focallength', type=float, default = 30,
        help='The focal length in CM')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--max-x','-x', dest='maxx', type=float,
                help='Max x (the x value of the parabolla). mutually exclusive with max r')
    group.add_argument('--max-r','-r', dest='maxr', type=float,
                help='Approximage length of petal in cm. mutually exclusive with max x')
    parser.add_argument('--screw-offset', dest='screwrad', type=float, default = 5*.8,
                help='Offset of screw hole from petal\support circle center in cm')
    parser.add_argument('--support-circle-size', '-scs', dest='supportsize', type=float, default = 6,
                help='Size of the support circle size in cm')
    parser.add_argument('--screw-hole-size', '-shs', dest='screwhole', type=float, default = .3,
    help='Size of the screw hole in cm')
    parser.add_argument('--center-hole-size', '-chs', dest='centerhole', type=float, default = .3,
    help='Size of the center hole in the disc in cm')

    args = parser.parse_args()
    if args.maxr is not None:
        maxx = args.maxr
        maximize_r = True
    else:
        maxx = args.maxx
        maximize_r = False
    save_files(args.numpetals, args.focallength, maxx ,maximize_r, args.screwrad, args.supportsize, args.screwhole, args.centerhole, .1)

def save_files(num_petals, focal_length, maxx, maximize_r, screwrad, supportcirclesize, screwhole, centerhole, stroke_width):
    pr = ParabolicReflector(num_petals, focal_length, maxx, maximize_r, screwrad, supportcirclesize, screwhole, centerhole, stroke_width)
    pr.draw_svg()
    pr.draw_circle()

class ParabolicReflector(object):
    def __init__(self, num_petals, focal_length, max_value, maximize_r, screwrad, supportcirclesize, screwhole, centerhole, stroke_width):
        self.num_petals = num_petals
        self.focal_length = focal_length
        self.max_value = max_value
        self.maximize_r = maximize_r
        self.screwrad = screwrad
        self.supportcirclesize = supportcirclesize
        self.screwhole = screwhole
        self.centerhole = centerhole
        self.stroke_width = stroke_width
        self.delta = .5
        self.margin_x = 2
        self.margin_y = 2

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

    def r_l(self,x):
        # get the length of the petal at point x
        r1_ = self.r1(x)

        # angle - the angle of the arch of the petal (the angle of a petal time x/r to compensate for the w)
        # x is the radius we want and r1 is the radius we have; so the real circl we want is not of angle 2pi/(num_petals); 
        # but rather need to take into account that along the circumference the error (w) is of 2pi(r-x); so the angle is compenstated accordingly
        # angel of leaf = ([r - (r-x)]/r)*2pi/numpetals = (x/r)*2pi/numpetals
        angle = 2*math.pi*x/(r1_*self.num_petals)

        # use half the angle for symmetry
        # i should really make a drawing to explain the math... :\
        # l = half the chord
        l = r1_*math.sin(angle/2)
        # r = r1-h (radius till the chord)
        h = r1_*math.cos(angle/2)
        return h,l


    def generate_points(self):
        list_of_ponts = [(0,0)]
        list_of_ponts_reverse = []

        x = self.delta
        r = 0
        while self.get_r_or_x(r,x) <= self.max_value:
            r,l = self.r_l(x)
            list_of_ponts.append((l,r))
            list_of_ponts_reverse.insert(0,(-l,r))
            x+=self.delta
        print "Max x is ", (x-self.delta), "max y is", self.f(x)
        return list_of_ponts + list_of_ponts_reverse

    def draw_svg(self, name = "petal.svg"):

        generated_points =  self.generate_points()
        # some of the points are negative... adding this offset will move them to be non-negative.
        offset_x = max([x for x,y in generated_points])
        max_y = max([y for x,y in generated_points])
        print "Max L is:",offset_x, "Max R is", max_y, "(width is", offset_x*2, ")"
        height  = max_y + self.margin_y
        width = offset_x*2+self.margin_x
        offset_y  = (self.margin_y / 2)
        offset_x += (self.margin_x / 2)
        dwg = svgwrite.Drawing(filename=name, size=(width*cm,  height*cm), viewBox=('0 0 %d %d'%(width, height)), debug=True)
        shapes = dwg.add(dwg.g(id='shapes'))
        points = [(x+offset_x, y+offset_y) for x,y in  generated_points]
        # set presentation attributes at object creation as SVG-Attributes
        polygon = shapes.add(dwg.polygon(points=points, stroke='blue', fill="none",
                              stroke_width=self.stroke_width))

        circle = shapes.add(dwg.circle(center = (0+offset_x, self.screwrad +offset_y), r = self.screwhole,  stroke='blue', fill="none",
                      stroke_width=self.stroke_width))
        dwg.save()


    def draw_circle(self, name = "discs.svg"):

        rad = self.supportcirclesize

        height  = rad*2
        width = rad*2
        dwg = svgwrite.Drawing(filename=name, size=(width*cm,  height*cm), viewBox=('0 0 %d %d'%(width, height)), debug=True)
        shapes = dwg.add(dwg.g(id='shapes'))
        # set presentation attributes at object creation as SVG-Attributes
        circle = shapes.add(dwg.circle(center = (rad,rad), r = rad, stroke='blue', fill="none", stroke_width=self.stroke_width))
        circle = shapes.add(dwg.circle(center = (rad,rad), r = self.centerhole,  stroke='blue', fill="none",
                              stroke_width=self.stroke_width))
        for i in range(self.num_petals):
            x = self.screwrad*math.sin(2*math.pi*i/self.num_petals)
            y = self.screwrad*math.cos(2*math.pi*i/self.num_petals)
            circle = shapes.add(dwg.circle(center = (rad+x,rad+y), r = self.screwhole,  stroke='blue', fill="none",
                              stroke_width=self.stroke_width))

        dwg.save()

if __name__ == '__main__':
    main()
