set term x11

set yrange [0:5]

if (!exists("f")) f='f.csv'
set title f

set datafile separator ";"
u=100 #upscale factor
d=1000 #downsclae factor
plot f u ($1/d) w linespoints title 'QPS', f u ($2/d) w linespoints title 'RPS', f u ($4*u) w linespoints title 'AVG', f u ($5*u) w linespoints title 'P50', f u ($6*u) w linespoints title 'P95'

set term png
set output f . ".png"
replot
