import subprocess
import time

from config import projects


def execute_command(command):
    pip = subprocess.Popen(command.strip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pip.stdout.readlines(), pip.stderr.readlines()


def parse_log(line):
    line = line.decode().strip()
    if line.startswith('Date:'):
        date = line.replace('Date:', '').strip()
        date = time.strptime(date, "%a %b %d %H:%M:%S %Y %z")
        return date
    elif len(line.split()) == 3:
        add, remove, file = line.split()
        if add.isnumeric() and remove.isnumeric():
            return line.split()


statistics = {}

for project, conf in projects.items():

    print('-' * 150)
    print('Start to analyse project [{}]'.format(project))


    command = 'cd {0} && git checkout {1} && git pull origin {1} && git log --author="{2}" --numstat'
    command = command.format(conf['path'], conf['branch'], conf['author'])
    stdout, stderr = execute_command(command)

    last_date = None
    for line in stdout:
        res = parse_log(line)
        if isinstance(res, list):
            add, remove, _ = line.split()
            statistics[last_date]['add'] = statistics[last_date].get('add', 0) + int(add)
            statistics[last_date]['remove'] = statistics[last_date].get('remove', 0) + int(remove)
        elif isinstance(res, time.struct_time):
            last_date = time.strftime("%Y-%m-%d", res)
            if last_date not in statistics:
                statistics[last_date] = {}
                statistics[last_date]['date'] = res
    print(stderr)

    # subprocess.Popen('cd {} && '.format(p['path']) + command.format(p['author']))
    print('-'*150 + '\n\n')

print(statistics)
total_add = 0
total_remove = 0
for k, v in statistics.items():
    total_add += v.get('add', 0)
    total_remove += v.get('remove', 0)
print('TOTAL ADD: {},  TOTAL REMOVE: {}'.format(total_add, total_remove))
