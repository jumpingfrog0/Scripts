#!/bin/sh

# 脚本需要在Copy Bundle Resources之前执行
# 这个脚本对AppIcon进行修改，添加版本信息、build版本信息和build config到icon中
# warning ！！！！！ 对该脚本进行修改时，请保证在外发包构建时不执行  warning ！！！！！

# ———————————————————————————————————————— 检测是否执行脚本 ————————————————————————————————————————
#if [[ ${BUILD_DISPLAY_NAME} == "" ]]; then
#	# BUILD_DISPLAY_NAME是构建系统的环境变量，该判断保证脚本只在构建系统上运行
#	exit 0;
#fi

if [[ ${PRODUCT_BUNDLE_IDENTIFIER} == "com.piko.gvoice" ]]; then
	# BUNDLE_IDENTIFIER为外发包，不执行
	echo "外发版本不执行icon替换"
	exit 0;
fi
# ———————————————————————————————————————— 检测是否执行脚本 ————————————————————————————————————————

# ———————————————————————————————————————— 检测安装执行环境 ————————————————————————————————————————
# 检测homebrew是否安装，没安装则结束
if which brew 2>/dev/null; then
  echo "homebrew exists!"
else
  echo "nope, no brew installed."
  exit 0;
fi

# 检测是否已安装imagemagick & ghostscript，没有则先安装
convertPath=`which convert`
echo ${convertPath}
if [[ ! -f ${convertPath} || -z ${convertPath} ]]; then 
	# echo "warning: Skipping Icon versioning, you need to install ImageMagick and ghostscript (fonts) first, you can use brew to simplify process:
	# brew install imagemagick
	# brew install ghostscript"
	# exit -1;
	# 安装imagemagick & ghostscript
	brew install imagemagick
	brew install ghostscript
fi
# ———————————————————————————————————————— 检测安装执行环境 ————————————————————————————————————————

ASSETS_NAME="Images.xcassets"
ICON_ORIGINAL_PATH="${PROJECT_DIR}/${PROJECT_NAME}/${ASSETS_NAME}/AppIcon.appiconset"

# 说明
# version    app-版本号
# build_num  app-构建版本号
# build_config Debug/Release/Distribute
version=`/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" "${INFOPLIST_FILE}"`
build_num=`/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "${INFOPLIST_FILE}"`
build_config=${CONFIGURATION}

shopt -s extglob
build_num="${build_num##*( )}"
shopt -u extglob
caption="#$build_num\nv${version}"
echo $caption

function processIcon() { 
	base_file=$1
	temp_path=$2 
	dest_path=$3 
	if [[ ! -e $base_file ]]; then 
		echo "error: file does not exist: ${base_file}" 
		exit -1; 
	fi 
	if [[ -z $temp_path ]]; then 
		echo "error: temp_path does not exist: ${temp_path}" 
		exit -1; 
	fi 
	if [[ -z $dest_path ]]; then 
		echo "error: dest_path does not exist: ${dest_path}" 
		exit -1; 
	fi 
	file_name=$(basename "$base_file") 
	final_file_path="${dest_path}/${file_name}" 
	base_tmp_normalizedFileName="${file_name%.*}-normalized.${file_name##*.}" 
	base_tmp_normalizedFilePath="${temp_path}/${base_tmp_normalizedFileName}" 
	# Normalize 
	echo "Reverting optimized PNG to normal" 
	echo "xcrun -sdk iphoneos pngcrush -revert-iphone-optimizations -q '${base_file}' '${base_tmp_normalizedFilePath}'" 
	xcrun -sdk iphoneos pngcrush -revert-iphone-optimizations -q "${base_file}" "${base_tmp_normalizedFilePath}" 
	width=`identify -format %w "${base_tmp_normalizedFilePath}"` 
	height=`identify -format %h "${base_tmp_normalizedFilePath}"` 
	band_height=$((($height * 32) / 100)) 
	band_position=$(($height - $band_height)) 
	text_position=$(($band_position)) 
	config_position=$((($height * 5) / 100))
	point_size=$(((13 * $width) / 100)) 
	config_size=$(((18 * $width) / 100))
	echo "Image dimensions ($width x $height) - band height $band_height @ $band_position - point size $point_size" 
	# 
	# text 
	# 
	convert -size ${width}x${band_height} xc:none -fill 'rgba(238,130,238,1)' -draw "rectangle 0,0,$width,$band_height" /tmp/labels-base.png
	convert -background none -size ${width}x${band_height} -pointsize $point_size -fill black -gravity center -gravity South caption:"$caption" /tmp/labels.png
    ## 暂时不显示构建环境是Debug/Release/Distribute
	#convert -background none -size ${width}x${band_height} -pointsize $config_size -fill 'rgba(0,0,0,1)' -gravity center -gravity North caption:"$build_config" /tmp/config.png
	# 
	# compose final image 
	# 
	filename=New"${base_file}" 
	#convert "${base_tmp_normalizedFilePath}" /tmp/labels-base.png -geometry +0+$band_position -composite /tmp/config.png -geometry +0+$config_position -composite /tmp/labels.png -geometry +0+$band_position -geometry +${w}-${h} -composite -alpha remove "${final_file_path}"
 convert "${base_tmp_normalizedFilePath}" /tmp/labels-base.png -geometry +0+$band_position -composite /tmp/labels.png -geometry +0+$band_position -geometry +${w}-${h} -composite -alpha remove "${final_file_path}"
	# clean up 
	rm /tmp/labels-base.png 
	rm /tmp/labels.png 
	#rm /tmp/config.png
	rm "${base_tmp_normalizedFilePath}" 
	echo "Overlayed ${final_file_path}"
}
# Process all app icons
icons_set=`basename "${ICON_ORIGINAL_PATH}"`
tmp_path="${TEMP_DIR}/IconVersioning"
echo "ICON_ORIGINAL_PATH: ${ICON_ORIGINAL_PATH}"
mkdir -p "${tmp_path}"

# Reference: https://askubuntu.com/a/343753
find "${ICON_ORIGINAL_PATH}" -type f -name "*.png" -print0 |
while IFS= read -r -d '' file; do 
	echo "$file" 
	processIcon "${file}" "${tmp_path}" "${ICON_ORIGINAL_PATH}"
done


