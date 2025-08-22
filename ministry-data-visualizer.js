// Google Sheets配置
const GOOGLE_SHEETS_CONFIG = {
    spreadsheetId: '1wescUQe9rIVLNcKdqmSLpzlAw9BGXMZmkFvjEF296nM',
    sheetName: 'Sheet1', // 或者实际的工作表名称
    range: 'A:Z' // 获取所有列
};

// 全局变量
let globalMinistryData = null;
let selectedYear = '2025'; // 默认选择2025年

// 从Google Sheets API获取数据
async function fetchGoogleSheetsData() {
    const { spreadsheetId, sheetName, range } = GOOGLE_SHEETS_CONFIG;
    const csvUrl = `https://docs.google.com/spreadsheets/d/${spreadsheetId}/gviz/tq?tqx=out:csv&sheet=${sheetName}&range=${range}`;
    
    try {
        console.log('正在从Google Sheets获取数据...');
        const response = await fetch(csvUrl);
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        const csvText = await response.text();
        console.log('CSV数据获取成功，长度:', csvText.length);
        return parseCSVData(csvText);
    } catch (error) {
        console.error('获取Google Sheets数据失败:', error);
        return null;
    }
}

// 解析CSV数据 - 从第55行开始（2025年数据）
function parseCSVData(csvText) {
    const lines = csvText.split('\n').filter(line => line.trim());
    if (lines.length === 0) return [];
    
    // 解析表头
    const headers = parseCSVRow(lines[0]);
    console.log('表头:', headers);
    console.log('总行数:', lines.length);
    
    const data = [];
    // 从第55行开始（索引54，因为第0行是表头），这是2025年数据的开始
    const startRow = Math.min(54, lines.length - 1);
    console.log(`从第${startRow + 1}行开始解析（2025年数据起点）`);
    
    for (let i = Math.max(1, startRow); i < lines.length; i++) {
        const values = parseCSVRow(lines[i]);
        if (values.length === 0) continue;
        
        const row = {};
        headers.forEach((header, index) => {
            row[header.trim()] = values[index] ? values[index].trim() : '';
        });
        
        // 只包含有日期的行
        if (row[headers[0]] && row[headers[0]].match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/)) {
            data.push(row);
        }
    }
    
    console.log('解析完成，数据行数:', data.length);
    return data;
}

// 解析CSV行（处理引号包围的内容）
function parseCSVRow(row) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < row.length; i++) {
        const char = row[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current);
    return result;
}

// 处理API数据，标准化格式
function processApiData(rawData) {
    return rawData.map(row => {
        // 根据实际的Google Sheets列映射到标准字段
        const processedRow = {
            date: formatDate(row['主日日期'] || row['日期'] || row['Date'] || ''),
            soundControl: row['音控'] || row['音响控制'] || '',
            director: row['导播/摄影'] || row['导播'] || row['摄影'] || '',
            proPresenter: row['ProPresenter播放'] || row['ProPresenter'] || '',
            mediaUpdate: row['ProPresenter更新'] || row['媒体更新'] || '',
            // 保留其他可能有用的字段
            preacher: row['讲员'] || row['牧师'] || '',
            worshipLeader: row['敬拜带领'] || row['敬拜'] || '',
            series: row['讲道系列'] || row['系列'] || '',
            scripture: row['经文'] || row['圣经'] || ''
        };
        
        // 过滤掉空的日期行
        return processedRow.date ? processedRow : null;
    }).filter(row => row !== null);
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    // 尝试解析不同的日期格式
    const dateFormats = [
        /(\d{4})[-/](\d{1,2})[-/](\d{1,2})/,  // 2025-01-05 或 2025/1/5
        /(\d{1,2})[-/](\d{1,2})[-/](\d{4})/   // 1/5/2025 或 01-05-2025
    ];
    
    for (const format of dateFormats) {
        const match = dateStr.match(format);
        if (match) {
            let year, month, day;
            if (match[1].length === 4) {
                // YYYY-MM-DD format
                [, year, month, day] = match;
            } else {
                // MM-DD-YYYY format
                [, month, day, year] = match;
            }
            
            // 确保两位数格式
            month = month.padStart(2, '0');
            day = day.padStart(2, '0');
            
            return `${year}-${month}-${day}`;
        }
    }
    
    return dateStr; // 如果无法解析，返回原始值
}

// 按年份过滤数据
function filterDataByYear(data, year) {
    console.log(`开始按年份过滤数据，目标年份: ${year}, 原始数据条数: ${data.length}`);
    
    if (year === 'all') {
        console.log('选择了所有年份，返回全部数据');
        return data;
    }
    
    const filtered = data.filter(service => {
        if (!service.date) {
            console.log('发现空日期记录，跳过');
            return false;
        }
        const serviceYear = service.date.split('-')[0];
        const match = serviceYear === year;
        console.log(`服务日期: ${service.date}, 提取年份: ${serviceYear}, 匹配${year}: ${match}`);
        return match;
    });
    
    console.log(`年份过滤结果: ${filtered.length}/${data.length} 条记录`);
    
    if (filtered.length === 0) {
        console.warn(`警告: 没有找到${year}年的数据！`);
        console.log('可用的年份数据:');
        const availableYears = [...new Set(data.map(s => s.date ? s.date.split('-')[0] : 'no-date'))];
        availableYears.forEach(y => console.log(`- ${y}`));
    }
    
    return filtered;
}

// 年份变更处理函数
async function changeYear() {
    const yearSelect = document.getElementById('yearSelect');
    selectedYear = yearSelect.value;
    
    console.log('切换到年份:', selectedYear);
    
    // 使用全局数据重新渲染图表
    if (globalMinistryData) {
        await renderChartsWithYear(selectedYear);
    }
}

// 按年份渲染图表
async function renderChartsWithYear(year, showLoadingIndicator = true) {
    try {
        if (showLoadingIndicator) {
            showLoading(`正在加载 ${year === 'all' ? '所有年份' : year + '年'} 的数据...`);
        }
        
        // 过滤数据
        const filteredData = filterDataByYear(globalMinistryData.services, year);
        const filteredMinistryData = { services: filteredData };
        
        console.log(`年份${year}过滤后数据:`, filteredData.length, '条');
        
        // 计算媒体数据
        const mediaData = await processMediaDataWithYear(filteredMinistryData, year);
        const lastSundayStr = getLastSunday();
        
        // 应用时间过滤（只在非"所有年份"时应用）
        let finalFilteredServices = filteredData;
        if (year !== 'all') {
            finalFilteredServices = filteredData.filter(service => service.date <= lastSundayStr);
        }
        
        console.log(`最终过滤后数据:`, finalFilteredServices.length, '条');
        
        // 更新数据源信息
        const dataSource = document.querySelector('.data-source');
        const yearInfo = document.getElementById('yearInfo');
        
        if (dataSource) {
            dataSource.innerHTML = `
                <strong>数据来源：</strong>Google Sheets API - 媒体技术服侍岗位<br>
                <strong>分析年份：</strong>${year === 'all' ? '所有年份' : year + '年'}<br>
                <strong>分析记录：</strong>${finalFilteredServices.length} 个主日服侍记录
            `;
        }
        
        if (yearInfo) {
            yearInfo.textContent = `(${finalFilteredServices.length} 条记录)`;
        }
        
        // 清除现有图表
        clearExistingCharts();
        
        if (showLoadingIndicator) {
            hideLoading();
        }
        
        // 重新创建图表
        createSoundControlChart(mediaData);
        createDirectorChart(mediaData);
        createProPresenterChart(mediaData);
        createMediaRoleChart(mediaData);
        
        console.log('图表创建完成');
        
    } catch (error) {
        if (showLoadingIndicator) {
            hideLoading();
        }
        console.error('按年份渲染图表失败:', error);
        throw error; // 重新抛出错误以便上层处理
    }
}

// 清除现有图表
function clearExistingCharts() {
    const chartElements = ['soundControlChart', 'directorChart', 'proPresenterChart', 'mediaRoleChart'];
    chartElements.forEach(chartId => {
        const canvas = document.getElementById(chartId);
        if (canvas) {
            const context = canvas.getContext('2d');
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    });
}

// 获取数据 - 优先从API获取，然后本地存储，最后使用示例数据
async function getMinistryData() {
    // 首先尝试从localStorage获取缓存的API数据
    const cachedApiData = localStorage.getItem('apiMinistryData');
    const cacheTime = localStorage.getItem('apiDataCacheTime');
    const currentTime = new Date().getTime();
    
    // 如果缓存存在且在1小时内，直接使用缓存
    if (cachedApiData && cacheTime && (currentTime - parseInt(cacheTime)) < 3600000) {
        try {
            const parsed = JSON.parse(cachedApiData);
            console.log('使用缓存的API数据');
            return { services: parsed };
        } catch (error) {
            console.warn('无法解析缓存的API数据');
        }
    }
    
    // 尝试从API获取数据
    const apiData = await fetchGoogleSheetsData();
    if (apiData && apiData.length > 0) {
        // 处理并标准化数据格式
        const processedData = processApiData(apiData);
        
        // 缓存API数据
        localStorage.setItem('apiMinistryData', JSON.stringify(processedData));
        localStorage.setItem('apiDataCacheTime', currentTime.toString());
        
        console.log('使用API数据，记录数:', processedData.length);
        return { services: processedData };
    }
    
    // 如果API失败，尝试使用用户导入的数据
    const importedData = localStorage.getItem('ministryData');
    if (importedData) {
        try {
            const parsed = JSON.parse(importedData);
            console.log('使用导入的数据');
            return { services: parsed };
        } catch (error) {
            console.warn('无法解析导入的数据');
        }
    }
    
    console.log('使用示例数据');
    
    // 示例数据（扩展到2025年8月，覆盖更多主日）
    return {
        services: [
            { date: '2025-01-05', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 5:33-37', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-01-12', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 5:38-48', soundControl: '俊鑫', director: '忠涵', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-01-19', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 6:1-4', soundControl: 'Jimmy', director: 'Jason', proPresenter: '康康', mediaUpdate: '俊鑫' },
            { date: '2025-01-26', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 6:5-15', soundControl: '俊鑫', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: 'Zoey' },
            { date: '2025-02-02', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 6:16-18', soundControl: 'Jimmy', director: '忠涵', proPresenter: '俊鑫', mediaUpdate: '康康' },
            { date: '2025-02-09', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 6:19-24', soundControl: '俊鑫', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-02-16', preacher: '周明哲传道', worshipLeader: '王通', series: '单篇证道', scripture: 'Mark 11:41-12:1-2', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-02-23', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 6:25-34', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-03-02', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 7:1-6', soundControl: 'Jimmy', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-03-09', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 7:7-12', soundControl: '俊鑫', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-03-16', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 7:13-20', soundControl: 'Jimmy', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-03-23', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 7:21-29', soundControl: '俊鑫', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-03-30', preacher: '王通', worshipLeader: '王通', series: '复活节特别聚会', scripture: 'Luke 24:1-12', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-04-06', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:1-4', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-04-13', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:5-13', soundControl: 'Jimmy', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-04-20', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:14-17', soundControl: '俊鑫', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-04-27', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:18-22', soundControl: 'Jimmy', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-05-04', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:23-27', soundControl: '俊鑫', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-05-11', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 8:28-34', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-05-18', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 9:1-8', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            // 继续添加5-8月的数据
            { date: '2025-05-25', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 9:9-13', soundControl: 'Jimmy', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-06-01', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 9:14-17', soundControl: '俊鑫', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '康康' },
            { date: '2025-06-08', preacher: '周明哲传道', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 9:18-26', soundControl: 'Jimmy', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-06-15', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 9:27-31', soundControl: '俊鑫', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-06-22', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 9:32-38', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-06-29', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 10:1-4', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-07-06', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 10:5-15', soundControl: 'Jimmy', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-07-13', preacher: '周明哲传道', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 10:16-23', soundControl: '俊鑫', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '康康' },
            { date: '2025-07-20', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 10:24-33', soundControl: 'Jimmy', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-07-27', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 10:34-42', soundControl: '俊鑫', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' },
            { date: '2025-08-03', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 11:1-6', soundControl: 'Jimmy', director: 'Gavin', proPresenter: 'Jimmy', mediaUpdate: '俊鑫' },
            { date: '2025-08-10', preacher: '王通', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 11:7-15', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' },
            { date: '2025-08-17', preacher: '周明哲传道', worshipLeader: '王通', series: '夏季系列', scripture: 'Matthew 11:16-24', soundControl: 'Jimmy', director: 'Jason', proPresenter: 'Zoey', mediaUpdate: 'Jimmy' }
        ]
    };
}

// 计算当前日期前的最后一个周日
function getLastSunday() {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const daysToSubtract = dayOfWeek === 0 ? 7 : dayOfWeek; // 如果今天是周日，则取上周日
    const lastSunday = new Date(today.getTime() - daysToSubtract * 24 * 60 * 60 * 1000);
    return lastSunday.toISOString().split('T')[0]; // 返回YYYY-MM-DD格式
}

// 显示原始数据 - 只显示媒体部相关数据
async function showRawData() {
    try {
        console.log('=== 开始显示原始数据 ===');
        
        const ministryData = globalMinistryData || await getMinistryData();
        const modal = document.getElementById('rawDataModal');
        const content = document.getElementById('rawDataContent');
        
        if (!modal || !content) {
            console.error('找不到模态框元素');
            alert('找不到数据显示窗口，请检查页面是否正确加载');
            return;
        }
        
        const lastSundayStr = getLastSunday();
        
        // 添加详细调试信息
        console.log('总数据条数:', ministryData.services.length);
        console.log('选择年份:', selectedYear);
        console.log('当前日期前最后一个周日:', lastSundayStr);
        console.log('今日日期:', new Date().toISOString().split('T')[0]);
        
        // 显示前几条原始数据样本
        console.log('前5条原始数据样本:');
        ministryData.services.slice(0, 5).forEach((service, index) => {
            console.log(`${index}: ${service.date} - 音控:${service.soundControl || '无'} - 导播:${service.director || '无'}`);
        });
        
        // 定义媒体部相关字段
        const mediaFields = ['date', 'soundControl', 'director', 'proPresenter', 'mediaUpdate'];
        const mediaFieldNames = {
            'date': '日期',
            'soundControl': '音控',
            'director': '导播/摄影', 
            'proPresenter': 'ProPresenter',
            'mediaUpdate': '媒体更新'
        };
        
        // 首先按年份过滤
        console.log('开始年份过滤...');
        let yearFilteredServices = filterDataByYear(ministryData.services, selectedYear);
        
        // 显示年份过滤后的数据样本
        console.log('年份过滤后前3条数据:');
        yearFilteredServices.slice(0, 3).forEach((service, index) => {
            console.log(`${index}: ${service.date} - 音控:${service.soundControl || '无'}`);
        });
        
        // 然后按时间过滤（如果不是查看所有年份）
        let filteredServices = yearFilteredServices;
        if (selectedYear !== 'all') {
            console.log('开始时间过滤...');
            filteredServices = yearFilteredServices.filter(service => {
                const include = service.date <= lastSundayStr;
                console.log(`日期 ${service.date} <= ${lastSundayStr}: ${include ? '包含' : '排除'}`);
                return include;
            });
        }
        
        console.log('年份过滤后:', yearFilteredServices.length, '条');
        console.log('时间过滤后:', filteredServices.length, '条');
        
        // 显示最终过滤后的数据
        console.log('最终过滤后的数据:');
        filteredServices.forEach((service, index) => {
            console.log(`${index}: ${service.date} - 音控:${service.soundControl || '无'} - 导播:${service.director || '无'}`);
        });
    
    let html = '<div style="margin-bottom: 15px;">';
    html += `<p><strong>选择年份：</strong>${selectedYear === 'all' ? '所有年份' : selectedYear + '年'}</p>`;
    if (selectedYear !== 'all') {
        html += `<p><strong>数据截止日期：</strong>${lastSundayStr} (当前日期前的最后一个周日)</p>`;
    }
    html += `<p><strong>显示字段：</strong>媒体部相关服侍岗位</p>`;
    html += '</div>';
    
    html += '<table border="1" style="border-collapse: collapse; width: 100%; font-size: 14px;">';
    
    if (filteredServices.length > 0) {
        // 表头 - 只显示媒体部相关字段
        html += '<thead><tr>';
        mediaFields.forEach(field => {
            html += `<th style="padding: 8px; background: #f0f0f0; border: 1px solid #ddd;">${mediaFieldNames[field] || field}</th>`;
        });
        html += '</tr></thead>';
        
        // 数据行
        html += '<tbody>';
        filteredServices.forEach((service, index) => {
            html += `<tr style="${index % 2 === 0 ? 'background: #f9f9f9' : ''}">`;
            mediaFields.forEach(field => {
                const value = service[field] || '';
                html += `<td style="padding: 8px; border: 1px solid #ddd;">${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody>';
    } else {
        html += '<tr><td colspan="' + mediaFields.length + '" style="padding: 20px; text-align: center;">没有找到符合条件的数据</td></tr>';
    }
    
    html += '</table>';
    html += `<div style="margin-top: 15px;">`;
    html += `<p><strong>显示记录数：</strong>${filteredServices.length} / ${ministryData.services.length}</p>`;
    html += `<p><strong>今日日期：</strong>${new Date().toISOString().split('T')[0]}</p>`;
    html += `</div>`;
        
        content.innerHTML = html;
        modal.style.display = 'block';
        
        console.log('原始数据显示完成');
        
    } catch (error) {
        console.error('显示原始数据失败:', error);
        alert('显示原始数据失败: ' + error.message);
    }
}

function closeRawData() {
    document.getElementById('rawDataModal').style.display = 'none';
}

// 媒体部数据处理函数 - 只处理到当前日期前最后一个周日的数据
function processMediaData() {
    const soundControlCount = {};
    const directorCount = {};
    const proPresenterCount = {};
    const mediaUpdateCount = {};
    const mediaRoleDistribution = {};
    
    const ministryData = getMinistryData();
    const lastSundayStr = getLastSunday();
    
    // 过滤数据：只包括到当前日期前的最后一个周日
    const filteredServices = ministryData.services.filter(service => {
        return service.date <= lastSundayStr;
    });

    filteredServices.forEach(service => {
        // 统计音控服侍频率
        if (service.soundControl) {
            soundControlCount[service.soundControl] = (soundControlCount[service.soundControl] || 0) + 1;
        }
        
        // 统计导播/摄影频率
        if (service.director) {
            directorCount[service.director] = (directorCount[service.director] || 0) + 1;
        }
        
        // 统计ProPresenter操作频率
        if (service.proPresenter) {
            proPresenterCount[service.proPresenter] = (proPresenterCount[service.proPresenter] || 0) + 1;
        }
        
        // 统计媒体更新频率
        if (service.mediaUpdate) {
            mediaUpdateCount[service.mediaUpdate] = (mediaUpdateCount[service.mediaUpdate] || 0) + 1;
        }
        
        // 统计每个人参与的媒体角色
        const roles = ['soundControl', 'director', 'proPresenter', 'mediaUpdate'];
        roles.forEach(role => {
            const person = service[role];
            if (person) {
                if (!mediaRoleDistribution[person]) {
                    mediaRoleDistribution[person] = { soundControl: 0, director: 0, proPresenter: 0, mediaUpdate: 0, total: 0 };
                }
                mediaRoleDistribution[person][role]++;
                mediaRoleDistribution[person].total++;
            }
        });
    });

    return { 
        soundControlCount, 
        directorCount, 
        proPresenterCount, 
        mediaUpdateCount, 
        mediaRoleDistribution 
    };
}

// 创建音控服侍频率图表
function createSoundControlChart(data) {
    const ctx = document.getElementById('soundControlChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.soundControlCount),
            datasets: [{
                label: '音控服侍次数',
                data: Object.values(data.soundControlCount),
                backgroundColor: '#FF6384',
                borderColor: '#FF6384',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '音控服侍频率统计'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '次数'
                    }
                }
            }
        }
    });
}

// 创建导播/摄影服侍频率图表
function createDirectorChart(data) {
    const ctx = document.getElementById('directorChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.directorCount),
            datasets: [{
                label: '导播/摄影服侍次数',
                data: Object.values(data.directorCount),
                backgroundColor: '#36A2EB',
                borderColor: '#36A2EB',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '导播/摄影服侍频率统计'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '次数'
                    }
                }
            }
        }
    });
}

// 创建ProPresenter操作频率图表
function createProPresenterChart(data) {
    const ctx = document.getElementById('proPresenterChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data.proPresenterCount),
            datasets: [{
                data: Object.values(data.proPresenterCount),
                backgroundColor: [
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'ProPresenter操作分布'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 创建媒体角色综合分析图表
function createMediaRoleChart(data) {
    const ctx = document.getElementById('mediaRoleChart').getContext('2d');
    
    const people = Object.keys(data.mediaRoleDistribution);
    const datasets = [
        {
            label: '音控',
            data: people.map(person => data.mediaRoleDistribution[person].soundControl),
            backgroundColor: '#FF6384'
        },
        {
            label: '导播/摄影',
            data: people.map(person => data.mediaRoleDistribution[person].director),
            backgroundColor: '#36A2EB'
        },
        {
            label: 'ProPresenter',
            data: people.map(person => data.mediaRoleDistribution[person].proPresenter),
            backgroundColor: '#FFCE56'
        },
        {
            label: '媒体更新',
            data: people.map(person => data.mediaRoleDistribution[person].mediaUpdate),
            backgroundColor: '#4BC0C0'
        }
    ];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: people,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '媒体部成员角色分布统计'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '服侍次数'
                    }
                }
            }
        }
    });
}

// 显示加载状态
function showLoading(message = '正在加载数据...') {
    // 先隐藏已存在的loading
    hideLoading();
    
    const container = document.querySelector('.container');
    if (!container) {
        console.error('找不到容器元素');
        return;
    }
    
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingStatus';
    loadingDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
        z-index: 10000;
        border: 1px solid #ddd;
    `;
    loadingDiv.innerHTML = `
        <div style="margin-bottom: 15px;">
            <div class="loading-spinner" style="display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #2196F3; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        </div>
        <div style="color: #333; font-size: 14px;">${message}</div>
    `;
    
    // 添加CSS动画
    if (!document.getElementById('loadingCSS')) {
        const style = document.createElement('style');
        style.id = 'loadingCSS';
        style.innerHTML = `
            @keyframes spin { 
                0% { transform: rotate(0deg); } 
                100% { transform: rotate(360deg); } 
            }
        `;
        document.head.appendChild(style);
    }
    
    // 添加背景遮罩
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.3);
        z-index: 9999;
    `;
    
    document.body.appendChild(overlay);
    document.body.appendChild(loadingDiv);
    
    console.log('Loading显示:', message);
}

// 隐藏加载状态
function hideLoading() {
    const loadingDiv = document.getElementById('loadingStatus');
    const overlay = document.getElementById('loadingOverlay');
    
    if (loadingDiv) {
        loadingDiv.remove();
    }
    if (overlay) {
        overlay.remove();
    }
    
    console.log('Loading隐藏');
}

// 初始化应用
async function initializeApp() {
    try {
        console.log('开始初始化应用...');
        showLoading('正在从Google Sheets获取数据...');
        
        // 获取并保存全局数据
        console.log('获取数据中...');
        globalMinistryData = await getMinistryData();
        console.log('数据获取完成，条数:', globalMinistryData?.services?.length || 0);
        
        // 按默认年份（2025）过滤和显示数据
        console.log('开始渲染图表...');
        await renderChartsWithYear(selectedYear, false); // 不显示重复的loading
        
        hideLoading();
        console.log('应用初始化完成');
        
    } catch (error) {
        hideLoading();
        console.error('初始化应用失败:', error);
        
        // 显示错误信息
        const dataSource = document.querySelector('.data-source');
        if (dataSource) {
            dataSource.innerHTML = `
                <strong style="color: #ff4444;">数据加载失败：</strong>${error.message}<br>
                <strong>说明：</strong>正在使用示例数据进行演示
            `;
        }
        
        // 使用示例数据初始化
        try {
            console.log('尝试使用示例数据...');
            globalMinistryData = await getMinistryData();
            await renderChartsWithYear(selectedYear, false);
            console.log('示例数据加载完成');
        } catch (fallbackError) {
            console.error('示例数据加载也失败了:', fallbackError);
        }
    }
}

// 异步版本的媒体数据处理函数
async function processMediaDataAsync(ministryData) {
    return processMediaDataWithYear(ministryData, selectedYear);
}

// 按年份处理媒体数据
async function processMediaDataWithYear(ministryData, year) {
    const soundControlCount = {};
    const directorCount = {};
    const proPresenterCount = {};
    const mediaUpdateCount = {};
    const mediaRoleDistribution = {};
    
    let filteredServices = ministryData.services;
    
    // 如果不是查看所有年份，应用时间过滤
    if (year !== 'all') {
        const lastSundayStr = getLastSunday();
        filteredServices = ministryData.services.filter(service => {
            return service.date <= lastSundayStr;
        });
    }

    filteredServices.forEach(service => {
        // 统计音控服侍频率
        if (service.soundControl) {
            soundControlCount[service.soundControl] = (soundControlCount[service.soundControl] || 0) + 1;
        }
        
        // 统计导播/摄影频率
        if (service.director) {
            directorCount[service.director] = (directorCount[service.director] || 0) + 1;
        }
        
        // 统计ProPresenter操作频率
        if (service.proPresenter) {
            proPresenterCount[service.proPresenter] = (proPresenterCount[service.proPresenter] || 0) + 1;
        }
        
        // 统计媒体更新频率
        if (service.mediaUpdate) {
            mediaUpdateCount[service.mediaUpdate] = (mediaUpdateCount[service.mediaUpdate] || 0) + 1;
        }
        
        // 统计每个人参与的媒体角色
        const roles = ['soundControl', 'director', 'proPresenter', 'mediaUpdate'];
        roles.forEach(role => {
            const person = service[role];
            if (person) {
                if (!mediaRoleDistribution[person]) {
                    mediaRoleDistribution[person] = { soundControl: 0, director: 0, proPresenter: 0, mediaUpdate: 0, total: 0 };
                }
                mediaRoleDistribution[person][role]++;
                mediaRoleDistribution[person].total++;
            }
        });
    });

    return { 
        soundControlCount, 
        directorCount, 
        proPresenterCount, 
        mediaUpdateCount, 
        mediaRoleDistribution 
    };
}

// 测试loading功能
function testLoading() {
    console.log('测试Loading...');
    showLoading('测试Loading显示...');
    
    setTimeout(() => {
        hideLoading();
        console.log('测试完成');
    }, 3000);
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，开始初始化...');
    
    // 添加测试按钮（仅用于调试）
    const container = document.querySelector('.container');
    if (container && window.location.search.includes('debug')) {
        const debugBtn = document.createElement('button');
        debugBtn.textContent = '测试Loading';
        debugBtn.onclick = testLoading;
        debugBtn.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 10001; background: red; color: white; padding: 5px;';
        document.body.appendChild(debugBtn);
    }
    
    initializeApp();
});

// 手动刷新数据
async function refreshData() {
    try {
        showLoading('正在重新获取数据...');
        
        // 清除缓存
        localStorage.removeItem('apiMinistryData');
        localStorage.removeItem('apiDataCacheTime');
        
        // 重新初始化
        await initializeApp();
        
    } catch (error) {
        hideLoading();
        console.error('刷新数据失败:', error);
        alert('刷新数据失败: ' + error.message);
    }
}

// 导出功能
async function exportChartData() {
    try {
        const ministryData = await getMinistryData();
        const mediaData = await processMediaDataAsync(ministryData);
        const lastSundayStr = getLastSunday();
        
        const filteredServices = ministryData.services.filter(service => service.date <= lastSundayStr);
        
        const exportData = {
            summary: {
                totalServices: ministryData.services.length,
                filteredServices: filteredServices.length,
                dateRange: `截止到 ${lastSundayStr}`,
                totalMediaMembers: Object.keys(mediaData.mediaRoleDistribution).length
            },
            mediaStatistics: mediaData,
            rawData: filteredServices,
            exportTime: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `media-ministry-analysis-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
    } catch (error) {
        console.error('导出数据失败:', error);
        alert('导出数据失败: ' + error.message);
    }
}