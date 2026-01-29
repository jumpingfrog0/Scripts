#!/bin/bash
#
# 删除垃圾代码
#

# mark: 运行脚本之前，请修改配置文件、垃圾引用配置和垃圾属性的个数

# 需要删除垃圾代码的配置，need to modify
config_file="$(pwd)/config/del_garbage_config.txt"

# 配置引用的垃圾代码的目录, need to modify
config_ref="$(pwd)/config/del_garbage_cfg_ref.txt"

# 垃圾属性的个数, need to modify
garbage_property_count=2

# 导入工具脚本
. ./FileUtil.sh
. ./EnvCheckUtil.sh
. ./LogUtil.sh

# 声明一些变量
declare -a dir_array
declare -a ref_array
declare -a target_file_array
declare -a garbage_refs
target_file=""

# 读取配置目录
function read_target_dirs() {
	dir_line_count=0

	print_tip "读取配置的目录："
	for line in $(cat ${config_file})
	do
		print_info ${line}
		if [[ ${#line} -eq 0 ]]; then
			err "blank line"
		else
			dir_array[${dir_line_count}]=${line}
		fi
		dir_line_count=$[ ${dir_line_count} + 1 ]
	done
	print_tip "读取配置目录结束"
}

# 读取垃圾引用配置
function read_ref_config() {
	ref_line_count=0

	print_tip "读取垃圾引用配置："
	for line in $(cat ${config_ref})
	do
		print_info ${line}
		if [[ ${#line} -eq 0 ]]; then
			err "blank line"
		else
			ref_array[${ref_line_count}]=${line}
		fi
		ref_line_count=$[ ${ref_line_count} + 1 ]
	done
	print_tip "读取垃圾引用配置结束"
}

# 读取垃圾引用文件
function read_ref_files() {
	print_tip "读取所有的垃圾引用文件类名"
	ref_count=0
	for(( f=0;f<${#ref_array[@]};f++ )); do
		current_path=`dirname $(pwd)`
		target=${current_path}/${ref_array[$f]}
		for item in $(ls ${target}); do
			# ${var%%.*} 该命令的使用是去掉变量var从右边算起的最后一个'.'字符及其右边的内容
			ref_name=${item%%.*}
			garbage_refs[ref_count]=${ref_name}
			ref_count=$[ ref_count + 1]
		done
	done

	echo "${garbage_refs[@]}"
}

# 递归遍历读取目录下的所有.h和.m文件
function read_target_file_recursively() {
	print_tip "递归遍历目录: $1"
	if [[ -d $1 ]]; then
		for item in $(ls $1); do
			item_path="$1/${item}"
			if [[ -d $item_path ]]; then
				# 目录
				print_tip "=====处理子目录: ${item_path}"
				read_target_file_recursively $item_path
				print_tip "处理子目录结束====="
			else 
				# .m文件
				if [[ -n $(echo "${item}" | egrep ".*\.(h|m)") ]]; then
					# print_info "处理文件 ${item_path}"
					target_file_array[$target_file_count]=${item_path}
					target_file_count=$[ target_file_count + 1 ];
				fi
			fi
		done
	else
		err "err:不是一个目录"
	fi
	print_tip "递归遍历目录结束"
}

# 判断当前文件是否有垃圾代码
# 如果文件中有 `+ (void)instanceFactory` 这个方法，就认定当前文件有垃圾代码
function check_exist_garbage_code() {
	garbage_code=$(awk '/\+ \(void\)instanceFactory/ { print $0 }' ${target_file})
	if [[ -z "${garbage_code}" ]]; then
		echo "不存在垃圾代码: ${target_file}"
		return 0
	fi
	return 1
}

# 删除垃圾代码的引用
function remove_garbage_refs {
	for(( j=0;j<${#garbage_refs[@]};j++))
	do
		regex=${garbage_refs[$j]}
		# sed -n "/#import \"${regex}.h\"/p" ${target_file}
		sed -i "/#import \"${regex}.h\"/d" ${target_file}
	done
}

# 删除头文件中声明的@class
function remove_garbage_@class {
	for(( j=0;j<${#garbage_refs[@]};j++))
	do
		regex=${garbage_refs[$j]}
		# sed -n "/@class ${regex}/p" ${target_file}
		sed -i "/@class ${regex}/d" ${target_file}
	done	
}

# 获取第一行垃圾代码的位置
function get_garbage_method_first_line() {
	first_line_num=$(
	awk 'BEGIN {
			first_num = -1
			i = 0;
		}

		# 正则，匹配`me_`开头或者`instanceFactory`方法
		/^\- \(.*\)me_.*/ || \
		/^\+ \(.*\)me_.*/ || \
		/\+ \(void\)instanceFactory/ {
			if (i == 0) {
				# 第一行的位置
				first_num = NR
			}
			i++
			#print NR, $0
		}

		END {
			print first_num
		}' ${target_file}
	)
}

# 获取最后一行垃圾代码的位置
function get_garbage_method_last_line() {
	last_line_num=$(
	awk 'BEGIN {
			last_num = -1
		}

		# 正则，匹配 `}`
		/\}/ {
			# 最后一个右大括号的位置
			last_num = NR
		}

		END {
			print last_num
		}' ${target_file}
	)
}

# 删除垃圾函数
function remove_garbage_methods() {
	# 因为垃圾代码是连续的，首先先找到第一行垃圾代码
	get_garbage_method_first_line
	get_garbage_method_last_line

	echo "first_line = ${first_line_num}"
	echo "last_line = ${last_line_num}"

	# 删除
	if [[ ${first_line_num} != -1 && ${last_line_num} != -1 ]]; then
		# sed -n "${first_line_num},${last_line_num}p" ${target_file}
		sed -i "${first_line_num},${last_line_num}d" ${target_file}
	fi
}

# # 删除头文件中的垃圾代码
function remove_garbage_code_in_header() {
	get_garbage_method_first_line

	last_line_num=$(
	awk 'BEGIN {
			last_num = -1
		}

		# 正则，匹配 `instanceFactory` 方法
		/\+ \(void\)instanceFactory/ {
			last_num = NR
		}

		END {
			print last_num
		}' ${target_file}
	)

	# 删除头文件中声明的方法和属性
	if [[ ${first_line_num} != -1 && ${last_line_num} != -1 ]]; then
		# 头文件中的声明的垃圾方法上面有一行空行和2个垃圾属性，也一并删除了
		first_line_num=$(expr ${first_line_num} - ${garbage_property_count} - 1)
		# sed -n "${first_line_num},${last_line_num}p" ${target_file}
		sed -i "${first_line_num},${last_line_num}d" ${target_file}
	fi

	# 删除声明的@class
	remove_garbage_@class
}

# 删除所有的垃圾代码
function remove_all_garbage_code() {
	for(( i=0;i<${#target_file_array[@]};i++))
	do
		target_file=${target_file_array[$i]}

		print_info "-----处理文件 ${target_file}"

		# 检查文件是否存在
		check_exist_file ${target_file}

		# 判断当前文件是否有垃圾代码
		check_exist_garbage_code
		if [[ $? -eq 1 ]]; then
			if [[ -n $(echo "${target_file}" | egrep ".*\.h") ]]; then
				# .h 文件
				remove_garbage_code_in_header
			else
				# .m文件
				remove_garbage_methods
				remove_garbage_refs
			fi
		fi
	done
}

function patch_deal_files() {
	# 批量处理目标文件
	for(( k=0;k<${#dir_array[@]};k++)) 
	do
		target_dir=${dir_array[$k]}
		current_path=`dirname $(pwd)`
		target_dir=${current_path}/${target_dir}
		echo "开始处理目录: ${target_dir}"
		unset target_file_array
		target_file_count=0
		read_target_file_recursively ${target_dir}

		# 删除垃圾代码
		remove_all_garbage_code
	done
}

function patch_remove_ref_files() {
	print_tip "开始删除垃圾引用文件"
	for(( f=0;f<${#ref_array[@]};f++ )); do
		current_path=`dirname $(pwd)`
		to_del=${current_path}/${ref_array[$f]}

		if [[ ${to_del} = "/" ]]; then
			err "ERROR!!!!!"
		elif [[ ${to_del} = ${current_path} ]]; then
			err "ERROR 222!!!!!"
		elif [[ -z ${to_del} ]]; then
			err "ERROR 333!!!!!"
		else
			print_tip "删除目录：${to_del}"
			rm -rf ${to_del}
		fi
	done	
}

# 检测gun sed
gunSedInstallCheck

# 读取需要处理的文件
read_target_dirs

# 读取垃圾引用配置和文件
read_ref_config
read_ref_files

# 批量处理目标文件
patch_deal_files

# 批量删除垃圾引用文件
patch_remove_ref_files






# sed -e '1,${
# 	/instanceF/d; 
# 	/JFLaunchTimeCostReport/d
# 		}' ${target_file}

# sed -n '1,${
# 	:label;
# 	N;
# 	$!b label;
# 	/^\+ \(.*\)me_.*\}/p
# 	}' ${target_file}

# sed -n '1,${
# 	:label;
#  	N;
#  	$!b label;
# 	/^\+ \(.*\)\w+\n\{\n\t\w+./p;
# 	/^\- \(.*\)me_.*/p;
# 	}' ${target_file}

# sed -i '/^- \(.*\)/{
#             :tag1;
#             N;
#             /{$/!b tag1;
#             a\ '"$injected_content"'
#         }' ${file}