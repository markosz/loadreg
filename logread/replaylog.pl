#!/usr/bin/perl
# replay the data log for testing logreader
use strict;
use warnings;

use Time::HiRes qw(usleep);

# perl -le 'print join ";", 1000, 480+int(rand 20), int(rand 100), rand, rand, rand, rand, "_" x int(1+rand 20) for 0..1000' >sample_data.csv

$| = 1; # autoflush stdout

my $fname = shift || die "No input file given\n";

open (my $F, $fname) || die "Cannot open input file '$fname': $!\n";

while (my $l = <$F>) {
    print $l;
    usleep(1000000*(1.9+rand 0.4));
}
