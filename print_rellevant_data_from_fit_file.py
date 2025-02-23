from datetime import datetime, timezone, timedelta

import fit2human

import json
import sys
import os

def get_human_distance(distance):
    if distance > 1000: return '%d,%d Km' % (int(distance / 1000), int(distance % 1000))
    return '%d m' % (distance)

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

def get_datetime(string):
    return datetime.fromisoformat(string)

def get_local_datetime(reference):
    return reference.astimezone() if isinstance(reference, datetime) else get_datetime(reference).astimezone()

def print_kms(data):
    total_distance = 0
    for lap in data['lap_mesgs']: total_distance = total_distance + lap['total_distance']
    print("Total distance:\t\t%s\n" % (get_human_distance(total_distance)) )
    lap_times = []
    print("SPEED")
    for lap in data['lap_mesgs']:
        if lap['total_distance'] != 1000: break
        lap_times.append(lap['total_elapsed_time'])
    if len(lap_times) > 0:
        print()
        for (i, lap_time) in enumerate(lap_times):
            print('Km %d:\t\t\t%s' % (i + 1, get_human_time(lap_time)))
        total_time = 0
        print()
        for (i, lap_time) in enumerate(lap_times):
            if (i > 0) and (i % 5 == 0): print('Time per %02d Km:\t\t%s (%s/Km)' % (i, get_human_time(total_time), get_human_time(total_time / i)))
            total_time = total_time + lap_time
        print('\nTime per %d Km\t\t%s (%s/Km)\n' % (len(lap_times), get_human_time(total_time), get_human_time(total_time / len(lap_times))))
    else:
        print('Lap times aren\'t valids')

def print_hr(data):
    print("HEART RATE\n")
    for subdata in data['time_in_zone_mesgs']:
        if subdata['reference_mesg'] == 'session':
            total_time, hr_times, hr_limits = 0, [ 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0 ]
            for i in range(0, len(subdata['hr_zone_high_boundary'])):
                total_time = total_time + subdata['time_in_hr_zone'][i]
                j = max(0, min(i - 1, len(hr_times) - 1))
                hr_times[j] = hr_times[j] + subdata['time_in_hr_zone'][i]
                hr_limits[j] = subdata['hr_zone_high_boundary'][i]
            for i in range (0, len(hr_times)):
                hr_time = hr_times[i]
                print('Time in Zone %d (%s):%s\t\t%s (%.02f%%)' % (i + 1, get_hr_interval(hr_limits[i - 1] if i > 0 else 0, hr_limits[i] if i + 1 < len(hr_limits) else 0), '' if i > 0 and i + 1 < len(hr_limits) else '  ', get_human_time(hr_time), hr_time * 100 / total_time))
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
            begin_datetime = get_datetime(data['activity_mesgs'][0]['timestamp'])
            print('Data from "%s"\n' % (source))
            print('Begin datetime:\t\t%s' % (get_local_datetime(begin_datetime).strftime('%d-%m-%Y %H:%M')))
            print('End datetime:\t\t%s' % (get_local_datetime(begin_datetime + timedelta(seconds = int(data['activity_mesgs'][0]['total_timer_time']))).strftime('%d-%m-%Y %H:%M')))
            print('Time running:\t\t%s\n' % (get_human_time(data['activity_mesgs'][0]['total_timer_time'])))
            print_kms(data)
            print_hr(data)

if __name__ == "__main__": main()
