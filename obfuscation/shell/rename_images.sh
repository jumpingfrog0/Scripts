#!/bin/bash
#
# 批量重命名资源图片
#

# 生成的图片名映射表的位置
output_path="$(pwd)/output"

grep_ignored_dirs=(
    Pods
    ME.xcodeproj
    MEModules/MEModules.xcodeproj
    FindYouBase/FindYouBase.xcodeproj
    MENotificationService
    Scripts
    XCConfig
    config
    ouput
)

# 脚本运行过程中的临时配置文件
tmp_config="$(pwd)/output/rename_images_tmp"

# 导入工具脚本
. ./FileUtil.sh
. ./EnvCheckUtil.sh
. ./LogUtil.sh

# 声明一些变量
declare -a old_image_name_array
declare -a new_image_name_array

current_path=`dirname $(pwd)`

# 生成图片名映射表
function generate_rename_images_map() {
    print_tip "开始生成图片名映射表..."

    assets=$(find ${current_path} -name "*.xcassets" -type d)

    # Fucking SPACE !!!!!
    # IFS_OLD=$IFS
	# IFS=$'\0'
    # assets=$(find ${current_path} -name "*.xcassets" -type d -print0)

    for row in ${assets}
    do
        print_tip "正在生成 ${row} 映射表"

        # 创建映射表文件
        filename=$(basename ${row} .xcassets)
        filename="rename_images_map_asset_${filename}.txt"
        output="${output_path}/${filename}"
        check_or_create_file ${output}

        echo -e "${row}\n" > ${output}
        echo -e "OLD_NAME\tNEW_NAME" >> ${output}
        echo -e "--------\t--------" >> ${output}

        echo "find ${row} -path \"${row}/AppIcon.appiconset\" -prune -o -name \"*.imageset\" -print"
        images=$(find ${row} -path "${row}/AppIcon.appiconset" -prune -o -name "*.imageset" -print)
        for image in ${images}
        do
            image_name=$(basename ${image} .imageset)

            # 去掉 @2x, @3x 后缀 
            # image_name=$(echo "${image_name}" | awk '{sub(/@(2|3)x/, ""); print}')

            echo -e "${image_name}\t${image_name}" >> ${output}
        done

        # 去重
        cat ${output} | awk '!a[$1]++{print}' > tmp && mv tmp ${output}

        # 对齐
        awk '{
            printf "%-50s%-50s\n", $1, $2
        }' ${output} > tmp && mv tmp ${output}
    done

    # IFS=${IFS_OLD}
}

# 读取图片名映射表
function read_rename_images_map() {
    file=$1
    check_file_exists_with_error_msg ${file} "图片名映射表不存在:"

    print_tip "正在读取图片名映射表 ${file} ..."

	IFS_OLD=$IFS
	IFS=$'\n'

    unset old_image_name_array
    unset new_image_name_array 
    old_image_name_array=($(awk 'NR > 4 {print $1}' ${file}))
    new_image_name_array=($(awk 'NR > 4 {print $2}' ${file}))

	IFS=${IFS_OLD}
}

# 批量重命名
function patch_rename_images() {
    map_files=$(find ${output_path} -name "rename_images_map_asset_*.txt")
    for row in ${map_files}
    do
        read_rename_images_map ${row}
        replace_image_name
        rename_image_file ${row}
    done
}

# 重命名 .imageset 和 png文件，以及 修改 Contents.json
function rename_image_file() {
    file=$1

    asset_path=$(awk 'NR==1 {print $0}' ${file})
    echo "正在重命名该目录下的文件: ${asset_path} ..."
        
    imagesets=$(find ${asset_path} -path "${asset_path}/AppIcon.appiconset" -prune -o -name "*.imageset" -print)
    for item in ${imagesets}
    do
        # 重命名 imageset
        imageset_name=$(basename ${item} .imageset)
        new_imageset_name=$(awk '$1 ~ /'$imageset_name'/ { print $2 }' ${file})
        # echo "aaa ${imageset_name}"
        # echo "ssss ${new_imageset_name}"

        if [[ ${imageset_name} = ${new_imageset_name} ]]; then
            continue
        fi
        if [[ -z ${imageset_name} || -z ${new_imageset_name} ]]; then
            continue
        fi

        new_imageset_path="$(dirname ${item})/${new_imageset_name}.imageset"
        # echo "rrr ${new_imageset_path}"
        mv ${item} ${new_imageset_path}

        # 重命名 png
        images_to_rename=$(find ${new_imageset_path} -name "*.png")
        for image in ${images_to_rename}
        do
            new_image="$(dirname ${image})/${new_imageset_name}"
            if [[ -n $(echo "${image}" | grep "@2x.png") ]]; then
                new_image="${new_image}@2x"
            elif [[ -n $(echo "${image}" | grep "3x.png") ]]; then
                new_image="${new_image}@3x"
            fi
            new_image="${new_image}.png"
            # echo "xxx ${new_image}"
            mv ${image} ${new_image}
        done

        # 修改 Contents.json ( 在 replace_image_name 这一步操作中会有遗漏)
        # target_file="${new_imageset_path}/a.txt"
        target_file="${new_imageset_path}/Contents.json"

        # @1x
	    first_line=$(awk 'BEGIN {
            line=-1
        }
        {
            ar[NR]=$0
            if ($0 ~ /\"scale\" : \"1x\"/) {
                if (match(ar[NR-1],/filename/)) {
                    line=NR-1
                }
            }
        }
        END { print line }' ${target_file})

        # @2x
        second_line=$(awk 'BEGIN {
            line=-1
        }
        {
            ar[NR]=$0
            if ($0 ~ /\"scale\" : \"2x\"/) {
                if (match(ar[NR-1],/filename/)) {
                    line=NR-1
                }
            }
        }
        END { print line }' ${target_file})

        # @3x
        third_line=$(awk 'BEGIN {
            line=-1
        }
        {
            ar[NR]=$0
            if ($0 ~ /\"scale\" : \"3x\"/) {
                if (match(ar[NR-1],/filename/)) {
                    line=NR-1
                }
            }
        }
        END { print line }' ${target_file})

        first_replacement="\      \"filename\" : \"${new_imageset_name}.png\","
        second_replacement="\      \"filename\" : \"${new_imageset_name}@2x.png\","
        third_replacement="\      \"filename\" : \"${new_imageset_name}@3x.png\","

        # @1x
        if [[ ${first_line} -gt -1 ]]; then
            sed -i "{
                ${first_line} c ${first_replacement}
            }" ${target_file}
        fi
        
        # @2x
        if [[ ${second_line} -gt -1 ]]; then
            sed -i "{
                ${second_line} c ${second_replacement}
            }" ${target_file}
        fi

        # @3x
        if [[ ${third_line} -gt -1 ]]; then
            sed -i "{
                ${third_line} c ${third_replacement}
            }" ${target_file}
        fi
        
        print_info "rename: ${imageset_name} --> ${new_imageset_name}"
    done
}

# 批量修改源代码中图片名的调用，如果 png 图片命名和 .imageset 命名不一致，则会有遗漏（遗漏的会在下一步操作中完成修改）
function replace_image_name() {
    echo "正在替换源代码中的图片名称..."
    for (( i=0; i<${#old_image_name_array[@]}; i++ ))
    do
        image_name=${old_image_name_array[$i]}
        new_image_name=${new_image_name_array[$i]}

        if [[ ${image_name} = ${new_image_name} ]]; then
            # echo "sssssssss ${image_name}"
            continue
        fi

        grep_command="grep ${image_name} ${current_path} -rl"
        for line in ${grep_ignored_dirs[@]}
        do
            grep_command="${grep_command} --exclude-dir=${line}"
        done

        # 忽略 .git 文件
        grep_command="${grep_command} --exclude-dir=.git"

        # echo "grep resutl ---- : $(${grep_command})"
        
        echo "${grep_command}"
        sed -i "{
            s/${image_name}/${new_image_name}/g;
        }" $(${grep_command})
        # sed -n "{
        #     s/${image_name}/${new_image_name}/g;
        #     p
        # }" $(${grep_command})

        print_info "succeed to replace: ${image_name} ---> ${new_image_name}"
    done
}

# 菜单
function gen_munu() {
	clear
	echo
    echo -e "该脚本的运行分为以下步骤：\n1) 选择选项1，脚本会自动遍历项目目录下的 .xcassets 文件夹的所有图片，在 \033[32m${output_path}\033[0m 目录下生成图片名映射表（以\033[32m rename_images_map_asset_*.txt \033[0m命名)"
    echo -e "2) 手动修改映射表中对应的图片的名字"
    echo -e "3) 选择选项3，进行图片重命名"
	echo -e "\n选项菜单:\n"
	echo -e "\t1. 生成图片名映射表"
	echo -e "\t2. 图片重命名"
	echo -e "\t0. Exit menu\n\n"
	echo -en "Enter option: "
	read -n 1 option
}

# 检测gun sed
gunSedInstallCheck

# 检测 jq
check_install_jq

while [[ 1 ]]; do
	gen_munu
	case $option in
	0 )
		echo ""
		echo "Bye"
		exit 0
	;;
	1 )
        generate_rename_images_map
	;;
	2 )
		patch_rename_images
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