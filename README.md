# 北航场馆预约系统Python+Selenium自动化脚本

An automatic Python script using selenium for the BUAA reservation system.
为了给脚本设置一些使用门槛，此Readme文档将用英文撰写（我知道这难不倒CS学生）。

# Features

- Totally automatic: *SLEEPS WELL.* You'll wake up with a notice that a court for you has been **reserved and paid**.
- Explicit waiting: *YOU SLEEP, BROWSERS DON'T.* A button shall be clicked when it's ready, which is defined by your network ability, rather than `time.sleep()`.
- Priority list: *DO IT WHEN IT'S GREEN.* you can make your own priority list of which court should be booked first. 
- Debugging mechanisms: there are a few circumstances that are extremely unfriendly to the automatic scripts. However, this script would counterback if it encounters them.

**Be warned, this script requires you to enter your SSO & Alipay account's usernames & passwords to achieve fully automation, be sure you run the script in a secure environment.**


# Installation
This project is based on Python=3.7.11. For ease of use, I highly recommend you to create a new environment using conda/miniconda.
```bash
conda create -n cgyy python=3.7 -y
conda activate cgyy
```

Then, install the requirements using files with specified versions. Use 'tab' wisely to avoid any typo mistakes (or just copy to clipboard).

```bash
pip install -r requirements.txt
```

To be specific, I used `selenium==4.1.3` with Google Chrome driver, `pillow==9.0.1`, `numpy==1.21.5`, `scikit-image==0.19.2` and `pyyaml==6.0`. And I also tried `pytesseract` to recognize the captcha code, but it in fact went very south.

# Usage

- Firstly download the Chrome Driver according to your Chrome browser's version. Check your version with `Settings --> About Chrome`, e.g. I'm 
99.0.4844.82 here.

![check your version](img/chrome.png)

- Then [download the chrome driver](https://chromedriver.storage.googleapis.com/index.html) to the specific version of your browser's. Replace it with the one provided in the repo if it's unmatched.

You could try with other browser's driver (e.g. Firefox, Edge, Safari, etc.). See compatibility with other browser and driver download links here: [Selenium Documentation](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#quick-reference). Normally, just replace the driver with your matched one and it should work as well.

- Write you own config in the 'configs' folder, which in this version I named it 'default.yaml'. Fill out some information right before you use the script:
1. Your SSO & Alipay account's usernames & passwords. **Be warned again, please make sure your environment is safe!**
2. The reservation time & priority list. It is represented by the beginning of an hour e.g. `reservation time: [19, 20]` means you're reserving 19:00~21:00. It might be a bug that the reservation system prevents you from reserving non-continuous time like [19, 21] which would be invalid, forcing you to select only either of the blocks.
3. **[Optional]** By default, the script chooses the first companion candidate showing in the default config file. If you would like to choose other candidate(s), revise the index of label ranging from 1 to n. For example, `candidate: 2` means choosing the secondary candidate. if you want to choose more of the candidates, check the related codes in `cgyy.py` line 80.
- **[Optional]** You can use the script just for reservation, but pay the fees manually (in 10 minutes). If in this case, just comment `cgyy.py` line 175 and leave the alipay username & password blank, then you can pay the fees manually using QR codes through multiple payment channels.
- please check `python cgyy.py` line 186-187. If your current time is in 0:00-7:00 (for example, you get up minutes before 7am and run the script), use line 187 and comment line 186. Instead, use 186, which is a more common scenario if you're running the script before bedtime.
- Simply run the code with `python cgyy.py`. Or you could use other IDEs like Pycharm to run and see how each line works.

# Results

If you're running everything correctly, you should see the messages like these (ignore the timestamp):
![](img/messages.png)

Theoretically, as the messages above indicate, it should only takes ***3 seconds*** to lock the court.

# TODO

- An automatic framework. Hopefully, the main python script should only have for-loops and the YAML file decides which button to click, which and where the keys to send.
- A locking mechanism. If there is a locking mechanism that will allow the script to just load the configuration but cannot access it, this whole process could be significantly safer and easier to widely use.
- Refinement. The codes can be organized better. I will reorganize it with when the automatic framework is constucted.
- Other functions. For instance, a looping mechanism that checks if there are any cancellation of a preset time; a longer/priority list of reserved time for people who accept multiple time choices; other debugging mechanisms like what if others locked a court where the script sees it available due to network latency...and so on.

# Version logs

- 2022/03/15: Making new directories and start coding.
- 2022/03/16: Ran a few tests. Basic functions are fine, but only supports manual payment at this moment.
- 2022/03/17: First test and the result is inspiring. However, an error occurred when sending the alipay password. ***Created this repo.***
- 2022/03/18: Second test result showing that the login shouldn't be too early or it will require re-login when paying. ***Uploaded ver 1.0, mainly basic modules.***
- 2022/03/19: Third test with an unexpecting crashdown of "buaa payment temporarily unavailable" happened.
- 2022/03/20: Fourth test with a huge success yet the crashdown didn't occur.
- 2022/03/21: Fifth test with another huge success as the confirming message was delayed for 4 minutes that seemingly proved the debugging mechanism worked. ***Uploaded ver 1.1, fixing multiple bugs occurred in previous tests and adding this ReadMe doc.***
- 2022/03/22: Sixth test encountered an error of loading pages, which is really wierd. Might be the network problem. ***Uploaded ver 1.2, adding yaml-load modules and revising the usage part of this doc.***
- 2022/03/23: Seventh test encountered an exception from the codes uploaded yesterday. ***Uploaded ver 1.3, adding a recheck-mechanism that allows it to repeat checking for available courts if other scripts get over. Also did a yapf refinement and added a few guiding messages.***

# License

This Repo is released under [MIT License](https://rem.mit-license.org/).

---

# 🆕 新增功能 - 自动监测模式 (2026更新)

## 概述

由于自动预约和支付存在一定风险，现已移除自动支付功能，改为**场地监测 + 邮件通知**模式。

### 主要特性

- 🔍 **智能监测**：自动检查多个场馆（主馆+副馆）的可用场地
- 📧 **邮件通知**：发现可用场地立即发邮件提醒，包含详细信息
- ⏰ **定时运行**：支持Windows任务计划程序，每30分钟自动检查
- 🔄 **持续监测**：提供Python脚本可24小时持续运行
- ✅ **更安全**：只监测不预约，需要手动登录完成预约
- 🤫 **静默运行**：支持后台无窗口运行，不干扰日常工作

---

## 📋 准备工作

### 第一步：安装Python环境

1. **安装Python 3.7+**（推荐使用Anaconda）
   
   ```bash
   # 使用conda创建独立环境（推荐）
   conda create -n cgyy python=3.7 -y
   conda activate cgyy
   ```

2. **安装依赖包**
   
   ```bash
   # 在项目目录下执行
   pip install -r requirements.txt
   ```

### 第二步：下载ChromeDriver

⚠️ **重要**：ChromeDriver版本必须与Chrome浏览器版本匹配！

#### 1. 查看Chrome浏览器版本

打开Chrome浏览器，访问：`chrome://version/`

或者：设置 → 关于Chrome → 查看版本号

例如：`145.0.7632.160` （前三位是主版本号）

#### 2. 下载对应版本的ChromeDriver

**下载地址**：

- **Chrome 115及以上版本**：https://googlechromelabs.github.io/chrome-for-testing/
  - 点击页面找到对应版本的 `chromedriver` 下载链接
  - 选择 `win64` 版本下载
  
- **Chrome 114及以下版本**：https://chromedriver.storage.googleapis.com/index.html
  - 找到对应版本文件夹
  - 下载 `chromedriver_win32.zip`

#### 3. 安装ChromeDriver

1. 解压下载的文件，得到 `chromedriver.exe`
2. 将 `chromedriver.exe` 复制到项目根目录（与 `cgyy.py` 同级）
3. 测试是否安装成功：
   ```bash
   # 在项目目录执行
   chromedriver.exe --version
   ```

**示例输出**：
```
ChromeDriver 145.0.7632.160 (...)
```

---

## ⚙️ 配置文件说明

编辑 `configs/default.yaml` 文件，按以下说明填写：

### 完整配置示例

```yaml
# 统一认证账号配置
sso:
  user: '12345678'              # 你的学号/工号
  passwd: 'YourPassword123'      # 统一认证密码

# 浏览器配置
browser:
  headless: true                 # 静默模式：true=后台运行, false=显示窗口

# 邮件通知配置
email:
  sender: '1234567890@qq.com'    # 发件邮箱（QQ邮箱）
  password: 'abcdefghijklmnop'   # SMTP授权码（不是邮箱密码！）
  receiver: '1234567890@qq.com'  # 收件邮箱（接收通知的邮箱）
  smtp_server: 'smtp.qq.com'     # SMTP服务器
  smtp_port: 465                 # SMTP端口

# 场地优先级（1-12号场地）
priority: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# 监测时间段范围（24小时制）
# 格式：[[起始小时, 结束小时], [起始小时, 结束小时], ...]
# 只有在这些时间段内的场地才会发送邮件通知
# 例如：[[7, 22]] 表示只监测 7:00-22:00 之间的场地
# 多个时间段：[[7, 12], [18, 22]] 表示只监测 7-12点 和 18-22点
reserve_time: [[7, 22]]

# 同伴选择（第几个候选同伴，从1开始）
candidate: 1
```

### 各字段详细说明

#### 1. `sso` - 统一认证配置

| 字段 | 说明 | 示例 |
|------|------|------|
| `user` | 学号或工号 | `'21376367'` |
| `passwd` | 统一认证密码 | `'YourPassword'` |

⚠️ **注意**：密码需要用引号包裹

#### 2. `browser` - 浏览器配置

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `headless` | 是否静默运行 | `true`（推荐）/ `false`（调试用） |

- `true`：浏览器在后台运行，不显示窗口（适合日常使用）
- `false`：显示浏览器窗口（适合首次测试或调试）

#### 3. `email` - 邮件通知配置

| 字段 | 说明 | 如何获取 |
|------|------|----------|
| `sender` | 发件邮箱 | 你的QQ邮箱地址 |
| `password` | SMTP授权码 | 见下方"获取QQ邮箱SMTP授权码" |
| `receiver` | 收件邮箱 | 接收通知的邮箱（可以与发件邮箱相同） |
| `smtp_server` | SMTP服务器 | QQ邮箱固定为 `smtp.qq.com` |
| `smtp_port` | SMTP端口 | 固定为 `465` |

**获取QQ邮箱SMTP授权码**：

1. 登录 [QQ邮箱网页版](https://mail.qq.com)
2. 点击顶部"设置" → "账户"
3. 向下滚动找到 **"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"**
4. 点击"开启" **IMAP/SMTP服务**
5. 按提示发送短信验证
6. 复制生成的**授权码**（16位字母，类似：`abcdefghijklmnop`）
7. 将授权码填入 `password` 字段

⚠️ **重要**：
- `password` 填写的是**授权码**，不是QQ邮箱登录密码！
- 授权码只显示一次，请妥善保存
- 如果忘记授权码，需要重新生成

**支持其他邮箱吗？**

可以，但需要修改 `smtp_server` 和 `smtp_port`：

| 邮箱 | SMTP服务器 | 端口 |
|------|-----------|------|
| QQ邮箱 | smtp.qq.com | 465 |
| 163邮箱 | smtp.163.com | 465 |
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |

#### 4. `priority` - 场地优先级

指定场地编号的优先级顺序（目前监测模式不需要此配置）

```yaml
priority: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

#### 5. `reserve_time` - 监测时间段范围 ⭐

**重要配置**：指定哪些时间段的场地需要监测和通知。

**格式**：二维数组 `[[起始小时, 结束小时], ...]`

**示例**：

| 配置 | 说明 | 效果 |
|------|------|------|
| `[[7, 22]]` | 监测 7:00-22:00 | 只通知这个时间段内的场地 |
| `[[8, 12], [18, 22]]` | 监测两个时段 | 只通知 8-12点 和 18-22点的场地 |
| `[[19, 22]]` | 只监测晚上 | 只通知 19:00-22:00 的场地 |
| `[[7, 9], [12, 14], [18, 20]]` | 三个时段 | 只通知早、中、晚三个时段的场地 |

**工作原理**：

- 脚本会检测**所有时间段**的场地
- 但只有**在配置范围内**的场地才会：
  - ✅ 显示在终端输出中
  - ✅ 包含在邮件通知中
- **不在范围内**的场地会被自动过滤掉：
  - ⊗ 终端显示"不在监测时间范围内"
  - ⊗ 不会发送邮件通知

**使用场景**：

1. **避开早晨时段**：`[[12, 22]]` （不通知 7-12点的场地）
2. **只要晚上时段**：`[[18, 22]]` （只想打晚场）
3. **午休时段**：`[[12, 14]]` （中午空闲时打球）
4. **工作日晚上+周末全天**：配合定时任务使用不同配置

**注意事项**：

- ⚠️ 小时数使用 24 小时制
- ⚠️ 结束小时为**不包含**，如 `[7, 22]` 表示 7:00-21:59
- ⚠️ 时间段匹配基于**场地开始时间**，如场地 "19:00-20:00" 匹配的是 19 点
- ⚠️ 如果设置了多个不连续的时间段，建议间隔至少 1 小时

#### 6. `candidate` - 同伴选择

指定选择第几个候选同伴（目前监测模式不需要此配置）

```yaml
candidate: 1  # 选择第1个同伴
```

---

## 快速开始

### 1️⃣ 配置邮箱（必需）

编辑 `configs/default.yaml`，按照上方"配置文件说明"填写完整信息。

### 1️⃣.5 配置静默运行（可选但推荐）⭐

**静默模式**：浏览器在后台运行，不会弹出窗口，避免干扰工作。

编辑 `configs/default.yaml`：

```yaml
browser:
  headless: true  # 静默运行（推荐），不显示浏览器窗口
  # headless: false  # 调试模式，显示浏览器窗口（用于排查问题）
```

**说明**：
- ✅ **开启静默模式**（`true`）：脚本在后台运行，不弹窗，适合日常自动化
- 🔧 **关闭静默模式**（`false`）：显示浏览器窗口，用于首次测试或调试问题

详细说明请查看：[静默运行说明.md](静默运行说明.md)

### 2️⃣ 测试邮件功能

```bash
python test_email.py
```

### 3️⃣ 手动运行一次测试

```bash
python cgyy.py
```

### 4️⃣ 设置自动运行（选择一种方式）

#### 方式A：Windows任务计划程序（推荐）⭐

**自动配置（最简单）：**
```powershell
# 右键PowerShell，选择"以管理员身份运行"
cd E:\HL_GIT\BUAA_CGYY
.\setup_scheduler.ps1
```

按提示输入：
- 任务名称（默认：BUAA场馆监测）
- 检测间隔（默认：30分钟）
- 开始时间（默认：07:00）
- 运行时长（默认：15小时）

**手动配置（详细步骤）：**

如果自动配置脚本无法运行，可以手动配置：

1. **准备启动脚本**
   
   确保项目目录下有 `run_cgyy.bat` 文件（自动配置会创建，手动创建参考下方）

2. **打开任务计划程序**
   
   ```
   Win + R → 输入 taskschd.msc → 回车
   ```

3. **创建基本任务**
   
   - 点击右侧"创建基本任务"
   - 任务名称：`BUAA场馆监测`
   - 描述：`每30分钟检测一次场馆可用情况`
   - 点击"下一步"

4. **设置触发器**
   
   - 选择"每天"，点击"下一步"
   - 开始时间：`07:00:00`（或你希望的时间）
   - 点击"下一步"

5. **设置操作**
   
   - 选择"启动程序"，点击"下一步"
   - 程序或脚本：浏览选择 `run_cgyy.bat`
   - 起始于（可选）：填写项目目录路径，如 `E:\HL_GIT\BUAA_CGYY`
   - 点击"下一步"

6. **完成并修改高级设置**
   
   - 勾选"完成时打开此任务的属性对话框"
   - 点击"完成"

7. **配置高级选项**（在打开的属性对话框中）
   
   **常规选项卡**：
   - ✅ 勾选"使用最高权限运行"
   - ✅ 勾选"不管用户是否登录都要运行"
   
   **触发器选项卡**：
   - 双击刚创建的触发器
   - ✅ 勾选"重复任务间隔"
   - 间隔：`30 分钟`（或根据需要调整）
   - 持续时间：`15 小时`（表示从07:00到22:00）
   - ✅ 勾选"已启用"
   - 点击"确定"
   
   **条件选项卡**：
   - ✅ 勾选"唤醒计算机运行此任务"（可选，确保电脑休眠时也能运行）
   - ❌ 取消勾选"只有在计算机使用交流电源时才启动此任务"
   
   **设置选项卡**：
   - ✅ 勾选"允许按需运行任务"
   - ✅ 勾选"如果任务失败，按以下时间重新启动"：`1 分钟`，尝试`3`次
   - 如果任务已在运行：选择"不启动新实例"
   
   点击"确定"保存设置

8. **测试任务**
   
   - 在任务计划程序中找到刚创建的任务
   - 右键点击 → 选择"运行"
   - 检查是否有邮件通知（如果有可用场地）

9. **查看运行历史**
   
   - 右键点击任务 → 属性 → 历史记录选项卡
   - 可以看到任务的运行日志

**`run_cgyy.bat` 文件内容**：

如果需要手动创建，内容如下：

```batch
@echo off
chcp 65001 > nul
echo 正在启动北航场馆监测...
echo 时间: %date% %time%

cd /d "%~dp0"

call D:\anaconda\Scripts\activate.bat base
if errorlevel 1 (
    echo 错误：无法激活conda环境
    pause
    exit /b 1
)

python cgyy.py
if errorlevel 1 (
    echo 错误：脚本执行失败
    pause
    exit /b 1
)

echo 监测完成
```

⚠️ **注意**：
- 将 `D:\anaconda` 替换为你的Anaconda安装路径
- 如果不使用conda，删除 `call D:\anaconda\Scripts\activate.bat base` 这行

#### 方式B：Python持续监测

```bash
python cgyy_monitor.py
```

按 `Ctrl+C` 停止

## 📁 新增文件

| 文件 | 说明 |
|------|------|
| `run_cgyy.bat` | Windows批处理启动脚本 |
| `setup_scheduler.ps1` | 自动配置任务计划程序工具 |
| `cgyy_monitor.py` | Python持续监测脚本 |
| `test_email.py` | 邮件功能测试脚本 |
| `自动监测配置指南.md` | 详细配置文档 |
| `快速开始.md` | 快速配置指引 |
| `静默运行说明.md` | 静默运行模式配置和使用说明 |

## 🔧 配置说明

### 监测场馆

当前监测两个场馆：
- 学院路校区-体育馆主馆-羽毛球
- 学院路校区-体育馆训练馆(副馆)-羽毛球

可在 `cgyy.py` 第546-555行修改。

### 检测间隔

**任务计划程序方式：**
- 打开任务计划程序（`taskschd.msc`）
- 编辑触发器的"重复任务间隔"

**Python持续监测方式：**
- 编辑 `cgyy_monitor.py` 第13行：
  ```python
  CHECK_INTERVAL_MINUTES = 30  # 改为你想要的间隔
  ```

## 📧 邮件通知示例

发现可用场地后，会收到包含以下信息的邮件：
- ✅ 检测时间
- ✅ 场馆名称
- ✅ 具体日期（如03月12日）
- ✅ 可用时间段
- ✅ 所有可用场地编号和价格
- ✅ 快捷预约链接

## ⚠️ 重要提醒

1. 脚本**仅做监测**，不会自动预约
2. 收到邮件后需要**尽快手动登录**完成预约
3. 建议检测间隔**至少30分钟**，避免频繁请求
4. 确保电脑不会休眠（或在任务计划中启用"唤醒计算机"）

## 🆘 故障排除

### 没收到邮件
1. 运行 `python test_email.py` 测试邮件配置
2. 检查垃圾邮件箱
3. 确认SMTP授权码正确（不是邮箱密码）

### 任务没有运行
1. 查看任务计划程序的历史记录
2. 确保使用了"最高权限运行"
3. 检查 `run_cgyy.bat` 中的路径是否正确

### 更多帮助
详细配置和高级功能请查看：[自动监测配置指南.md](自动监测配置指南.md)

---

## 2026 Update Log

- 2026/03/11: 移除自动支付功能，改为监测+邮件通知模式
- 2026/03/11: 新增多场馆检查功能（主馆+副馆）
- 2026/03/11: 新增Windows任务计划程序自动配置工具
- 2026/03/11: 新增Python持续监测脚本
- 2026/03/11: 优化邮件通知，汇总所有可用场地信息