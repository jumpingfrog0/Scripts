# Quick-Mount.ps1 - 快速挂载指定磁盘
param(
    [int]$DiskNumber = 0
)

# 设置磁盘在线
Set-Disk -Number $DiskNumber -IsOffline $false

# 自动分配驱动器号
$partitions = Get-Partition -DiskNumber $DiskNumber
foreach ($partition in $partitions) {
    if (-not $partition.DriveLetter) {
        $usedLetters = (Get-Volume).DriveLetter | Where-Object { $_ -ne $null }
        $availableLetter = [char[]](68..90) | Where-Object { $_ -notin $usedLetters } | Select-Object -First 1
        if ($availableLetter) {
            Set-Partition -DiskNumber $DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter $availableLetter
            Write-Host "已分配驱动器号 ${availableLetter}: 给磁盘 $DiskNumber"
        }
    }
}

Write-Host "挂载完成！"