import os
import json
import subprocess


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception as err:
        print(err)
    return -1


def get_all_image_path_size(file_dir, dic_path_size, exclude_dir_list):
    for file in os.listdir(file_dir):
        if file in exclude_dir_list:
            continue
        file_path = os.path.join(file_dir, file)
        if os.path.isdir(file_path):
            get_all_image_path_size(file_path, dic_path_size, exclude_dir_list)
        elif file_path.endswith('.png'):
            dic_path_size[file_path] = get_file_size(file_path)


def write_html_begin(version):
    if not os.path.exists('./trackImageSize/'):
        os.mkdir('./trackImageSize/')
    html_file_path = './trackImageSize/trackImageSize%s.html' % version
    file = open(html_file_path, 'w+')
    file.write('<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    file.write('<head><title>trackImageSize</title></head><body>')
    return file


def write_html_end(file, version):
    html_file_path = './trackImageSize/trackImageSize%s.html' % version
    file.write('</body></html>')
    file.close()
    subprocess.call(['open', html_file_path])


def write_html_table(file, title, cell_list, color):
    file.write('<p></p>')
    file.write('<table border = "1"><tr style="background-color:%s"><td> %s </td><td> %s </td></tr>' % (color, title, 'byte'))
    for (key, value) in cell_list:
        file.write('<tr><td> %s </td><td> %d </td></tr>' % (key, value))
    file.write('</table>')


def write_html_table_begin(file):
    file.write('<p></p>')
    file.write('<table border = "1">')


def write_html_table_cell(file, title, content, color):
    file.write('<tr style="background-color:%s"><td> %s </td><td> %s </td></tr>' % (color, title, content))


def write_html_table_cell_list(file, cell_list):
    for (key, value) in cell_list:
        file.write('<tr><td> %s </td><td> %d </td></tr>' % (key, value))


def write_html_table_end(file):
    file.write('</table>')


def save_dic_to_json(dic, dic_type, dic_version):
    json_file_path = './trackImageSize/trackImageSize%s%s.json' % (dic_type, dic_version)
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(dic, f)


def get_dic_from_json(dic_type, dic_version):
    json_file_path = './trackImageSize/trackImageSize%s%s.json' % (dic_type, dic_version)
    if not os.path.exists(json_file_path):
        return {}
    with open(json_file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        res = json.loads(file_content)
        return res


def sort_to_list(dic):
    return sorted(dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)


def write_dic_to_html(file, title, cur_dic, pre_dic):
    add_dic = {}
    remove_dic = {}
    change_dic = {}
    if pre_dic is not None:
        for key, value in pre_dic.items():
            if key in cur_dic:
                if value != cur_dic[key]:
                    change_dic[key] = cur_dic[key] - value
            else:
                remove_dic[key] = value
        for key, value in cur_dic.items():
            if key not in pre_dic:
                add_dic[key] = value

    file.write('<p>%s</p>' % title)
    write_html_table_begin(file)
    write_html_table_cell(file, 'added', 'byte', 'rgb(255,100,83)')
    write_html_table_cell_list(file, sort_to_list(add_dic))
    write_html_table_cell(file, 'removed', 'byte', 'rgb(180,220,16)')
    write_html_table_cell_list(file, sort_to_list(remove_dic))
    write_html_table_cell(file, 'changed', 'byte', 'rgb(238,227,100)')
    write_html_table_cell_list(file, sort_to_list(change_dic))
    write_html_table_cell(file, 'current', 'byte', 'rgb(86,116,254)')
    write_html_table_cell_list(file, sort_to_list(cur_dic))
    write_html_table_end(file)


def get_dic_value_sum(path_size_list):
    size_sum = 0
    for (path, size) in path_size_list:
        size_sum = size_sum + size
    return size_sum


def do(root_dir, exclude_dir_list, cur_version, pre_version):
    if not os.path.exists('./trackImageSize/'):
        os.mkdir('./trackImageSize/')

    all_size_dic = {}
    get_all_image_path_size(root_dir, all_size_dic, exclude_dir_list)

    save_dic_to_json(all_size_dic, '', cur_version)
    pre_all_size_dic = get_dic_from_json('', pre_version)

    file = write_html_begin(cur_version)
    write_dic_to_html(file, 'object', all_size_dic, pre_all_size_dic)
    write_html_end(file, cur_version)


do('../../', ['Pods'], '4.29.0', '4.28.1')
