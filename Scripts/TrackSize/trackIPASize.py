import os
import json
import subprocess
import urllib.request
import zipfile
import shutil


def download_callback(block_num, block_size, total_size):
    all_size = total_size / block_size
    ten_percent = all_size / 10
    ten_percent_int = int(ten_percent)
    if block_num % ten_percent_int == 0:
        percent = int(block_num / ten_percent_int) * 10
        print('download %d%%' % percent)


def download_file(file_path, file_name):
    urllib.request.urlretrieve(file_path, file_name, download_callback)


def unzip_file(file_path, target_path):
    file = zipfile.ZipFile(file_path, 'r')
    file.extractall(target_path)


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception as err:
        print(err)
    return -1


def get_dir_size(dir_path):
    size = 0
    for root, dirs, files in os.walk(dir_path):
        size += sum([get_file_size(os.path.join(root, name)) for name in files])
    return size


def get_all_path_size(file_dir, dic_path_size, exclude_dir_list):
    for file in os.listdir(file_dir):
        file_decode = file
        try:
            file_decode = file.encode('cp437').decode('utf-8')
        except:
            file_decode = file.encode('utf-8').decode('utf-8')
        if file_decode in exclude_dir_list:
            continue
        file_path = os.path.join(file_dir, file)
        if os.path.isdir(file_path):
            dic_path_size[file_decode] = get_dir_size(file_path)
        else:
            dic_path_size[file_decode] = get_file_size(file_path)


def write_html_begin(version):
    if not os.path.exists('./trackIPASize/'):
        os.mkdir('./trackIPASize/')
    html_file_path = './trackIPASize/trackIPASize%s.html' % version
    file = open(html_file_path, 'w+', encoding='utf-8')
    file.write('<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    file.write('<head><title>trackIPASize</title></head><body>')
    return file


def write_html_end(file, version):
    html_file_path = './trackIPASize/trackIPASize%s.html' % version
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
    json_file_path = './trackIPASize/trackIPASize%s%s.json' % (dic_type, dic_version)
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(dic, f)


def get_dic_from_json(dic_type, dic_version):
    json_file_path = './trackIPASize/trackIPASize%s%s.json' % (dic_type, dic_version)
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


def do(app_name, file_url, exclude_dir_list, cur_version, pre_version):
    if not os.path.exists('./trackIPASize/'):
        os.mkdir('./trackIPASize/')

    ipa_file_path = './trackIPASize/trackIPASize%s.ipa' % cur_version
    unzip_file_path = './trackIPASize/trackIPASize%s' % cur_version
    target_file_path = './trackIPASize/trackIPASize%s/Payload/%s.app' % (cur_version, app_name)

    download_file(file_url, ipa_file_path)
    unzip_file(ipa_file_path, unzip_file_path)

    all_size_dic = {}
    get_all_path_size(target_file_path, all_size_dic, exclude_dir_list)

    save_dic_to_json(all_size_dic, '', cur_version)
    pre_all_size_dic = get_dic_from_json('', pre_version)

    file = write_html_begin(cur_version)
    write_dic_to_html(file, 'object', all_size_dic, pre_all_size_dic)
    write_html_end(file, cur_version)

    os.remove(ipa_file_path)
    shutil.rmtree(unzip_file_path)


do('QingYu',
   'http://repo.yy.com/dwbuild/mobile/ios/xunyin/XUNYIN-IOS_4.29.0_REVIEW2/20201116-125-rdd451c5781d9029030775b5ba08d019ecf7ae004/xunyin.ipa',
   [], '4.29.0', '4.28.1')
