# Logread

A simple tool to read a continuously growing log file and export the data to a
Grafana dashboard using the Grada library.

Dependencies: https://github.com/christophberger/grada

Note that Grada needs Go 1.8.

Compilation: put logread.go into ~/go/src/logread, and `go build logread`

Usage: ./logread [options] inputfile

I recommend using a named pipe (created with mkfifo) for the communication
between the log generator and the log reader.


