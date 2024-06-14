import re


def add_prefix_to_file(input_file, output_file):
    prefix = " 61726739 queried credit score"  # 前缀内容
    with open(input_file, 'r') as f_input:
        with open(output_file, 'w') as f_output:
            for line in f_input:
                split_string = line.split()[0]
                if '[' in split_string:
                    s = line.split()[1]
                    if (s != "OPEN") & (s != "CLOSE"):
                        a = split_string + prefix + "\n"
                        f_output.write(a + line)
                    else:
                        f_output.write(line)
                else:
                    f_output.write(line)


if __name__ == "__main__":
    input_file = "input.txt"  # 输入文件名
    output_file = "debug_out.txt"  # 输出文件名
    add_prefix_to_file(input_file, output_file)
    print("Prefix added to each line successfully!")
