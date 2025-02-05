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
            print('Data from "%s"' % (source))
            lap_times = []
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

if __name__ == "__main__": main()
