// 获取数据 - 优先使用导入的真实数据，否则使用示例数据
function getMinistryData() {
    const importedData = localStorage.getItem('ministryData');
    if (importedData) {
        try {
            const parsed = JSON.parse(importedData);
            return { services: parsed };
        } catch (error) {
            console.warn('无法解析导入的数据，使用示例数据');
        }
    }
    
    // 示例数据（基于实际Google Sheets内容）
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
            { date: '2025-05-18', preacher: '王通', worshipLeader: '王通', series: '愿你的国降临', scripture: 'Matthew 9:1-8', soundControl: '俊鑫', director: '忠涵', proPresenter: '康康', mediaUpdate: 'Zoey' }
        ]
    };
}

// 数据处理函数 - 讲道和敬拜数据
function processData() {
    const preacherCount = {};
    const worshipLeaderCount = {};
    const seriesCount = {};
    const scriptureBooks = {};
    
    const ministryData = getMinistryData();

    ministryData.services.forEach(service => {
        // 统计讲员频率
        preacherCount[service.preacher] = (preacherCount[service.preacher] || 0) + 1;
        
        // 统计敬拜带领者频率
        worshipLeaderCount[service.worshipLeader] = (worshipLeaderCount[service.worshipLeader] || 0) + 1;
        
        // 统计讲道系列
        seriesCount[service.series] = (seriesCount[service.series] || 0) + 1;
        
        // 提取经文书卷
        const book = service.scripture.split(' ')[0];
        scriptureBooks[book] = (scriptureBooks[book] || 0) + 1;
    });

    return { preacherCount, worshipLeaderCount, seriesCount, scriptureBooks };
}

// 媒体部数据处理函数
function processMediaData() {
    const soundControlCount = {};
    const directorCount = {};
    const proPresenterCount = {};
    const mediaUpdateCount = {};
    const mediaRoleDistribution = {};
    
    const ministryData = getMinistryData();

    ministryData.services.forEach(service => {
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

// 创建讲员频率图表
function createPreacherChart(data) {
    const ctx = document.getElementById('preacherChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.preacherCount),
            datasets: [{
                label: '讲道次数',
                data: Object.values(data.preacherCount),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0'
                ],
                borderColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '各讲员服侍频率统计'
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

// 创建敬拜带领者饼图
function createWorshipLeaderChart(data) {
    const ctx = document.getElementById('worshipLeaderChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data.worshipLeaderCount),
            datasets: [{
                data: Object.values(data.worshipLeaderCount),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '敬拜带领者分布'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 创建讲道系列图表
function createSermonSeriesChart(data) {
    const ctx = document.getElementById('sermonSeriesChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.seriesCount),
            datasets: [{
                data: Object.values(data.seriesCount),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '讲道系列分布'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 创建经文书卷图表
function createScriptureChart(data) {
    const ctx = document.getElementById('scriptureChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.scriptureBooks),
            datasets: [{
                label: '使用次数',
                data: Object.values(data.scriptureBooks),
                backgroundColor: '#36A2EB',
                borderColor: '#36A2EB',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: '经文书卷使用频率'
                }
            },
            scales: {
                x: {
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

// 全局变量控制当前显示的页面
let currentView = 'preaching';

// 切换视图函数
function switchView(view) {
    currentView = view;
    
    // 隐藏所有图表容器和标题
    const allContainers = document.querySelectorAll('.chart-container');
    allContainers.forEach(container => {
        container.style.display = 'none';
    });
    
    // 隐藏所有标题
    document.getElementById('preachingTitle').style.display = 'none';
    document.getElementById('mediaTitle').style.display = 'none';
    
    // 更新导航按钮状态
    const allButtons = document.querySelectorAll('.nav-button');
    allButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    if (view === 'preaching') {
        // 显示讲道相关图表和标题
        document.getElementById('preachingTitle').style.display = 'block';
        document.getElementById('preacherContainer').style.display = 'block';
        document.getElementById('worshipLeaderContainer').style.display = 'block';
        document.getElementById('sermonSeriesContainer').style.display = 'block';
        document.getElementById('scriptureContainer').style.display = 'block';
        document.getElementById('preachingNav').classList.add('active');
    } else if (view === 'media') {
        // 显示媒体部图表和标题
        document.getElementById('mediaTitle').style.display = 'block';
        document.getElementById('soundControlContainer').style.display = 'block';
        document.getElementById('directorContainer').style.display = 'block';
        document.getElementById('proPresenterContainer').style.display = 'block';
        document.getElementById('mediaRoleContainer').style.display = 'block';
        document.getElementById('mediaNav').classList.add('active');
    }
}

// 页面加载完成后初始化图表
document.addEventListener('DOMContentLoaded', function() {
    const processedData = processData();
    const mediaData = processMediaData();
    
    // 创建讲道相关图表
    createPreacherChart(processedData);
    createWorshipLeaderChart(processedData);
    createSermonSeriesChart(processedData);
    createScriptureChart(processedData);
    
    // 创建媒体部图表
    createSoundControlChart(mediaData);
    createDirectorChart(mediaData);
    createProPresenterChart(mediaData);
    createMediaRoleChart(mediaData);
    
    // 默认显示讲道视图
    switchView('preaching');
});

// 导出功能
function exportChartData() {
    const data = processData();
    const ministryData = getMinistryData();
    const exportData = {
        summary: {
            totalServices: ministryData.services.length,
            dateRange: '2025-01-05 到 2025-05-18',
            mainPreacher: '王通',
            mainSeries: '愿你的国降临'
        },
        statistics: data
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ministry-data-analysis.json';
    link.click();
}