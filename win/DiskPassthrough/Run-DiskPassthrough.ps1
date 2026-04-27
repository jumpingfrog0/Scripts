# Run-DiskPassthrough.ps1
# 功能：一键将物理硬盘直通挂载到Hyper-V虚拟机
# 使用方法：修改下面的 $VMName 和 $DiskNumber 变量，然后运行脚本

param(
    [switch]$Interactive = $false  # 添加一个交互模式开关
)

# ============ 在这里修改配置 ============
$VMName = "NasServer"    # 修改为你的虚拟机名称
$DiskNumber = 0               # 修改为你要直通的磁盘编号
# =======================================

# 显示脚本信息
Write-Host "=== Hyper-V 物理硬盘直通一键脚本 ===" -ForegroundColor Green
Write-Host "当前配置：虚拟机: $VMName, 磁盘编号: $DiskNumber" -ForegroundColor Yellow
Write-Host ""

# 交互模式：如果启用交互模式或者配置为空，提示用户输入
if ($Interactive -or $VMName -eq "你的虚拟机名称" -or -not $VMName) {
    Write-Host "进入交互模式..." -ForegroundColor Cyan
    $VMName = Read-Host "请输入虚拟机名称"
    $DiskNumber = Read-Host "请输入要直通的磁盘编号"
}

# 验证管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell 选择'以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

# 验证虚拟机是否存在
if (-not (Get-VM -Name $VMName -ErrorAction SilentlyContinue)) {
    Write-Host "错误：虚拟机 '$VMName' 不存在！" -ForegroundColor Red
    Write-Host "可用的虚拟机列表：" -ForegroundColor Yellow
    Get-VM | Format-Table Name, State, Status -AutoSize
    pause
    exit 1
}

# 验证磁盘是否存在
if (-not (Get-Disk -Number $DiskNumber -ErrorAction SilentlyContinue)) {
    Write-Host "错误：磁盘编号 $DiskNumber 不存在！" -ForegroundColor Red
    Write-Host "可用的物理磁盘列表：" -ForegroundColor Yellow
    Get-Disk | Where-Object {$_.BusType -ne 'Microsoft Reserved'} | Format-Table Number, FriendlyName, Size, OperationalStatus -AutoSize
    pause
    exit 1
}

# 显示磁盘信息
$diskInfo = Get-Disk -Number $DiskNumber
Write-Host "`n操作确认：" -ForegroundColor Red
Write-Host "虚拟机: $VMName" -ForegroundColor White
Write-Host "磁盘: $($diskInfo.FriendlyName)" -ForegroundColor White
Write-Host "编号: $DiskNumber" -ForegroundColor White
Write-Host "大小: $([math]::Round($diskInfo.Size/1GB,2)) GB" -ForegroundColor White
Write-Host "当前状态: $($diskInfo.OperationalStatus)" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "确认要将此磁盘直通挂载到虚拟机？(y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "操作已取消。" -ForegroundColor Yellow
    pause
    exit 0
}

# 执行操作
try {
    Write-Host "`n开始执行操作..." -ForegroundColor Green
    
    # 设置磁盘离线
    Write-Host "1. 设置磁盘 $DiskNumber 离线..." -ForegroundColor Cyan
    Set-Disk -Number $DiskNumber -IsOffline $true
    
    # 添加直通磁盘到虚拟机
    Write-Host "2. 添加磁盘到虚拟机 $VMName..." -ForegroundColor Cyan
    Add-VMHardDiskDrive -VMName $VMName -DiskNumber $DiskNumber
    
    Write-Host "`n✅ 操作成功完成！" -ForegroundColor Green
    Write-Host "磁盘已成功直通挂载到虚拟机 $VMName" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ 操作失败：$($_.Exception.Message)" -ForegroundColor Red
    
    # 尝试恢复磁盘状态
    try {
        Set-Disk -Number $DiskNumber -IsOffline $false
        Write-Host "已恢复磁盘在线状态" -ForegroundColor Yellow
    } catch {
        Write-Host "警告：无法恢复磁盘在线状态" -ForegroundColor Red
    }
    
    pause
    exit 1
}

# 显示操作结果
Write-Host "`n最终状态检查：" -ForegroundColor Cyan
Write-Host "磁盘状态：" -ForegroundColor White
Get-Disk -Number $DiskNumber | Select-Object Number, FriendlyName, IsOffline, OperationalStatus | Format-List

Write-Host "虚拟机硬盘配置：" -ForegroundColor White
Get-VMHardDiskDrive -VMName $VMName | Format-Table ControllerType, ControllerNumber, ControllerLocation, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}} -AutoSize

Write-Host "`n请在虚拟机中执行以下操作：" -ForegroundColor Yellow
Write-Host "1. 打开磁盘管理 (diskmgmt.msc)" -ForegroundColor White
Write-Host "2. 挂载新磁盘" -ForegroundColor White

Write-Host "`n脚本执行完毕，按任意键退出..." -ForegroundColor Green
pause