C=10 
for i in {2..6} 
do
  Q=$((10 * $i))
  fname=fix-c$C-q$Q.csv
  ./load_control.sh $C $Q f > $fname
  gnuplot -p -e "f='$fname'" gplot.gp
done
