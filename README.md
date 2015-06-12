# Paraboloid
Creates a paraboloid tempaltes so they can be fabricated using flat materials. 
see:
http://ashokk_3.tripod.com/srinivasan.htm

An example instructable:
http://www.instructables.com/id/Parabolic-solar-oven/

The output files of this script are similar to discs.svg and petals.svg from that instructable.

## To Run
requires svgwrite to create svg files.

    pip install svgwrite

Usage example:

    python par.py -n 8 -f 30 --max-r 35 --support-circle-size 10 --center-hole-size 4 --screw-offset 7 

this creates a petal, assuming 8 petals per paraboloid. the parapoloid focus point is at 30cm; length of each petal is approx 35cm; the doughnut to mount the petals on (support circle) is 10 cm outer radius 4cm inner radius; the the offset of a screw holes from the cental of the support circle\ petal is 7cm

for more info on the math, look at the code, or at [explanation.svg](explanation.svg)
