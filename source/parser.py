import pandas as pd
from IPython.display import display, HTML
from datetime import datetime
from datetime import timedelta
import subprocess
import re
from multiprocessing.dummy import Pool as ThreadPool

def run_command(command):
    print("Starting command: " + command)
    subprocess.run(command, shell=True)
    print("Finished command: " + command)

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def main():
    df = pd.read_csv('tcpdump.list', delim_whitespace=True)

    # Get unique attack names and display for our script purposes
    print('Available attacks names:\n')
    df_attacks = df[['attack_name']].drop_duplicates()
    display(df_attacks)

    # Get only port scans
    df2 = df#.loc[df['service'] == "telnet"]

    # Output this table into an html file.
    df2.to_html('filename.html')

    commands = []

    print("Generate commands to run...")
    for index, row in df2.iterrows():
        datetime_start = datetime.strptime(("%s %s") % (row['date'], row['time']), '%m/%d/%Y %H:%M:%S')
        duration = row['duration'].split(':')
        hours = int(duration[0])
        minutes = int(duration[1])
        seconds = int(duration[2])
        datetime_end = datetime_start + timedelta(hours=hours, minutes=minutes, seconds=seconds)

        #editcap -v  -A "1998-01-23 16:03:52" -B "1998-01-23 16:03:58"  sample_data01.tcpdump /dev/null
        file_name = "%s_%s.pcap" % (row['id'], row['attack_name'])
        file_name = get_valid_filename(file_name)
        command = ("editcap -A \"%s\" -B \"%s\"  sample_data01.tcpdump output/%s") % (datetime_start, datetime_end, file_name)

        #print(command)

        #print("'%s'" % datetime_start)
        commands.append(command)

    print("Starting Multithreaded Splitting...")
    pool = ThreadPool(8)

    # split datasets in their own threads
    # and return the results
    pool.starmap(run_command, zip(commands))

    # close the pool and wait for the work to finish
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()