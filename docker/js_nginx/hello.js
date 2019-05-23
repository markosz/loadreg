function hello(r) {
  var i;
  var sum = 0;
  for (i = 0; i < 15000; i++) {
    sum = sum+Math.sqrt(i);
  }
  r.return(200, "Hello world!");
}
