#!/bin/bash
#
# 在方法第一行注入垃圾代码
#

######请修改以下配置#######

# mark: TODO
# 注入内容的配置文件
cfg_injected_content="$(pwd)/config/injected_content_config.txt"

# 需要注入内容的目标目录
cfg_target_dirs="$(pwd)/config/injected_file_dirs_base.txt"

# 配置删除注入内容的目录
cfg_rm_dirs="$(pwd)/config/injected_remove_config.txt"

# 注入内容的前缀（用于删除操作）
cfg_rm_content_prefix="ME_LOG_NOTHING_";

######请修改以上配置#######

# 导入工具脚本
. ./FileUtil.sh
. ./EnvCheckUtil.sh
. ./LogUtil.sh

# 声明一些变量
declare -a dir_array
declare -a config_content_array
declare -a target_file_array
declare -a remove_dir_array

# 递归函数读取目录下的所有.m文件
function read_target_file_recursively {
	print_tip "递归遍历目录: $1"
	if [[ -d $1 ]]; then
		for item in $(ls $1); do
			itemPath="$1/${item}"
			if [[ -d $itemPath ]]; then
				# 目录
				print_tip "=====处理子目录: ${item_path}"
				read_target_file_recursively ${itemPath}
				print_tip "处理子目录结束====="
			else 
				# .m文件
				if [[ -n $(echo "${item}" | egrep ".*\.m") ]]; then
					# print_info "处理文件 ${item_path}"
					target_file_array[$target_file_count]=${itemPath}
					target_file_count=$[ target_file_count + 1 ];
				fi
				echo ""
			fi
		done
	else
		err "err:不是一个目录"
	fi
}

# 处理目标文件，添加配置文件中注入的内容
function process_to_inject_content {
	injected_content_index=0
	for(( i=0;i<${#target_file_array[@]};i++)) 
	do 
		file=${target_file_array[i]}; 
		print_tip "正在处理目标文件: ${file}"

		injected_content=${config_content_array[$injected_content_index]};
		injected_content_index=$[ $injected_content_index + 1 ]
		if [[ injected_content_index -ge ${#config_content_array[@]} ]]; then
			injected_content_index=0;
		fi
		print_info ">>>>>>> ${injected_content}  #${injected_content_index}"

		# mark: sed 命令中使用变量 http://blog.csdn.net/lepton126/article/details/36374933
		# 在匹配的行下面添加注入内容
		#sed -i '/^- \(.*\){$/{
		#	a\ '"$injected_content"'
		#}' ${file}

		sed -i '/^- \(.*\)/{
            :tag1;
            N;
            /{$/!b tag1;
            a\ '"$injected_content"'
        }' ${file}

		#sed -i '/^- \(.*\)/{
		#	:tag1;
 		#	N;
 		#	/{$/!b tag1;
 		#	a '"$injected_content"'
		#}' ${file}

	done;
}

# 处理目标文件，删除配置文件中注入的内容
function process_to_remove_content {
	for(( i=0;i<${#target_file_array[@]};i++)) 
	do 
		file=${target_file_array[i]}; 
		print_tip "正在处理目标文件：${file}"

		sed -i "/${cfg_rm_content_prefix}/d" ${file}
	done
}

# 检查配置文件
function check_inject_config_file() {
	check_file_exists_with_msg ${cfg_injected_content} "检测到配置文件存在:" "配置文件不存在:"
	if [[ ! $? ]]; then
		exit 1
	fi
}

# 读取配置文件的内容（需要处理的文件目录）
function read_config_file() {
	print_tip "开始读取目录配置..."
	cfg_dirs=$1
	dir_line_count=0
	for line in $(cat ${cfg_dirs})
	do
		print_info ${line}
		if [[ ${#line} -eq 0 ]]; then
			echo "blank line"
		else
			dir_array[${dir_line_count}]=${line}
		fi
		dir_line_count=$[ ${dir_line_count} + 1 ]
	done
	print_tip "读取目录配置结束=="
}

# 从配置文件读取需要注入的内容
function read_injected_content() {
	print_tip "开始读取需要注入的内容..."

	cfg_line_count=0
	IFS_OLD=$IFS
	IFS=$'\n'

	for line in $(cat ${cfg_injected_content})
	do
		print_info ${line}
		if [[ ${#line} -eq 0 ]]; then
			echo "blank line"
		else
			config_content_array[${cfg_line_count}]=${line}
		fi
		cfg_line_count=$[ ${cfg_line_count} + 1 ]
	done
	IFS=${IFS_OLD}
	print_tip "读取注入内容结束=="
}

# 批量注入内容
function patch_inject_content() {
	echo "${dir_array[@]}"
	for(( k=0;k<${#dir_array[@]};k++)) 
	do
		target_dir=${dir_array[$k]}
		current_path=`dirname $(pwd)`
		target_dir=${current_path}/${target_dir}
		echo ${target_dir}
		unset target_file_array
		target_file_count=0
		read_target_file_recursively ${target_dir}

		# # 添加配置文件中注入的内容
		process_to_inject_content
	done
	print_tip "内容添加完成"
}

# 批量删除内容
function patch_remove_content() {
	echo "${dir_array[@]}"
	for(( k=0;k<${#dir_array[@]};k++)) 
	do
		target_dir=${dir_array[$k]}
		current_path=`dirname $(pwd)`
		target_dir=${current_path}/${target_dir}
		echo ${target_dir}
		unset target_file_array
		target_file_count=0
		read_target_file_recursively ${target_dir}

		# 添加删除之前注入的内容
		process_to_remove_content
	done
	print_tip "内容删除完成"
} 

# 菜单
function gen_munu() {
	clear
	echo
	echo -e "\t\t\t选项菜单\n"
	echo -e "\t1. 删除注入内容"
	echo -e "\t2. 添加注入内容"
	echo -e "\t0. Exit menu\n\n"
	echo -en "\t\tEnter option: "
	read -n 1 option
}

function read_inject_config() {
	# 检查配置文件
	check_inject_config_file

	# 读取配置文件
	read_config_file ${cfg_target_dirs}

	# 读取需要注入的内容
	read_injected_content
}

function read_rm_config() {
	# 检查配置文件
	check_file_exists_with_msg ${cfg_rm_dirs} "检测到配置文件存在:" "配置文件不存在:"
	if [[ ! $? ]]; then
		exit 1
	fi	

	# 读取配置文件：需要删除的目录
	read_config_file ${cfg_rm_dirs}
}

function add_injected_content() {
	echo -e "\n"
	read_inject_config
	patch_inject_content
}

function remove_injected_content() {
	echo -e "\n"
	read_rm_config
	patch_remove_content
}

# 检测gun sed
gunSedInstallCheck

while [[ 1 ]]; do
	gen_munu
	case $option in
	0 )
		echo ""
		echo "Bye"
		exit 0
	;;
	1 )
		# 删除配置文件中注入的内容
		remove_injected_content
	;;
	2 )
		# 添加配置文件中注入的内容
		add_injected_content
	;;
	h )
		gen_munu
	;;
	* )
		echo "Wrong!!"
	;;
	esac

	echo
	echo -en "\n\n\tHit any key to continue"
	read -n 1 line

done

