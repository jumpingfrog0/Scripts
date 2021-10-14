require('xcodeproj')

project_path = "#{__dir__}/../PikoCore/PikoCore.xcodeproj"
project_path = File.expand_path(project_path)
project = Xcodeproj::Project.open(project_path)
target = project.targets.first
group = project.main_group["PikoCore"]["proto"]

file_refs = Array.new
source_path = "#{__dir__}/../PikoCore/PikoCore/proto"
source_path = File.expand_path(source_path)
Dir.chdir(source_path)
Dir.each_child(source_path) do |child| 
    if File.file?(child) && group.find_file_by_path(child).nil? 
        file_ref = group.new_file(child)
        file_refs.push(file_ref)
    end
end

if file_refs.empty?
    puts "没有需要添加的文件"
    return
end

puts "添加以下文件"
puts file_refs.map { |ref| ref.display_name }

target.add_file_references(file_refs)
project.save