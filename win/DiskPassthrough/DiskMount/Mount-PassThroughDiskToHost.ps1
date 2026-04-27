# Mount-PassThroughDiskToHost.ps1
# 功能：将直通物理硬盘从Hyper-V虚拟机挂载回宿主机
# 注意：需要在宿主机以管理员身份运行

param(
    [int]$DiskNumber,
    [switch]$ReadOnly = $false,
    [switch]$ListDisks = $false
)

Write-Host "=== 直通物理硬盘挂载回宿主机工具 ===" -ForegroundColor Green
Write-Host "功能：将直通到虚拟机的物理硬盘重新挂载回宿主机" -ForegroundColor Yellow
Write-Host ""

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell 选择'以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

# 显示所有磁盘列表
if ($ListDisks -or -not $DiskNumber) {
    Write-Host "当前所有物理磁盘列表：" -ForegroundColor Cyan
    $allDisks = Get-Disk | Where-Object {$_.BusType -ne 'Microsoft Reserved'}
    $allDisks | Format-Table Number, FriendlyName, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, OperationalStatus, IsOffline, IsReadOnly -AutoSize
    
    if ($ListDisks) {
        pause
        exit 0
    }
}

# 如果没有指定磁盘编号，提示输入
if (-not $DiskNumber) {
    $DiskNumber = Read-Host "请输入要挂载回宿主机的磁盘编号（Number）"
}

# 验证磁盘是否存在
$disk = Get-Disk -Number $DiskNumber -ErrorAction SilentlyContinue
if (-not $disk) {
    Write-Host "错误：磁盘编号 $DiskNumber 不存在！" -ForegroundColor Red
    pause
    exit 1
}

# 显示磁盘信息
Write-Host "`n磁盘信息：" -ForegroundColor Cyan
Write-Host "编号: $($disk.Number)" -ForegroundColor White
Write-Host "名称: $($disk.FriendlyName)" -ForegroundColor White
Write-Host "大小: $([math]::Round($disk.Size/1GB,2)) GB" -ForegroundColor White
Write-Host "状态: $($disk.OperationalStatus)" -ForegroundColor White
Write-Host "离线: $($disk.IsOffline)" -ForegroundColor White
Write-Host "只读: $($disk.IsReadOnly)" -ForegroundColor White

# 检查磁盘是否已经在宿主机在线
if (-not $disk.IsOffline) {
    Write-Host "`n⚠️  磁盘 $DiskNumber 已经在宿主机在线状态" -ForegroundColor Yellow
    
    $partitions = Get-Partition -DiskNumber $DiskNumber -ErrorAction SilentlyContinue
    if ($partitions) {
        Write-Host "当前分区信息：" -ForegroundColor White
        $partitions | Format-Table PartitionNumber, DriveLetter, Size, Type -AutoSize
    }
    
    $confirm = Read-Host "是否继续操作？(y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "操作已取消。" -ForegroundColor Yellow
        pause
        exit 0
    }
}

# 确认操作
Write-Host "`n操作确认：" -ForegroundColor Red
Write-Host "将把磁盘 $DiskNumber ($($disk.FriendlyName)) 挂载回宿主机" -ForegroundColor White
if ($ReadOnly) {
    Write-Host "访问模式: 只读" -ForegroundColor Yellow
} else {
    Write-Host "访问模式: 读写" -ForegroundColor Yellow
}

$confirm = Read-Host "确认执行此操作？(y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "操作已取消。" -ForegroundColor Yellow
    pause
    exit 0
}

# 执行挂载操作
try {
    Write-Host "`n开始执行挂载操作..." -ForegroundColor Green
    
    # 设置磁盘在线
    Write-Host "1. 设置磁盘在线..." -ForegroundColor Cyan
    Set-Disk -Number $DiskNumber -IsOffline $false
    
    if ($ReadOnly) {
        Write-Host "2. 设置只读模式..." -ForegroundColor Cyan
        Set-Disk -Number $DiskNumber -IsReadOnly $true
    } else {
        Set-Disk -Number $DiskNumber -IsReadOnly $false
    }
    
    # 为分区分配驱动器号
    Write-Host "3. 分配驱动器号..." -ForegroundColor Cyan
    $partitions = Get-Partition -DiskNumber $DiskNumber -ErrorAction SilentlyContinue
    
    if ($partitions) {
        foreach ($partition in $partitions) {
            if (-not $partition.DriveLetter) {
                # 获取可用的驱动器号（从D:开始）
                $usedLetters = (Get-Volume).DriveLetter | Where-Object { $_ -ne $null }
                $availableLetter = [char[]](68..90) | Where-Object { $_ -notin $usedLetters } | Select-Object -First 1
                
                if ($availableLetter) {
                    Set-Partition -DiskNumber $DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter $availableLetter
                    Write-Host "   ✅ 分区 $($partition.PartitionNumber) 分配驱动器号: ${availableLetter}:" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  分区 $($partition.PartitionNumber) 无法分配驱动器号（无可用盘符）" -ForegroundColor Yellow
                }
            } else {
                Write-Host "   ✅ 分区 $($partition.PartitionNumber) 已有驱动器号: $($partition.DriveLetter):" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "   ⚠️  磁盘没有分区，请在磁盘管理中处理" -ForegroundColor Yellow
    }
    
    Write-Host "`n✅ 挂载操作成功完成！" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ 操作失败：$($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

# 显示最终结果
Write-Host "`n最终磁盘状态：" -ForegroundColor Cyan
$finalDisk = Get-Disk -Number $DiskNumber
$finalDisk | Format-List Number, FriendlyName, Size, OperationalStatus, IsOffline, IsReadOnly

Write-Host "分区信息：" -ForegroundColor Cyan
$finalPartitions = Get-Partition -DiskNumber $DiskNumber -ErrorAction SilentlyContinue
if ($finalPartitions) {
    $finalPartitions | Format-Table PartitionNumber, DriveLetter, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, Type -AutoSize
}

Write-Host "卷信息：" -ForegroundColor Cyan
$volumes = Get-Volume -ErrorAction SilentlyContinue | Where-Object { $_.DriveLetter -ne $null -and (Get-Partition -DriveLetter $_.DriveLetter).DiskNumber -eq $DiskNumber }
if ($volumes) {
    $volumes | Format-Table DriveLetter, FileSystemLabel, FileSystem, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="Free(GB)";Expression={[math]::Round($_.SizeRemaining/1GB,2)}} -AutoSize
}

# 打开文件资源管理器查看
$mountedDrives = $volumes | Where-Object { $_.DriveLetter -ne $null } | Select-Object -ExpandProperty DriveLetter
if ($mountedDrives) {
    Write-Host "`n正在打开文件资源管理器..." -ForegroundColor Green
    foreach ($drive in $mountedDrives) {
        Start-Process "explorer.exe" -ArgumentList "${drive}:"
    }
}

Write-Host "`n挂载完成！按任意键退出..." -ForegroundColor Green
pause