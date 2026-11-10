# -*- coding:utf-8 -*-
from selenium import webdriver
import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from captcha2str import captcha2str
import yaml
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from pathlib import Path

# 先读取配置文件
begin_time = "07:00:00"  # 注意07的0

conf_file = open('configs/default.yaml', 'r',encoding='utf-8')
configs = yaml.load(conf_file, Loader=yaml.Loader)
# 监测时间段范围配置
# 格式：[[7, 22]] 表示只监测 7:00-22:00 之间的场地
# 可以设置多个区间：[[7, 12], [18, 22]] 表示只监测 7-12点 和 18-22点
reserve_time = configs['reserve_time']
priority = configs['priority']


def is_time_in_range(time_slot_str, time_ranges):
    """
    检查时间段是否在允许的范围内
    
    参数:
        time_slot_str: 时间段字符串，如 "07:00-08:00" 或 "19:00-20:00"
        time_ranges: 允许的时间范围列表，如 [[7, 22]] 或 [[7, 12], [18, 22]]
    
    返回:
        True: 时间段在允许范围内
        False: 时间段不在允许范围内或格式错误
    """
    try:
        # 解析时间段字符串，提取开始小时
        # 格式示例："07:00-08:00" 或 "19:00-20:00"
        if '-' not in time_slot_str or ':' not in time_slot_str:
            return False
        
        start_time = time_slot_str.split('-')[0].strip()
        start_hour = int(start_time.split(':')[0])
        
        # 检查是否在任一允许的时间范围内
        for time_range in time_ranges:
            if len(time_range) >= 2:
                range_start = time_range[0]
                range_end = time_range[1]
                
                # 检查开始小时是否在范围内
                if range_start <= start_hour < range_end:
                    return True
        
        return False
    except Exception as e:
        print(f"  ⚠️ 时间段解析错误: {time_slot_str}, 错误: {e}")
        return False


# 配置Chrome选项
browser_version = '156.0.8078.73'
browser_dir = Path(__file__).resolve().parent / '.browser' / browser_version
browser_binary = browser_dir / 'chrome-win64' / 'chrome.exe'
driver_binary = browser_dir / 'chromedriver-win64' / 'chromedriver.exe'
for binary in (browser_binary, driver_binary):
    if not binary.is_file():
        raise FileNotFoundError(
            f'Missing pinned browser runtime: {binary}. Run .\\install_browser.ps1 first.')

chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
chrome_options.binary_location = str(browser_binary)

# 根据配置决定是否使用静默模式
if configs.get('browser', {}).get('headless', True):  # 默认使用headless模式
    print("🔇 使用静默模式运行（无窗口）")
    chrome_options.add_argument('--headless')  # 无窗口模式
else:
    print("🖥️ 使用可见窗口模式运行")
    pass

# 添加其他优化选项
chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument('--disable-dev-shm-usage')  # 解决资源限制
chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 防止被检测为自动化
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')

print(f'Pinned Chrome/ChromeDriver: {browser_version}')
driver = webdriver.Chrome(service=Service(str(driver_binary)), options=chrome_options)


def explicit_click(by, value):
    print(f"尝试点击元素: {by}, {value}")
    locator = (by, value)
    try:
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located(locator))
        print("元素已找到，准备点击")
        driver.find_element(by, value).click()
    except Exception as e:
        print("元素未找到，异常信息：", e)
        driver.save_screenshot('error.png')
        raise


def explicit_find(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 30,
                  0.5).until(EC.presence_of_element_located(locator))
    return driver.find_element(method, value)


def explicit_find_short(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 5,
                  0.5).until(EC.presence_of_element_located(locator))
    return driver.find_element(method, value)


def explicit_interact(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    return driver.find_element(method, value)


def safe_click(by, value, retries=3, wait_timeout=10, use_js=False):
    """安全点击元素，处理各种点击异常"""
    locator = (by, value)
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, wait_timeout, 0.5).until(EC.element_to_be_clickable(locator))
            if use_js:
                # 使用JavaScript点击
                driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            if attempt == retries - 1:
                # 最后一次尝试使用JavaScript点击
                try:
                    element = driver.find_element(by, value)
                    driver.execute_script("arguments[0].click();", element)
                    return True
                except:
                    raise
            time.sleep(0.5)
    return False


def safe_click_element(element, retries=3):
    """安全点击已找到的元素，处理StaleElementReferenceException和ElementClickInterceptedException"""
    for attempt in range(retries):
        try:
            element.click()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            if attempt == retries - 1:
                # 最后一次尝试使用JavaScript点击
                try:
                    driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_error:
                    print(f"点击元素失败，已重试{retries}次: {js_error}")
                    return False
            time.sleep(0.5)
        except Exception as e:
            print(f"点击元素时出错: {e}")
            return False
    return False


def save_page_html(filename="page_debug.html"):
    """保存当前页面的HTML到文件"""
    try:
        html_content = driver.page_source
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ 页面HTML已保存到: {filename}")
        return True
    except Exception as e:
        print(f"❌ 保存HTML失败: {e}")
        return False


def get_venue_data_from_js():
    """通过JavaScript直接获取场地数据"""
    try:
        js_code = """
        function getVenueData() {
            let venueBlocks = [];
            let debugInfo = [];
            
            // 获取当前显示的时间段（从表头获取）
            let table = document.querySelector('#scrollTable');
            if (!table) {
                return {
                    totalBlocks: 0,
                    freeBlocks: 0,
                    blocks: [],
                    currentTimes: [],
                    error: 'Table not found',
                    debug: ['未找到 #scrollTable']
                };
            }
            
            debugInfo.push('找到表格 #scrollTable');
            
            // 获取表头（注意：这个表格使用 td 而不是 th）
            let thead = table.querySelector('thead');
            if (!thead) {
                return {
                    totalBlocks: 0,
                    freeBlocks: 0,
                    blocks: [],
                    currentTimes: [],
                    error: 'thead not found',
                    debug: debugInfo
                };
            }
            
            // 查找所有包含时间的表头单元格（注意：是 td 不是 th）
            let timeHeaders = Array.from(thead.querySelectorAll('tr td'));
            debugInfo.push('找到 ' + timeHeaders.length + ' 个表头单元格(td)');
            
            let currentTimes = [];
            
            // 遍历所有td，提取时间信息
            for (let i = 0; i < timeHeaders.length; i++) {
                let td = timeHeaders[i];
                
                // 尝试多种方式提取时间
                let timeText = '';
                
                // 方法1: 查找span标签（常见于 data-v-e6c914f0="" 的span）
                let span = td.querySelector('span');
                if (span) {
                    timeText = span.innerText || span.textContent || '';
                }
                
                // 方法2: 如果span没有内容，直接读取td的文本
                if (!timeText) {
                    timeText = td.innerText || td.textContent || '';
                }
                
                timeText = timeText.trim();
                
                // 只保留包含时间格式的文本 (XX:XX-XX:XX 或 XX:XX)
                if (timeText && timeText.match(/\\d{1,2}:\\d{2}/)) {
                    currentTimes.push(timeText);
                    debugInfo.push('提取时间: ' + timeText);
                }
            }
            
            debugInfo.push('共提取 ' + currentTimes.length + ' 个时间段');
            
            // 获取所有场地行
            let tbody = table.querySelector('tbody');
            if (!tbody) {
                return {
                    totalBlocks: 0,
                    freeBlocks: 0,
                    blocks: [],
                    currentTimes: currentTimes,
                    error: 'tbody not found',
                    debug: debugInfo
                };
            }
            
            let rows = tbody.querySelectorAll('tr');
            debugInfo.push('找到 ' + rows.length + ' 行场地');
            
            rows.forEach(function(row, rowIndex) {
                // 获取场地号（第一列）
                let firstCell = row.querySelector('td:first-child');
                let venueNum = '';
                if (firstCell) {
                    let div = firstCell.querySelector('div');
                    venueNum = div ? div.innerText.trim() : firstCell.innerText.trim();
                }
                
                // 获取该行所有单元格
                let cells = Array.from(row.querySelectorAll('td'));
                
                // 从第二列开始遍历（第一列是场地号）
                for (let cellIndex = 1; cellIndex < cells.length; cellIndex++) {
                    let cell = cells[cellIndex];
                    let block = cell.querySelector('.reserveBlock');
                    if (!block) continue;
                    
                    let classList = Array.from(block.classList);
                    let text = block.innerText || block.textContent;
                    text = text.trim();
                    
                    // 判断是否可预约
                    let isFree = classList.includes('free') || 
                                (text.includes('￥') && 
                                 !text.includes('已售') && 
                                 !text.includes('校训') && 
                                 !text.includes('训练') &&
                                 !text.includes('羽毛球课') &&
                                 !text.includes('舞龙课'));
                    
                    if (!isFree) continue;
                    
                    // 对应的时间段索引
                    // 注意：如果表头第一个是场地号列，需要减1
                    let timeSlotIndex = cellIndex - 1;
                    let timeSlot = '未知时间';
                    
                    if (timeSlotIndex >= 0 && timeSlotIndex < currentTimes.length) {
                        timeSlot = currentTimes[timeSlotIndex];
                    } else {
                        // 如果索引不匹配，尝试直接使用cellIndex
                        if (cellIndex < currentTimes.length) {
                            timeSlot = currentTimes[cellIndex];
                        }
                    }
                    
                    venueBlocks.push({
                        venueNum: venueNum,
                        timeSlot: timeSlot,
                        text: text,
                        rowIndex: rowIndex,
                        colIndex: cellIndex,
                        classes: classList,
                        isFree: isFree
                    });
                }
            });
            
            debugInfo.push('找到 ' + venueBlocks.length + ' 个可用场地块');
            
            return {
                totalBlocks: venueBlocks.length,
                freeBlocks: venueBlocks.length,
                blocks: venueBlocks,
                currentTimes: currentTimes,
                debug: debugInfo
            };
        }
        
        return getVenueData();
        """
        
        result = driver.execute_script(js_code)
        
        # 打印调试信息（可选 - 设置为 False 禁用详细调试）
        ENABLE_DEBUG = False
        if ENABLE_DEBUG and result and 'debug' in result:
            print(f"  [调试] JavaScript执行信息:")
            for debug_msg in result['debug']:
                print(f"    - {debug_msg}")
                pass
        return result
    except Exception as e:
        print(f"获取JavaScript数据失败: {e}")
        return None


def reserve(reserve_time, priority, venue_name="场地", driver=driver):
    """搜索可用场地，返回所有可用场地信息列表"""
    all_available_venues = []  # 存储所有发现的可用场地信息
    
    # 轮询三天的场地：今天、明天、后天
    for day_index in range(3):
        print(f"正在检查第{day_index + 1}天的场地...")
        # 点击对应的日期按钮切换到那一天
        try:
            # 根据HTML结构：.date_box 容器内有多个 div，每个代表一天
            # day_index=0 点击第1个，day_index=1 点击第2个，依此类推
            
            # 使用JavaScript查找并点击对应的日期按钮
            click_date_js = f"""
            // 查找 .date_box 容器内的所有日期 div
            let dateContainer = document.querySelector('.date_box');
            if (dateContainer) {{
                let dateDivs = dateContainer.querySelectorAll(':scope > div');
                if (dateDivs.length > {day_index}) {{
                    // 点击对应序号的日期按钮
                    dateDivs[{day_index}].click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = driver.execute_script(click_date_js)
            if result:
                print(f"已点击日期按钮切换到第{day_index + 1}天")
                time.sleep(2)
            else:
                print(f"警告：未找到第{day_index + 1}天的日期按钮")
                pass
                    
        except Exception as e:
            print(f"切换到第{day_index + 1}天失败: {e}")
            # 继续执行，尝试在当前页面查找
            pass
            
        # 保存当前页面HTML用于调试
        try:
            if day_index == 0:  # 只保存第一天的HTML
                save_page_html(f"debug_day{day_index + 1}.html")
        except Exception as e:
            print(f"点击第{day_index + 1}天日期失败: {e}")
            continue

        # 搜索所有时间段页面的可用场地
        try:
            # 等待表格加载完成
            explicit_find('css selector', '#scrollTable')
            
            # 不强制重置到第一页，因为页面可能根据当前时间自动定位
            # 如果现在是晚上，页面可能只显示晚上的时间段
            print("从当前时间段开始搜索...")
            page_count = 0
            max_pages = 10  # 增加最大页数，因为现在查找更快
            
            # 遍历所有时间段页面
            while page_count < max_pages:
                page_count += 1
                print(f"正在搜索第 {page_count} 个时间段页面...")
                # 等待当前页面加载
                time.sleep(1.5)
                
                # 使用JavaScript获取场地数据
                venue_data = get_venue_data_from_js()
                
                if venue_data:
                    current_times = venue_data.get('currentTimes', [])
                    if current_times:
                        print(f"  当前时间段: {', '.join(current_times)}")
                        pass
                    else:
                        print(f"  ⚠️ 未获取到时间段信息")
                        pass
                    print(f"  找到 {venue_data['freeBlocks']} 个可预约场地块")
                    # 检查是否有可用场地（无需按优先级，只要有就通知）
                    free_blocks = venue_data.get('freeBlocks', 0)
                    
                    if free_blocks > 0:
                        # 找到可用场地！收集信息并发送邮件
                        blocks_info = venue_data.get('blocks', [])
                        available_list = []
                        filtered_count = 0
                        
                        # 收集所有可用场地信息，并根据时间段过滤
                        print(f"  正在收集 {len(blocks_info)} 个场地块的详细信息...")
                        for block in blocks_info:
                            venue_num = block.get('venueNum', '')
                            time_slot = block.get('timeSlot', '未知时间')
                            price = block.get('text', '')
                            
                            if venue_num and '号' in venue_num:
                                # 检查时间段是否在允许范围内
                                if not is_time_in_range(time_slot, reserve_time):
                                    filtered_count += 1
                                    print(f"    ⊗ {venue_num} | {time_slot} | {price} (不在监测时间范围内)")
                                    continue
                                
                                # 格式化显示：场地号 | 时间段 | 价格
                                venue_info_text = f"{venue_num} | {time_slot} | {price}"
                                available_list.append(venue_info_text)
                                print(f"    ✓ {venue_info_text}")
                        if filtered_count > 0:
                            print(f"  ℹ️ 已过滤 {filtered_count} 个不在监测时间范围内的场地")
                            pass
                        
                        if available_list:
                            print(f"  🎉 发现 {len(available_list)} 个可用场地！")
                            # 获取当前日期信息
                            from datetime import datetime, timedelta
                            check_date = (datetime.now() + timedelta(days=day_index)).strftime('%m月%d日')
                            
                            # 将这批可用场地信息保存到列表中
                            venue_day_info = {
                                'venue_name': venue_name,
                                'date': check_date,
                                'day_index': day_index,
                                'time_slots': current_times,
                                'available_list': available_list.copy()
                            }
                            all_available_venues.append(venue_day_info)
                            
                            print(f"  ✅ 已记录 {len(available_list)} 个可用场地信息")
                            # 不再立即发送邮件，继续搜索其他时间段和日期
                else:
                    print("  ⚠️ 无法获取场地数据")
                    pass
                
                # 尝试翻到下一页继续搜索
                try:
                        # 使用JavaScript查找并检查向右箭头是否可点击
                        check_arrow_js = """
                        // 查找 scrollTable thead 中 .arrowWrap 内的向右箭头
                        // 箭头在最后一个时间段列的.arrowWrap中
                        let table = document.querySelector('#scrollTable');
                        if (!table) return null;
                        
                        let arrowWraps = table.querySelectorAll('thead .arrowWrap');
                        
                        // 遍历所有时间段单元格，查找包含向右箭头的
                        for (let wrap of arrowWraps) {
                            let forwardArrow = wrap.querySelector('i.ivu-icon-ios-arrow-forward');
                            if (forwardArrow && forwardArrow.offsetParent !== null) {
                                // 找到可见的向右箭头
                                return forwardArrow;
                            }
                        }
                        
                        return null;
                        """
                        
                        forward_arrow = driver.execute_script(check_arrow_js)
                        
                        if forward_arrow:
                            print(f"  翻到下一个时间段页面...")
                            # 使用JavaScript点击避免被其他元素遮挡
                            driver.execute_script("arguments[0].click();", forward_arrow)
                            # 增加等待时间，防止页面跳转或加载问题
                            time.sleep(2)
                        else:
                            print("  没有更多时间段了（已到最后一页或当前时间段之后无场地）")
                            break
                except Exception as page_e:
                    print(f"  翻页时出错: {page_e}")
                    break
            
            print(f"第{day_index + 1}天搜索完成")
        except Exception as e:
            print(f"第{day_index + 1}天查找场地时出错: {str(e)}")
            continue
    
    # 返回所有收集到的可用场地信息
    print(f"\n{'='*60}")
    print(f"场馆 {venue_name} 搜索完成，共发现 {len(all_available_venues)} 个时段有可用场地")
    print(f"{'='*60}\n")
    return all_available_venues


def send_email_notification(subject_or_venue_info, body_or_time_info):
    """发送邮件通知
    
    参数:
        subject_or_venue_info: 邮件主题（如果包含换行符则视为正文的一部分）
        body_or_time_info: 邮件正文内容
    """
    try:
        email_config = configs.get('email', {})
        if not email_config:
            print("未配置邮件通知，跳过发送")
            return
        
        sender_email = email_config['sender']
        sender_password = email_config['password']
        receiver_config = email_config.get('receiver', [])
        if isinstance(receiver_config, str):
            receiver_emails = [email.strip() for email in receiver_config.replace(';', ',').split(',') if email.strip()]
        elif isinstance(receiver_config, (list, tuple, set)):
            receiver_emails = [str(email).strip() for email in receiver_config if str(email).strip()]
        else:
            raise ValueError("email.receiver 配置格式错误，应为字符串或邮箱列表")

        if not receiver_emails:
            print("未配置收件人邮箱，跳过发送")
            return

        smtp_server = email_config.get('smtp_server', 'smtp.qq.com')
        smtp_port = email_config.get('smtp_port', 465)
        
        # 创建邮件内容
        message = MIMEMultipart()
        message['From'] = formataddr(("北航场馆预约通知", sender_email))
        message['To'] = ', '.join(receiver_emails)
        
        # 判断是新格式（直接传主题）还是旧格式（传场馆信息）
        if '\n' in body_or_time_info and '━' in body_or_time_info:
            # 新格式：统一汇总邮件
            message['Subject'] = Header(subject_or_venue_info, 'utf-8')
            email_body = body_or_time_info
        else:
            # 旧格式：兼容性处理
            message['Subject'] = Header("🎉 发现可用场地！", 'utf-8')
            email_body = f"场馆：{subject_or_venue_info}\n\n{body_or_time_info}"
        
        # 邮件正文HTML格式
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2c3e50;">🎉 场地可用通知</h2>
            <p><strong>检测时间：</strong>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr style="border: 1px solid #ecf0f1;">
            <pre style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; font-family: 'Courier New', monospace; white-space: pre-wrap; word-wrap: break-word;">
{email_body}
            </pre>
            <hr style="border: 1px solid #ecf0f1;">
            <p style="font-size: 16px; color: #e74c3c; font-weight: bold;">
                ⚠️ 场地紧张，请尽快预约！
            </p>
            <p>
                <a href="https://cgyy.buaa.edu.cn" style="display: inline-block; padding: 12px 24px; background-color: #3498db; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    立即前往预约 →
                </a>
            </p>
            <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                此邮件由北航场馆预约监测系统自动发送
            </p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_emails, message.as_string())
        
        print(datetime.datetime.now().time(), f"邮件通知已发送至 {', '.join(receiver_emails)}")
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False

def pay_removed_comment(driver=driver):
    """此函数已被移除 - 不再自动支付"""
    pass


def pay(driver=driver):
    """支付功能已禁用，请手动登录系统完成支付"""
    print(datetime.datetime.now().time(), "自动支付功能已关闭，请在10分钟内手动登录完成支付！")
    print("支付地址: https://cgyy.buaa.edu.cn")
    explicit_click(
        'xpath',
        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[3]/div[7]/div[2]/button'
    )
    explicit_click(
        'css selector',
        'body > div:nth-child(18) > div.ivu-modal-wrap > div > div > div.ivu-modal-body > div.payHint > a'
    )

    driver.switch_to.window(driver.window_handles[1])

    explicit_click('css selector', '#basic > a')

    try:
        print(datetime.datetime.now().time(), '准备支付，首先检查北航支付系统是否出现故障……')
        while (explicit_find_short('xpath', '/ html / body / pre')):
            print(datetime.datetime.now().time(), '支付系统异常，尝试重新进入……')
            driver.back()
            explicit_click('css selector', '#basic > a')
    except:
        print(datetime.datetime.now().time(), '支付系统无异常，进行支付……')
        pass

    explicit_click(
        'css selector',
        '#mat-tab-content-0-0 > div > div > span:nth-child(1) > svg')
    explicit_click('css selector', '#J_changePayStyle')
    explicit_click('css selector', '#J_viewSwitcher')
    explicit_interact('css selector',
                      '#J_tLoginId').send_keys(configs['alipay']['user'])
    explicit_interact('css selector', '#payPasswd_rsainput').send_keys(
        configs['alipay']['passwd'])

    capt_code = captcha2str('class name', 'checkCodeImg', driver)

    explicit_find('class name', 'ui-input-checkcode').send_keys(capt_code)
    explicit_click('css selector', '#J_newBtn')

    driver.switch_to.window(driver.window_handles[1])
    explicit_find('class name',
                  'sixDigitPassword').send_keys(configs['alipay']['passwd'])
    explicit_click('css selector', '#J_authSubmit')

    print(datetime.datetime.now().time(), "支付成功！祝你打球愉快~")
    return None


def install_click_logger(driver):
    script = """
    (function() {
        const makePath = (el) => {
            if (!el) return '';
            if (el.id) return '#' + el.id;
            const parent = el.parentElement;
            if (!parent) return el.tagName.toLowerCase();
            const siblings = Array.from(parent.children).filter(e => e.tagName === el.tagName);
            const index = siblings.length > 1 ? `[${siblings.indexOf(el) + 1}]` : '';
            return makePath(parent) + ' > ' + el.tagName.toLowerCase() + index;
        };

        window._lastClicked = null;
        document.addEventListener('click', (event) => {
            window._lastClicked = {
                cssPath: makePath(event.target),
                tag: event.target.tagName.toLowerCase(),
                classes: event.target.className,
                text: event.target.innerText.slice(0, 50)
            };
            console.log('Clicked:', window._lastClicked);
        }, true);
    })();
    """
    driver.execute_script(script)


def get_last_clicked(driver):
    return driver.execute_script("return window._lastClicked;")


def main():

    now = datetime.datetime.now()
    begin_time_today = str(now.date()) + ' ' + begin_time
    # begin_time_dt = datetime.datetime.strptime(begin_time_today, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=1) # 0点之前使用
    begin_time_dt = datetime.datetime.strptime(begin_time_today, "%Y-%m-%d %H:%M:%S")  # 0点之后/测试时使用
    one_minute_before = begin_time_dt - datetime.timedelta(minutes=1)

    while (now < one_minute_before):
        now = datetime.datetime.now()
        print("等待到达目标时间前一分钟:", now.time())
    print(now.time(), "到达目标时间前一分钟，开始启动浏览器内核")
    driver.set_page_load_timeout(60)
    driver.get("https://cgyy.buaa.edu.cn/venue/Login")

    # 点击进入场馆预约的统一认证界面，输入用户名密码、确认
    safe_click(
        By.CSS_SELECTOR,
        'body > div.fullHeight > div > div > div > div > div.loginFlagWrap > a',
        wait_timeout=30)
    WebDriverWait(driver, 30, 0.5).until(
        EC.frame_to_be_available_and_switch_to_it("loginIframe"))
    explicit_find('id', 'unPassword').send_keys(configs['sso']['user'])
    explicit_find('id', 'pwPassword').send_keys(configs['sso']['passwd'])
    explicit_click('class name', 'submit-btn')

    # 登录成功后切回主页面并等待功能模块出现
    driver.switch_to.default_content()
    badminton_selector = "//div[contains(@class,'sports-events')]//div[contains(@class,'BUAA') and .//div[text()='羽毛球']]"
    explicit_find('xpath', badminton_selector)

    # 点击运动项目中的“羽毛球”入口
    explicit_click('xpath', badminton_selector)
    WebDriverWait(driver, 30, 0.5).until(EC.url_contains('/venue/venue-introduce'))
    badminton_list_url = driver.current_url

    now = datetime.datetime.now()
    while (now < begin_time_dt):
        now = datetime.datetime.now()
        print("等待到达目标时间:", now.time())
    print(now.time(), "到达目标时间，开始抢场地！")
    # 定义要检查的场馆列表
    venues_to_check = [
        {
            'name': '学院路校区-体育馆主馆-羽毛球',
            'selector': "//div[contains(@class,'place-item')]//h5[contains(normalize-space(.),'学院路校区-体育馆主馆-羽毛球')]"
        },
        {
            'name': '学院路校区-体育馆训练馆(副馆)-羽毛球',
            'selector': "//div[contains(@class,'place-item')]//h5[contains(normalize-space(.),'学院路校区-体育馆训练馆(副馆)-羽毛球')]"
        }
    ]
    
    all_venues_info = []  # 存储所有场馆的可用信息
    
    # 依次检查每个场馆
    for venue_idx, venue in enumerate(venues_to_check):
        print(f"\n{'='*60}")
        print(f"正在检查场馆 {venue_idx + 1}/{len(venues_to_check)}: {venue['name']}")
        print(f"{'='*60}\n")
        try:
            # 如果不是第一个场馆，直接重新加载列表页（history.back 会让 SPA 渲染进程超时）
            if venue_idx > 0:
                print("重新打开羽毛球场地列表页面...")
                driver.set_page_load_timeout(60)
                driver.get(badminton_list_url)
                WebDriverWait(driver, 30, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, venue['selector'])))
                time.sleep(2)
            
            # 点击场馆订场按钮
            book_button_selector = venue['selector']
            explicit_interact('xpath', book_button_selector).click()

            WebDriverWait(driver, 30, 0.5).until(
                EC.url_contains('/venue/venue-introduce'))
            
            # 开始检查该场馆，收集可用场地信息
            venue_available = reserve(reserve_time, priority, venue['name'])
            if venue_available:
                all_venues_info.extend(venue_available)  # 将该场馆的可用信息添加到总列表
                print(f"✅ 在 {venue['name']} 发现可用场地")
            else:
                print(f"❌ {venue['name']} 暂无可用场地")
                pass
                
        except Exception as e:
            print(f"检查场馆 {venue['name']} 时出错: {e}")
            continue
    
    # 所有场馆检查完毕，统一发送邮件
    print(f"\n{'='*60}")
    print("所有场馆检查完成！")
    print(f"{'='*60}\n")
    if all_venues_info:
        # 构建邮件内容
        print(f"共发现 {len(all_venues_info)} 个时段有可用场地，正在发送邮件通知...")
        email_subject = f"🎉 发现 {len(all_venues_info)} 个时段有可用场地！"
        email_body = "【可用场地汇总通知】\n\n"
        
        for idx, info in enumerate(all_venues_info, 1):
            email_body += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            email_body += f"【{idx}】{info['venue_name']}\n"
            email_body += f"日期：{info['date']} (第{info['day_index'] + 1}天)\n"
            email_body += f"\n可用场地（场地号 | 时间段 | 价格）：\n"
            for venue in info['available_list']:
                email_body += f"  ✓ {venue}\n"
            email_body += "\n"
        
        email_body += "━━━━━━━━━━━━━━━━━━━━━━\n"
        email_body += "请尽快登录系统预约：https://cgyy.buaa.edu.cn"
        
        # 发送邮件
        send_email_notification(email_subject, email_body)
        
        receiver_config = configs['email'].get('receiver', [])
        if isinstance(receiver_config, str):
            receiver_display = ', '.join([email.strip() for email in receiver_config.replace(';', ',').split(',') if email.strip()])
        else:
            receiver_display = ', '.join([str(email).strip() for email in receiver_config if str(email).strip()])
        print(f"\n✅ 邮件通知已发送到 {receiver_display}")
        print("请登录系统查看详情并预约：https://cgyy.buaa.edu.cn")
    else:
        print("所有场馆都暂无可用场地。")
        pass
    
    print(f"{'='*60}\n")


if __name__ == '__main__':
    try:
        main()
    finally:
        driver.quit()
