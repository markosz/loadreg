package main

import (
    "bufio"
    "flag"
    "fmt"
    "os"
    "strconv"
    "strings"
    "time"

    "grada"
)

const usage = `Usage: logread [options] <input file>

Options:
  -b Buffer size for timeseries (default: %v)
  -i Idle time for reporting 0 in timeseries (default: %v, 0 means off)
  -p Listening port for Grada (default: 3001)
`
const (
    default_buffersize = 100
    default_idle = 3 * time.Second
)

var (
    buffersize = default_buffersize
    idletime = default_idle
)

func makeMetric(dash *grada.Dashboard, name string) chan float64 {
    metric, err := dash.CreateMetricWithBufSize(name, buffersize)
    if err != nil {
        fmt.Fprintf(os.Stderr, "could not create metric: %v\n", err)
        os.Exit(1)
    }
    ch := make(chan float64)

    go func() {
        if idletime >= 1*time.Second {
            tim := time.NewTimer(idletime)
            for {
                select {
                case <-tim.C:
                    //send 0 if no data was received for a while
                    metric.Add(0.0)
                case l := <-ch:
                    // restart timer
                    if !tim.Stop() {
                        // timer was expired, begin the new peak from 0
                        metric.Add(0.0)
                    }
                    tim.Reset(idletime)
                    metric.Add(l)
                }
            }

        } else {
            for {
                l := <-ch
                metric.Add(l)
            }
        }
    }()

    return ch
}

func main() {
    fmt.Printf("Logread\n")

    flag.Usage = func() {
        fmt.Fprint(os.Stderr, fmt.Sprintf(usage, default_buffersize, default_idle))
    }
    flb := flag.Int("b", default_buffersize, "")
    fli := flag.Duration("i", default_idle, "")
    flp := flag.Int("p", 0, "")

    flag.Parse()
    if flag.NArg() < 1 {
        flag.Usage()
        os.Exit(1)
    }

    buffersize = *flb
    idletime = *fli

    if *flp != 0 {
        fmt.Printf("Listening on non-default port %v\n", *flp)
        os.Setenv("GRADA_PORT", fmt.Sprintf("%d", *flp))
    }

    fname := flag.Args()[0]

    // create dashboard stuff
    dashb := grada.GetDashboard()

    // a sample metric for testing
    tlen := makeMetric(dashb, "Line lengths")

    // metrics from Markosz
    queries := makeMetric(dashb, "Queries")
    requests := makeMetric(dashb, "Requests")
    success := makeMetric(dashb, "Successrate")
    average := makeMetric(dashb, "Average latency")
    p50 := makeMetric(dashb, "P 50%")
    p95 := makeMetric(dashb, "P 95%")
    p99 := makeMetric(dashb, "P 99%")

    for {
        fmt.Printf("Opening input file %v\n", fname)

        f, err := os.Open(fname)
        if err != nil {
            fmt.Fprintf(os.Stderr, "Error: %v\n", err)
            os.Exit(1)
        }

        sc := bufio.NewScanner(f)

        for sc.Scan() {
            //fmt.Printf("Read line: %v\n", sc.Text())
            elems := strings.Split(sc.Text(), ";")
            if len(elems) == 8 {
                //fmt.Printf("split: %q", elems)
                equery, _   := strconv.ParseFloat(elems[0], 64)
                erequest, _ := strconv.ParseFloat(elems[1], 64)
                esucc, _    := strconv.ParseFloat(elems[2], 64)
                eavg, _     := strconv.ParseFloat(elems[3], 64)
                ep50, _     := strconv.ParseFloat(elems[4], 64)
                ep95, _     := strconv.ParseFloat(elems[5], 64)
                ep99, _     := strconv.ParseFloat(elems[6], 64)
                //eop, _      := elems[7]

                queries <- equery
                requests <- erequest
                success <- esucc
                average <- eavg
                p50 <- ep50
                p95 <- ep95
                p99 <- ep99
            } else {
                fmt.Printf("Cannot parse line: %v\n", sc.Text())
            }
            //fmt.Printf("%q\n", strings.Split("a man a plan a canal panama", "a "))
            tlen <- float64(len(sc.Text()))
        }

        fmt.Printf("End of input file, reopening\n")

        f.Close()
    }
}

