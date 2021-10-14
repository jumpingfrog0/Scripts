import os
import re


def get_all_image_name(file_dir, list_name, exclude_dir_list):
    for file in os.listdir(file_dir):
        if file in exclude_dir_list:
            continue
        file_path = os.path.join(file_dir, file)
        if os.path.isdir(file_path):
            if file_path.endswith('.appiconset'):
                continue
            elif file_path.endswith('.imageset'):
                image_name = file_path[file_path.rindex('/') + 1 : len(file_path) - len('.imageset')]
                if not image_name.startswith('{'):
                    list_name.append(image_name)
            else:
                get_all_image_name(file_path, list_name, exclude_dir_list)
        else:
            (tmp_path, file_name) = os.path.split(file_path)
            if '.png' in file_name:
                list_name.append(file_name.replace('@2x.png', '').replace('@3x.png', ''))


def get_dir_all_file_path(file_dir, list_path):
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if os.path.isdir(file_path):
            get_dir_all_file_path(file_path, list_path)
        else:
            (tmp_path, file_name) = os.path.split(file_path)
            if file_name.endswith('.m') or file_name.endswith('.mm') or file_name.endswith('.storyboard') or file_name.endswith('.xib'):
                list_path.append(file_path)


def get_maybe_image_name_string(file_dir, set_name, set_name_percent_sign, exclude_dir_list):
    rule = r'(@")([^,:\s]*?)"'
    rule2 = r'(image|image name)="([^,:\s]*?)"'
    os.chdir(file_dir)
    for dir_path in os.listdir(os.getcwd()):
        if dir_path in exclude_dir_list:
            continue
        if not os.path.isdir(dir_path):
            continue
        file_list = []
        get_dir_all_file_path(dir_path, file_list)
        for file_path in file_list:
            try:
                file = open(file_path, "r")
                file_lines = file.readlines()
                file.close()
                real_rule = rule
                if file_path.endswith('.storyboard') or file_path.endswith('.xib'):
                    real_rule = rule2
                for line in file_lines:
                    match_iter = re.finditer(real_rule, line)
                    for match in match_iter:
                        image_name = match.group(2)
                        if image_name.endswith('.png'):
                            image_name = image_name[0:len(image_name) - len('.png')]
                        if image_name.find('%') == -1:
                            set_name.add(image_name)
                        else:
                            set_name_percent_sign.add(image_name)
            except Exception as e:
                print(file_path + ":" + e.__str__())
            else:
                pass
            finally:
                pass


def find_unused_images(root_dir, exclude_dir_list):
    all_names = []
    get_all_image_name(root_dir, all_names, exclude_dir_list)
    print('All image count without YY face image', len(all_names))

    used_string = set()
    used_string_percent_sign = set()
    get_maybe_image_name_string(root_dir, used_string, used_string_percent_sign, exclude_dir_list)
    print('string without % count', len(used_string))
    print('string with % count', len(used_string_percent_sign))

    used_string_percent_sign_prefix = []
    for text in used_string_percent_sign:
        text = text[0:text.find('%')]
        if len(text) > 0:
            used_string_percent_sign_prefix.append(text)

    need_check_prefix_names = []
    for name in all_names:
        if name not in used_string:
            need_check_prefix_names.append(name)

    maybe_used_names = set()
    for name in need_check_prefix_names:
        for text in used_string_percent_sign_prefix:
            if name.startswith(text):
                maybe_used_names.add(name)

    maybe_used_names_list = []
    maybe_unused_names_list = []
    for name in need_check_prefix_names:
        if name in maybe_used_names:
            maybe_used_names_list.append(name)
        else:
            maybe_unused_names_list.append(name)

    print('maybe used image count', len(maybe_used_names_list))
    print('maybe used image names: ')
    sorted_maybe_used_names_list = sorted(maybe_used_names_list)
    for name in sorted_maybe_used_names_list:
        print('\t', name)

    print('maybe unused image count', len(maybe_unused_names_list))
    print('maybe unused image names: ')
    sorted_maybe_unused_names_list = sorted(maybe_unused_names_list)
    for name in sorted_maybe_unused_names_list:
        print('\t', name)


find_unused_images('../../', ['Pods', 'ThirdParty'])

