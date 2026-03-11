# 自动运行脚本使用说明

本项目提供两种自动运行方案，可根据需求选择：

## 方案一：持续运行脚本（推荐用于临时运行）

### 文件：`run_auto.bat`

**特点：**
- 简单易用，双击即可运行
- 脚本会持续运行，每隔指定时间执行一次预约程序
- 关闭窗口即停止运行

**使用步骤：**

1. 双击运行 `run_auto.bat`
2. 脚本会自动激活 conda 环境并运行预约程序
3. 每次运行完成后，等待指定时间（默认 30 分钟）再次运行
4. 按 `Ctrl+C` 可以停止脚本

**自定义运行间隔：**

编辑 `run_auto.bat`，修改以下行：
```batch
set INTERVAL=1800
```
将 `1800`（秒）改为你想要的间隔时间。例如：
- 10 分钟 = 600 秒
- 30 分钟 = 1800 秒
- 1 小时 = 3600 秒

---

## 方案二：Windows 任务计划程序（推荐用于长期运行）

### 文件：`setup_task_scheduler.ps1`

**特点：**
- 开机自动启动（延迟1分钟，避免开机卡顿）
- 后台运行，不会显示窗口
- 每隔指定时间（默认30分钟）自动运行一次
- 更稳定，系统级别的任务管理
- 可在 Windows 任务计划程序中统一管理
- 即使关机重启，任务也会自动恢复运行

**使用步骤：**

1. **以管理员身份运行 PowerShell：**
   - 在开始菜单搜索 "PowerShell"
   - 右键点击 "Windows PowerShell"
   - 选择 "以管理员身份运行"

2. **执行配置脚本：**
   ```powershell
   cd E:\HL_GIT\BUAA_CGYY
   .\setup_task_scheduler.ps1
   ```

3. **根据提示完成配置：**
   - 脚本会自动创建名为 "BUAA_场地预约" 的任务
   - 询问是否立即启动任务，输入 `Y` 确认

4. **任务创建完成！**
   - 任务会每隔 30 分钟自动运行一次
   - **开机后会自动启动**（延迟1分钟）
   - 每天早上 7:00 也会自动启动（双重保障）
   - 无需手动启动，完全自动化

**自定义运行间隔：**

编辑 `setup_task_scheduler.ps1`，修改以下行：
```powershell
$IntervalMinutes = 30
```
将 `30` 改为你想要的间隔分钟数。

**管理任务：**

```powershell
# 查看任务状态（State: Ready=就绪, Running=运行中, Disabled=已禁用）
Get-ScheduledTask -TaskName "BUAA_场地预约" | Select-Object TaskName, State

# 查看任务详细信息（上次运行时间、下次运行时间、运行结果）
Get-ScheduledTaskInfo -TaskName "BUAA_场地预约"

# 启动任务
Start-ScheduledTask -TaskName "BUAA_场地预约"

# 停止任务
Stop-ScheduledTask -TaskName "BUAA_场地预约"

# 禁用任务（暂时不运行）
Disable-ScheduledTask -TaskName "BUAA_场地预约"

# 启用任务（恢复自动运行）
Enable-ScheduledTask -TaskName "BUAA_场地预约"

# 删除任务
Unregister-ScheduledTask -TaskName "BUAA_场地预约" -Confirm:$false

# 实时监控任务状态（每5秒刷新一次，按 Ctrl+C 停止）
while ($true) { 
    Clear-Host
    Write-Host "========== 任务监控 ==========" -ForegroundColor Cyan
    Get-ScheduledTask -TaskName "BUAA_场地预约" | Select-Object TaskName, State | Format-List
    Get-ScheduledTaskInfo -TaskName "BUAA_场地预约" | Select-Object LastRunTime, LastTaskResult, NextRunTime | Format-List
    Write-Host "LastTaskResult 说明：0=成功, 其他值=错误代码" -ForegroundColor Yellow
    Write-Host "按 Ctrl+C 停止监控..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}
```

或者在 Windows 图形界面中管理：
- 按 `Win+R`，输入 `taskschd.msc` 打开任务计划程序
- 在任务计划程序库中找到 "BUAA_场地预约"
- 可以查看：
  - **常规**：任务基本信息和运行权限
  - **触发器**：运行时间和频率设置
  - **操作**：执行的命令和脚本
  - **历史记录**：查看每次运行的详细日志（需要启用历史记录）
- 右键任务可以进行：启动、结束、禁用、启用、删除等操作

---

## 注意事项

1. **确保配置文件正确：**
   - 在运行自动脚本前，请先确保 `configs/default.yaml` 已正确配置
   - 包括统一认证账号密码、邮箱配置等

2. **Conda 环境路径：**
   - 两个脚本中都默认使用 `D:\anaconda` 和 `torch` 环境
   - 如果你的路径不同，请修改脚本中的路径

3. **网络连接：**
   - 预约程序需要网络连接
   - 建议在网络稳定的环境下运行

4. **日志查看：**
   - 方案一：直接在窗口中查看运行日志
   - 方案二：
     - 使用 PowerShell 查看任务信息：`Get-ScheduledTaskInfo -TaskName "BUAA_场地预约"`
     - 在任务计划程序（taskschd.msc）的"历史记录"标签页查看详细日志
     - `LastTaskResult` 为 `0` 表示成功，其他值表示错误代码

5. **任务状态说明：**
   - `Ready` - 就绪状态，等待下次运行
   - `Running` - 正在运行中
   - `Disabled` - 已禁用，不会自动运行
   - 任务创建后会自动启用，每隔设定的时间（默认30分钟）自动运行

---

## 故障排除

**问题：脚本无法运行**
- 检查 Python 和 conda 是否已安装
- 检查脚本中的路径是否正确
- 确保已安装所有依赖包：`pip install -r requirements.txt`

**问题：任务计划程序任务失败**
- 检查任务历史记录，查看错误信息
- 确保以管理员身份运行了配置脚本
- 检查 `run_scheduled.bat` 文件是否创建成功

**问题：程序运行但没有预约成功**
- 检查 `configs/default.yaml` 配置是否正确
- 查看程序运行日志，确认账号密码是否正确
- 确认目标场地是否可预约

---

## 推荐配置

- **临时使用**（几小时到一天）：使用方案一（`run_auto.bat`）
- **长期使用**（几天到几周）：使用方案二（任务计划程序）
- **运行间隔**：建议设置为 30-60 分钟，避免过于频繁请求

