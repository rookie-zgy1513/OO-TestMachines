from pathlib import Path
import json
import os
import subprocess
from DataGenerator import data_generator
from Checker import Library
import shutil
from datetime import date, timedelta, datetime
import re

config = json.load(open('config.json',encoding='utf-8'))
test_num = int(config['test_num'])
del_temp_file = config['del_temp_file']
jar_path = config['jar_path']

def file_load(file_path) -> list:
    """
    从指定路径加载txt文件的内容
    :param file_path: txt文件路径
    :return: 含有txt文件内容的一个列表(去除空行)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'文件{file_path}不存在')
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_output_to_file(file_path) -> None:
    """
    加载output.txt文件的内容到指定路径
    """
    path = Path(file_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    command = "type " + path.parent.__str__() + "\\input.txt" + " | java -jar " + jar_path + " > " + file_path
    subprocess.run(command, shell=True)
def process_function(case_id) -> str:
    library = Library()
    generator = data_generator(library)
    proc = subprocess.Popen(
        ['java','-jar', config['jar_path']],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    mkdir(f"workspace/{case_id}")
    f_in = open(f"workspace/{case_id}/input.txt", 'w', encoding='utf-8')
    f_out = open(f"workspace/{case_id}/output.txt", 'w', encoding='utf-8')

    try:
        for command in generator.init_command_list:
            f_in.write(command)
            proc.stdin.write(command)
            proc.stdin.flush()
        while True:
            input_command = generator.get_next_command()
            if input_command == "":
                break
            f_in.write(input_command)
            proc.stdin.write(input_command)
            proc.stdin.flush()
            output_command = []#proc.stdout.readline()
            output_command.append(proc.stdout.readline())
            try:
                if not('-' in output_command[0] or int(output_command[0])==0):
                    for i in range(0,int(output_command[0])):
                        output_command.append(proc.stdout.readline())
            except:
                return '未获取到正确的输出:'+output_command[0]
            for i in output_command:
                f_out.write(i)
                generator.add_command(i)
            if 'OPEN' in input_command:
                tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\].*', input_command)
                time = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
                library.update(False,time)
                if int(output_command[0])>0:
                    for i in range(1,output_command.__len__()):
                        result=library.orgnize(True,output_command[i])
                        if result!='':
                            return result
                result=library.open_check()
                if result!='':
                    return result
            elif 'CLOSE' in input_command:
                library.update(True, time)
                if int(output_command[0])>0:
                    for i in range(1,output_command.__len__()):
                        result=library.orgnize(False,output_command[i])
                        if result!='':
                            return result
            elif 'credit' in input_command:
                tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\] (\d{8}).*', input_command)
                personId = tmp_match.group(4)
                tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\] (\d{8}) (.*)', output_command[0])
                personId2 = tmp_match.group(4)
                if personId != personId2:
                    return '查询的学生id不匹配'
                credit = int(tmp_match.group(5))
                if library.persons[personId].credit != credit:
                    return '查询的学生的信用分应为 ' + str(library.persons[personId].credit)
            else:
                result=library.action(input_command,output_command[0])
                if result != '':
                    return result
        return "Accepted!"
    finally:
        proc.stdin.close()
        proc.stdout.close()
        proc.stderr.close()
        f_in.close()
        f_out.close()

def mkdir(path):
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    shutil.rmtree("workspace", ignore_errors=True)
    failed_list = []
    for i in range(test_num):
        result = process_function(i + 1)
        if del_temp_file and result == "Accepted!":
            shutil.rmtree(f"workspace/{i + 1}")
        elif result != "Accepted!":
            failed_list.append(i + 1)
        if result == "Accepted!":
            print("\033[36mCase {}: {}\033[0m".format(i + 1, "\033[32m" + str(result) + "\033[0m"))
        else:
            print("\033[36mCase {}: {}\033[0m".format(i + 1, "\033[31m" + str(result) + "\033[0m"))
    if failed_list:
        print("\033[31mFailed cases: {}\033[0m".format(failed_list))
    else:
        print("\033[32mAll cases passed!\033[0m")
    print("\033[35mTest finish time: " + str(datetime.now()) + "\033[0m")