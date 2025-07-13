from obspy import read

st = read("waveforms/2016-08-15-1124-26M.arct__039")
for tr in st:
    print(f"Trace ID: {tr.id}")
    print(f"  Start time: {tr.stats.starttime}")
    print(f"  End time:   {tr.stats.endtime}")