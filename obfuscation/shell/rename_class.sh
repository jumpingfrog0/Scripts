#!/bin/bash
#
# 批量重命名类名（修改类前缀）
#

######请修改以下配置#######

# mark: TODO
# 黑名单配置文件
# 使用json配置，脚本会过滤黑名单中的文件，dirs 表示目录，file 表示单个文件
cfg_blacklist_config="$(pwd)/config/rename_blacklist_config.txt"

# 需要忽略的目录，这个配置下的目录的文件不会修改源文件内容，目的是主要是忽略 Pods 下的第三方库，优化脚本速度
cfg_ignored_dirs_config="$(pwd)/config/rename_ignored_config.txt"

# 原前缀
old_class_prefix="ME"
# 新前缀
new_class_prefix="JF"

######请修改以上配置#######

# 导入工具脚本
. ./FileUtil.sh
. ./EnvCheckUtil.sh
. ./LogUtil.sh

# 声明一些变量
declare -a file_to_rename_array
declare -a class_to_rename_array
declare -a file_to_modify_content_array
declare -a blacklist_dirs
declare -a blacklist_files
declare -a ignored_dirs

current_path=`dirname $(pwd)`
output_file="${current_path}/scripts/output/files_to_rename"
output_class="${current_path}/scripts/output/class_to_rename"

# 递归遍历读取目录下的所有需要重命名的文件
function read_to_rename_file_recursively() {
	print_tip "递归遍历目录: $1" &>/dev/null
	if [[ -d $1 ]]; then
		for item in $(ls $1); do
			item_path="$1/${item}"
			if [[ -d $item_path ]]; then # 目录
                # 过滤黑名单中的目录
                if [[ -n $(echo "${blacklist_dirs[@]}" | grep -w ${item_path}) ]]; then
				    continue
                fi

                read_to_rename_file_recursively ${item_path}
			else 
				# 过滤非.h/.m文件
				if [[ -z $(echo "${item}" | egrep ".*\.(h|m)") ]]; then
                    continue
				fi

                # ${var%%.*} 该命令的使用是去掉变量var从右边算起的最后一个'.'字符及其右边的内容
                # 去除后缀
			    item_name=${item%%.*}

                #过滤没有前缀的文件
                if [[ -z $(echo "${item_name}" | grep "${old_class_prefix}") ]]; then
                    continue
                fi

                # 过滤黑名单中的文件
                if [[ -n $(echo "${blacklist_files[@]}" | grep ${item_name}) ]]; then
                    continue
                fi

                file_to_rename_array[$file_to_rename_count]=${item_path}
                class_to_rename_array[$file_to_rename_count]=${item_name}
                file_to_rename_count=$[ file_to_rename_count + 1 ];
			fi
		done
	else
		err "err:不是一个目录"
	fi
}

# 递归遍历读取目录下所有需要修改源代码的文件
function read_to_mofity_content_file_recursively() {
	print_tip "递归遍历目录: $1" &>/dev/null
	if [[ -d $1 ]]; then
		for item in $(ls $1); do
			item_path="$1/${item}"
			if [[ -d $item_path ]]; then # 目录
                # 过滤需要忽略的目录
                if [[ -n $(echo "${ignored_dirs[@]}" | grep -w ${item_path}) ]]; then
				    continue
                fi

                read_to_mofity_content_file_recursively ${item_path}
			else 
				# 过滤非.h/.m/.xcodeproj文件
				if [[ -z $(echo "${item}" | egrep ".*\.(h|m|pbxproj)") ]]; then
                    continue
				fi

                file_to_modify_content_array[$to_modify_content_count]=${item_path}
                to_modify_content_count=$[ to_modify_content_count + 1 ];
			fi
		done
	else
		err "err:不是一个目录"
	fi
}

# 读取忽略文件配置
function read_ignored_dirs_config() {
    check_file_exists_with_error_msg ${cfg_ignored_dirs_config} "忽略文件配置不存在:"

	print_tip "开始读取忽略文件配置..."

	cfg_line_count=0
	IFS_OLD=$IFS
	IFS=$'\n'

	for line in $(cat ${cfg_ignored_dirs_config})
	do
		print_info ${line}
		if [[ ${#line} -eq 0 ]]; then
			echo "blank line"
		else
			ignored_dirs[${cfg_line_count}]="${line}"
		fi
		cfg_line_count=$[ ${cfg_line_count} + 1 ]
	done
	IFS=${IFS_OLD}
	print_tip "读取忽略文件配置结束=="

    # echo "xxxxxxx ${ignored_dirs[@]}"
}

# 读取黑名单配置
function read_blacklist_config() {
    check_file_exists_with_msg ${cfg_blacklist_config} "检测到黑名单配置文件存在:" "配置文件不存在:"
	if [[ ! $? ]]; then
		exit 1
	fi

    print_tip "开始读取黑名单配置..."
    tmp_dirs=$(jq -r '.dirs[]' ${cfg_blacklist_config})
    blacklist_files=$(jq -r '.file[]' ${cfg_blacklist_config})

    index=0
    for row in ${tmp_dirs}
    do
        blacklist_dirs[${index}]="${current_path}/${row}"
        index=$[ ${index} + 1 ]
    done
    print_tip "读取黑名单配置结束=="
    
    echo "黑名单目录: ${blacklist_dirs[@]}"
    echo "黑名单文件: ${blacklist_files[@]}"
}

# 找到所有需要重命名的文件
function find_all_files_to_rename() {
    current_path=`dirname $(pwd)`
    file_to_rename_count=0
    read_to_rename_file_recursively ${current_path}

    # 去重
    class_to_rename_array=$(echo ${class_to_rename_array[@]} | sed 's/ /\n/g' | sort | uniq)

    # 清空临时文件
    rm -f ${output_file}
    rm -f ${output_class}

    for row in ${file_to_rename_array[@]}
    do
        # output_dir=
        # ${var%/*}
        echo "${row}" >> ${output_file}
        # echo "${a}"
    done

    for class_name in ${class_to_rename_array[@]}
    do
        echo "${class_name}" >> ${output_class}
    done
}

# # 找到所有需要替换处理的文件(包括.h, .m, .pbxproj)
# function find_all_files_to_modify_content() {
#     current_path=`dirname $(pwd)`
#     to_modify_content_count=0
#     read_to_mofity_content_file_recursively ${current_path}

#     for a in ${file_to_modify_content_array[@]}
#     do
#         echo "${a}" &>/dev/null
#     done
# }

# 批量替换源代码中的类名
function patch_replace_class_name() {
    for class_name in ${class_to_rename_array[@]}
    do
        new_class_name=$(echo ${class_name} | sed "s/^${old_class_prefix}/${new_class_prefix}/g")

        # 使用 grep 筛选出目标目录并过滤掉需要忽略的目录
        grep_command="grep ${class_name} ${current_path} -rl"
        for row in ${ignored_dirs[@]}
        do
            grep_command="${grep_command} --exclude-dir=${row}"
        done

        print_info "${grep_command}"

        # 批量替换
        sed -i "{
            s/${class_name}/${new_class_name}/g;
            }" $(${grep_command})

        echo "replacement: ${class_name} --> ${new_class_name}"
    done
}

function patch_rename_file() {
    for target_file in ${file_to_rename_array[@]}
    do
        file_name=$(basename ${target_file})
        new_file_name=$(echo ${file_name} | sed "s/^${old_class_prefix}/${new_class_prefix}/g")
        
        result_path="$(dirname ${target_file})/${new_file_name}"
        # echo "${result_path}"
        mv ${target_file} ${result_path}
    done
}

# 检测gun sed
gunSedInstallCheck

# 检测 jq
check_install_jq

# 读取黑名单配置
read_blacklist_config

# 读取忽略文件配置
read_ignored_dirs_config

# 找到所有需要重命名的文件
find_all_files_to_rename

# 找到所有需要替换处理的文件
# find_all_files_to_modify_content

# 批量替换源代码中的类名
patch_replace_class_name

# # 修改类源文件名
patch_rename_file