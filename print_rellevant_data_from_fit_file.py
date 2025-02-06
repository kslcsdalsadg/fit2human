import fit2human

import json
import sys
import os

def get_human_time(time):
    if time > 60 * 60:
        hours = int(time / (60 * 60))
        time = time % (60 * 60)
        return '%d:%02d:%02d' % (hours, int(time / 60), int(time % 60))
    return '%d:%02d' % (int(time / 60), int(time % 60))

def get_hr_interval(min, max):
    if min == 0: return 'HR less than %d bpm' % (max)
    if max == 0: return 'HR higher to %d bpm' % (min)
    return 'HR from %d to %d bpm' % (min, max)


def print_kms(data):
    lap_times = []
    print("SPEED\n")
    for lap in data['lap_mesgs']:
        if lap['total_distance'] != 1000:
            break
        else:
            lap_times.append(lap['total_elapsed_time'])
    if len(lap_times) >= len(data['lap_mesgs']) - 1:
        print()
        for (i, lap_time) in enumerate(lap_times):
            print('KM %d:\t\t\t\t%s' % (i + 1, get_human_time(lap_time)))
        total_time = 0
        print()
        for (i, lap_time) in enumerate(lap_times):
            if (i > 0) and (i % 5 == 0): print('Time per %02d KMs:\t\t%s (%s per KM)' % (i, get_human_time(total_time), get_human_time(total_time / i)))
            total_time = total_time + lap_time
        print('\nTime per %d KMs\t\t\t%s (%s per KM)\n' % (len(lap_times), get_human_time(total_time), get_human_time(total_time / len(lap_times))))
    else:
        print('Lap times aren\'t valids')

def print_hr(data):
    print("HEART RATE\n")
    for subdata in data['time_in_zone_mesgs']:
        if subdata['reference_mesg'] == 'session':
            total_time, hr_times, hr_limits = 0, [ 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0 ]
            for i in range(0, len(subdata['hr_zone_high_boundary'])):
                total_time = total_time + subdata['time_in_hr_zone'][i]
                j = i if i < len(hr_times) else len(hr_times -1)
                hr_times[j] = hr_times[j] + subdata['time_in_hr_zone'][i]
                hr_limits[j] = subdata['hr_zone_high_boundary'][i]
            for (i, hr_time) in enumerate(hr_times):
                print('Time in Zone %d (%s):%s\t\t%s (%.02f%%)' % (i, get_hr_interval(hr_limits[i - 1] if i > 0 else 0, hr_limits[i] if i + 1 < len(hr_limits) else 0), '' if i > 0 and i + 1 < len(hr_limits) else '  ', get_human_time(hr_time), hr_time * 100 / total_time))
            return
    print('HR times aren\'t valids')


def main():
    if len(sys.argv) < 2:
        print('No input file received')
    else:
        source = sys.argv[1]
        data = None
        if os.path.splitext(source)[1] == '.fit':
            data = fit2human.main(source, 'json')
            if not data: print('Cannot load json data')
            else: data = json.loads(data)
        else:
            with open(source) as json_file: data = json.load(json_file)
        if data:
            print('Data from "%s"\n' % (source))
            print_kms(data)
            print_hr(data)

if __name__ == "__main__": main()
