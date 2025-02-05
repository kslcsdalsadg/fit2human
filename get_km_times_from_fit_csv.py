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
                total_time = 0
                for (i, lap_time) in enumerate(lap_times):
                    print('KM %d:\t\t\t\t%s' % (i + 1, get_human_time(lap_time)))
                    total_time = total_time + lap_time
                print('\nAverage time per KM:\t\t%s\n' % (get_human_time(total_time / len(lap_times))))
                total_time = 0
                for (i, lap_time) in enumerate(lap_times):
                    if (i > 0) and (i % 5 == 0): print('Average time per %02d KMs:\t%s' % (i, get_human_time(total_time)))
                    total_time = total_time + lap_time
                print('\nTotal time per %d KMs\t\t%s\n' % (len(lap_times), get_human_time(total_time)))
            else:
                print('Lap times aren\'t valids')

if __name__ == "__main__": main()
