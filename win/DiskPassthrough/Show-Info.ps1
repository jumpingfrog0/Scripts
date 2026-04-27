# Show-Info.ps1 - 显示当前磁盘和虚拟机信息
Write-Host "=== 当前系统信息 ===" -ForegroundColor Green

Write-Host "`n可用的虚拟机：" -ForegroundColor Yellow
Get-VM | Format-Table Name, State, Status, @{Name="Memory(MB)";Expression={$_.MemoryAssigned/1MB}} -AutoSize

Write-Host "`n物理磁盘列表：" -ForegroundColor Yellow
Get-Disk | Where-Object {$_.BusType -ne 'Microsoft Reserved'} | Format-Table Number, FriendlyName, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, OperationalStatus, IsOffline -AutoSize

pause