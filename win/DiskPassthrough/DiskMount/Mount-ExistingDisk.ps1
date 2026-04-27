# Mount-ExistingDisk.ps1
# 功能：自动挂载已有数据的磁盘（不格式化）
# 在虚拟机中以管理员身份运行

# 显示脚本信息
Write-Host "=== 现有数据磁盘自动挂载脚本 ===" -ForegroundColor Green
Write-Host "功能：将已包含数据的磁盘设置为在线并分配驱动器号" -ForegroundColor Yellow
Write-Host "注意：不会进行格式化操作，保留所有现有数据" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell 选择'以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

# 查找离线磁盘
Write-Host "正在扫描离线磁盘..." -ForegroundColor Cyan
$offlineDisks = Get-Disk | Where-Object { $_.OperationalStatus -eq 'Offline' -and $_.PartitionStyle -ne 'Raw' }

if (-not $offlineDisks) {
    Write-Host "未找到包含数据的离线磁盘" -ForegroundColor Yellow
    Write-Host "当前磁盘状态：" -ForegroundColor White
    Get-Disk | Format-Table Number, FriendlyName, Size, OperationalStatus, IsOffline, PartitionStyle -AutoSize
    pause
    exit 0
}

Write-Host "找到 $($offlineDisks.Count) 个包含数据的离线磁盘：" -ForegroundColor Green
$offlineDisks | Format-Table Number, FriendlyName, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, PartitionStyle -AutoSize

foreach ($disk in $offlineDisks) {
    Write-Host "`n处理磁盘 $($disk.Number): $($disk.FriendlyName)" -ForegroundColor Cyan
    Write-Host "大小: $([math]::Round($disk.Size/1GB,2)) GB" -ForegroundColor White
    Write-Host "分区样式: $($disk.PartitionStyle)" -ForegroundColor White
    
    # 检查磁盘是否已有分区
    $partitions = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue
    if ($partitions) {
        Write-Host "发现现有分区，尝试挂载..." -ForegroundColor Yellow
        
        try {
            # 设置磁盘在线
            Set-Disk -Number $disk.Number -IsOffline $false
            Write-Host "✅ 磁盘已设置为在线" -ForegroundColor Green
            
            # 为每个分区分配驱动器号
            <#
            foreach ($partition in $partitions) {
                if (-not $partition.driveletter) {
                    # 获取可用的驱动器号
                    $usedletters = (get-volume).driveletter | where-object { $_ -ne $null }
                    $availableletter = [char[]](68..90) | where-object { $_ -notin $usedletters } | select-object -first 1
                    
                    if ($availableletter) {
                        set-partition -disknumber $disk.number -partitionnumber $partition.partitionnumber -newdriveletter $availableletter
                        write-host "✅ 分区 $($partition.partitionnumber) 已分配驱动器号: ${availableletter}:" -foregroundcolor green
                    } else {
                        write-host "⚠️  分区 $($partition.partitionnumber) 无法分配驱动器号（无可用盘符）" -foregroundcolor yellow
                    }
                } else {
                    write-host "✅ 分区 $($partition.partitionnumber) 已有驱动器号: $($partition.driveletter):" -foregroundcolor green
                }
            }
            #>
            
        } catch {
            Write-Host "❌ 挂载失败: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "⚠️  磁盘没有分区，但包含数据。可能需要手动处理。" -ForegroundColor Yellow
        
        $confirm = Read-Host "是否尝试设置磁盘在线？(y/N)"
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            try {
                Set-Disk -Number $disk.Number -IsOffline $false
                Write-Host "✅ 磁盘已设置为在线，请在磁盘管理中查看" -ForegroundColor Green
            } catch {
                Write-Host "❌ 设置失败: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

# 显示最终结果
Write-Host "`n=== 挂载操作完成 ===" -ForegroundColor Green
Write-Host "当前磁盘状态：" -ForegroundColor Cyan
Get-Disk | Format-Table Number, FriendlyName, OperationalStatus, IsOffline, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}} -AutoSize

Write-Host "`n当前卷状态：" -ForegroundColor Cyan
Get-Volume | Where-Object DriveLetter -ne $null | Format-Table DriveLetter, FileSystemLabel, FileSystem, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="Free(GB)";Expression={[math]::Round($_.SizeRemaining/1GB,2)}} -AutoSize

Write-Host "`n脚本执行完毕，按任意键退出..." -ForegroundColor Green
pause