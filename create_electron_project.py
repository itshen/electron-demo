import os
import subprocess
import sys
import json
from pathlib import Path
import time

def check_command(command, name):
    try:
        result = subprocess.run([command, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        version = result.stdout.decode().strip()
        print(f"{name} 已安装，版本: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"{name} 未安装或无法识别。")
        print(f"错误信息: {e}")
        print("请确保 Node.js 和 npm 已正确安装并添加到系统 PATH 中。")
        print(f"当前 PATH: {os.environ.get('PATH')}")
        sys.exit(1)

def run_command(command, cwd=None):
    try:
        subprocess.run(command, check=True, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"运行命令时出错: {' '.join(command)}")
        print(e)
        sys.exit(1)

def create_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"创建文件: {path}")
    except Exception as e:
        print(f"创建文件 {path} 时出错: {e}")
        sys.exit(1)

def ensure_config(path):
    config_path = path / 'config.json'
    if not config_path.exists():
        default_config = {
            "menuBarVisible": False,
            "hideScrollBar": True
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"创建默认配置文件: {config_path}")
    return config_path

def update_package_json(path):
    package_json = path / 'package.json'
    try:
        with open(package_json, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        # 更新现有配置
        package['main'] = 'main.js'
        package['scripts']['start'] = 'electron .'
        
        # 添加打包相关配置
        package['scripts']['build'] = 'electron-builder'
        package['build'] = {
            "appId": "com.luoxiaoshan.cheshire",
            "productName": "CheshireDemo",
            "directories": {
                "output": "dist"
            },
            "win": {
                "target": [
                    "nsis"
                ],
                "icon": "static/icon.ico"
            },
            "nsis": {
                "oneClick": False,
                "allowToChangeInstallationDirectory": True,
                "createDesktopShortcut": True,
                "createStartMenuShortcut": True,
                "shortcutName": "CheshireDemo"
            }
        }
        
        with open(package_json, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        print("更新 package.json 文件。")
    except Exception as e:
        print(f"更新 package.json 时出错: {e}")
        sys.exit(1)

def create_static_files(project_path):
    # 创建 static 目录
    static_path = project_path / 'static'
    static_path.mkdir()

    # 创建 css 目录并添加 styles.css 文件
    css_path = static_path / 'css'
    css_path.mkdir()
    styles_css_content = """/* styles.css */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    background: #f7f7f7;
    overflow-y: scroll;
    padding-top: 32px;
}

.title-bar {
    background: #333;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
    color: #fff;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

/* 其他样式... */
"""
    create_file(css_path / 'styles.css', styles_css_content)

    # 创建 js 目录并添加 renderer.js 文件
    js_path = static_path / 'js'
    js_path.mkdir()
    renderer_js_content = """// renderer.js
const { ipcRenderer } = require('electron');
const { dialog } = require('@electron/remote');
const axios = require('axios');

let currentConfig = {};

// 创建一个 API 服务模块
const apiService = {
    async fetchPosts() {
        try {
            const response = await axios.get('https://jsonplaceholder.typicode.com/posts');
            return response.data;
        } catch (error) {
            console.error('获取数据时出错:', error);
            throw error;
        }
    }
};

// 初始化时获取配置并根据配置更新页面
async function loadConfig() {
    currentConfig = await ipcRenderer.invoke('get-config');
    updateUIFromConfig();
}

function updateUIFromConfig() {
    const body = document.body;
    const titleBar = document.querySelector('.title-bar');
    
    // 控制自定义标题栏显示
    if (currentConfig.menuBarVisible) {
        titleBar.style.display = 'none';  // 系统标题栏显示时，隐藏自定义标题栏
        body.style.paddingTop = '0';
        document.getElementById('btn-toggle-menu-bar').textContent = '显示自定义标题栏';
    } else {
        titleBar.style.display = 'flex';  // 系统标题栏隐藏时，显示自定义标题栏
        body.style.paddingTop = '32px';
        document.getElementById('btn-toggle-menu-bar').textContent = '显示系统标题栏';
    }

    // hideScrollBar
    if (currentConfig.hideScrollBar) {
        body.classList.add('no-scrollbar');
        document.getElementById('btn-toggle-scrollbar').textContent = '显示滚动条';
    } else {
        body.classList.remove('no-scrollbar');
        document.getElementById('btn-toggle-scrollbar').textContent = '隐藏滚动条';
    }
}

// 事件监听
document.getElementById('btn-minimize').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'minimize');
});
document.getElementById('btn-maximize').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'maximize');
});
document.getElementById('btn-close').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'close');
});

// 切换 menuBarVisible 设置
document.getElementById('btn-toggle-menu-bar').addEventListener('click', () => {
    currentConfig.menuBarVisible = !currentConfig.menuBarVisible;
    requestConfigUpdate();
});

// 切换 hideScrollBar 设置
document.getElementById('btn-toggle-scrollbar').addEventListener('click', () => {
    currentConfig.hideScrollBar = !currentConfig.hideScrollBar;
    requestConfigUpdate();
});

function requestConfigUpdate() {
    // 更新配置文件
    ipcRenderer.send('update-config', currentConfig);
}

// 当需要重启时会收到此消息
ipcRenderer.on('need-restart', () => {
    const restartPanel = document.getElementById('restart-panel');
    restartPanel.style.display = 'block';
});

document.getElementById('btn-restart-now').addEventListener('click', () => {
    ipcRenderer.send('request-restart');
});

// 使用 IPC 处理请求
document.getElementById('btn-fetch-data').addEventListener('click', async () => {
    try {
        const posts = await apiService.fetchPosts();
        console.log('获取的帖子数据:', posts);
        
        // 在这里更新 UI，例如显示帖子标题
        const postsContainer = document.getElementById('posts-container');
        postsContainer.innerHTML = ''; // 清空之前的内容
        posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.classList.add('post-card'); // 添加动画效果的类
            postElement.innerHTML = `<h3>${post.title}</h3><p>${post.body}</p>`;
            postsContainer.appendChild(postElement);
        });
    } catch (error) {
        // 处理错误
        alert('无法获取数据，请稍后再试。');
    }
});

// 初始化配置
loadConfig();
"""
    create_file(js_path / 'renderer.js', renderer_js_content)

    # 创建 SVG 文件
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 124 124" fill="none">
<rect width="124" height="124" rx="24" fill="#F97316"/>
<path d="M19.375 36.7818V100.625C19.375 102.834 21.1659 104.625 23.375 104.625H87.2181C90.7818 104.625 92.5664 100.316 90.0466 97.7966L26.2034 33.9534C23.6836 31.4336 19.375 33.2182 19.375 36.7818Z" fill="white"/>
<circle cx="63.2109" cy="37.5391" r="18.1641" fill="black"/>
<rect opacity="0.4" x="81.1328" y="80.7198" width="17.5687" height="17.3876" rx="4" transform="rotate(-45 81.1328 80.7198)" fill="#FDBA74"/>
</svg>
    """
    create_file(static_path / 'icon.svg', svg_content)

    # 将 SVG 转换为 ICO 并保存
    ico_content = """
    <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 124 124" fill="none">
        <rect width="124" height="124" rx="24" fill="#F97316"/>
        <path d="M19.375 36.7818V100.625C19.375 102.834 21.1659 104.625 23.375 104.625H87.2181C90.7818 104.625 92.5664 100.316 90.0466 97.7966L26.2034 33.9534C23.6836 31.4336 19.375 33.2182 19.375 36.7818Z" fill="white"/>
        <circle cx="63.2109" cy="37.5391" r="18.1641" fill="black"/>
        <rect opacity="0.4" x="81.1328" y="80.7198" width="17.5687" height="17.3876" rx="4" transform="rotate(-45 81.1328 80.7198)" fill="#FDBA74"/>
    </svg>
    """
    create_file(static_path / 'icon.ico', ico_content)

def main():
    print("Electron 示例项目创建脚本")
    print("============================")

    PROJECT_NAME = f"my-electron-app-{int(time.time())}"

    check_command('node', 'Node.js')
    check_command('npm', 'npm')

    project_path = Path.cwd() / PROJECT_NAME
    if project_path.exists():
        print(f"目录 '{PROJECT_NAME}' 已存在。请删除或选择其他项目名称。")
        sys.exit(1)

    project_path.mkdir()
    print(f"创建项目目录: {project_path}")

    print("\n初始化 npm 项目...")
    run_command(['npm', 'init', '-y'], cwd=project_path)

    print("\n安装 Electron...")
    run_command(['npm', 'install', 'electron', '--save-dev'], cwd=project_path)

    print("\n安装 @electron/remote...")
    run_command(['npm', 'install', '@electron/remote', '--save-prod'], cwd=project_path)
    
    print("\n安装 axios")
    run_command(['npm', 'install', 'axios', '--save-prod'], cwd=project_path)

    print("\n安装 electron-builder...")
    run_command(['npm', 'install', 'electron-builder', '--save-dev'], cwd=project_path)
    
    # 创建打包脚本
    build_bat_content = """@echo off
cd /d "%~dp0"
npm run build
"""
    create_file(project_path / 'build_electron.bat', build_bat_content)

    config_path = ensure_config(project_path)

    main_js_content = r"""const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
require('@electron/remote/main').initialize();

let win;
let config;

function loadConfig() {
  const configPath = path.join(__dirname, 'config.json');
  if (!fs.existsSync(configPath)) {
    config = { menuBarVisible: true, hideScrollBar: false };
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
  } else {
    const rawData = fs.readFileSync(configPath, 'utf-8');
    config = JSON.parse(rawData);
  }
}

function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建窗口',
          accelerator: 'CmdOrCtrl+N',
          click: () => createWindow()
        },
        { type: 'separator' },
        {
          label: '保存',
          accelerator: 'CmdOrCtrl+S',
          click: () => { /* 添加保存逻辑 */ }
        },
        { type: 'separator' },
        { 
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销', accelerator: 'CmdOrCtrl+Z' },
        { role: 'redo', label: '重做', accelerator: 'CmdOrCtrl+Y' },
        { type: 'separator' },
        { role: 'cut', label: '剪切', accelerator: 'CmdOrCtrl+X' },
        { role: 'copy', label: '复制', accelerator: 'CmdOrCtrl+C' },
        { role: 'paste', label: '粘贴', accelerator: 'CmdOrCtrl+V' },
        { role: 'selectAll', label: '全选', accelerator: 'CmdOrCtrl+A' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新加载', accelerator: 'CmdOrCtrl+R' },
        { role: 'forceReload', label: '强制重新加载', accelerator: 'CmdOrCtrl+Shift+R' },
        { type: 'separator' },
        { role: 'toggleDevTools', label: '开发者工具', accelerator: 'F12' },
        { type: 'separator' },
        { role: 'resetZoom', label: '实际大小', accelerator: 'CmdOrCtrl+0' },
        { role: 'zoomIn', label: '放大', accelerator: 'CmdOrCtrl+Plus' },
        { role: 'zoomOut', label: '缩小', accelerator: 'CmdOrCtrl+-' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '全屏', accelerator: 'F11' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { role: 'minimize', label: '最小化', accelerator: 'CmdOrCtrl+M' },
        { role: 'zoom', label: '缩放' },
        { type: 'separator' },
        { role: 'close', label: '关闭', accelerator: 'CmdOrCtrl+W' }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: async () => {
            const { dialog } = require('electron');
            await dialog.showMessageBox({
              title: '关于',
              message: '洛小山 Cheshire Demo',
              detail: '版本 1.0.0\n作者：洛小山\n一个优雅的 Electron 应用示例。',
              buttons: ['确定'],
              type: 'info'
            });
          }
        },
        {
          label: '检查更新',
          click: () => { /* 添加检查更新逻辑 */ }
        },
        { type: 'separator' },
        {
          label: '访问官网',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://your-website.com');
          }
        }
      ]
    }
  ];

  // 针对 macOS 的特殊处理
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.name,
      submenu: [
        { role: 'about', label: '关于' },
        { type: 'separator' },
        { role: 'services', label: '服务' },
        { type: 'separator' },
        { role: 'hide', label: '隐藏' },
        { role: 'hideOthers', label: '隐藏其他' },
        { role: 'unhide', label: '显示全部' },
        { type: 'separator' },
        { role: 'quit', label: '退出' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function createWindow () {
  loadConfig();

  win = new BrowserWindow({
    width: 800,
    height: 700,
    frame: config.menuBarVisible,
    resizable: true,
    autoHideMenuBar: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
      enableRemote: true
    }
  });

  require('@electron/remote/main').enable(win.webContents);

  // 注入自定义菜单样式
  win.webContents.on('dom-ready', () => {
    const menuStyle = `
      .menu-custom {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
        padding: 5px 0 !important;
      }
      
      .menuitem-custom {
        padding: 6px 24px !important;
        color: #333333 !important;
        font-size: 13px !important;
        font-family: system-ui, -apple-system, sans-serif !important;
      }
      
      .menuitem-custom:hover {
        background-color: #f5f5f5 !important;
        color: #1a73e8 !important;
      }
      
      .menuitem-custom:active {
        background-color: #e8f0fe !important;
      }
      
      .separator-custom {
        margin: 5px 0 !important;
        border-bottom: 1px solid #e0e0e0 !important;
      }
      
      .accelerator-custom {
        color: #666666 !important;
        font-size: 12px !important;
      }
      
      .submenu-custom {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1) !important;
      }
      
      .menu-custom::-webkit-scrollbar {
        width: 6px !important;
        height: 6px !important;
      }
      
      .menu-custom::-webkit-scrollbar-thumb {
        background: #c1c1c1 !important;
        border-radius: 3px !important;
      }
      
      .menu-custom::-webkit-scrollbar-track {
        background: transparent !important;
      }
    `;
    
    win.webContents.insertCSS(menuStyle);
    
    // 如果配置了隐藏滚动条
    if (config.hideScrollBar) {
      win.webContents.insertCSS('*::-webkit-scrollbar { display: none !important; }');
    }
  });

  win.loadFile('index.html');
  win.setMenuBarVisibility(config.menuBarVisible);
}

// IPC 事件

// 窗口控制
ipcMain.on('window-action', (event, action) => {
  if (!win) return;
  switch (action) {
    case 'minimize':
      win.minimize();
      break;
    case 'maximize':
      if (win.isMaximized()) {
        win.unmaximize();
      } else {
        win.maximize();
      }
      break;
    case 'close':
      win.close();
      break;
  }
});

// 用户请求更改配置（需重启生效）
ipcMain.on('update-config', (event, newConfig) => {
  const configPath = path.join(__dirname, 'config.json');
  fs.writeFileSync(configPath, JSON.stringify(newConfig, null, 2), 'utf-8');
  
  // 由于标题栏的改变需要重新创建窗口，所以这里总是需要重启
  event.reply('need-restart');
});

// 用户请求重启应用
ipcMain.on('request-restart', () => {
  app.relaunch();
  app.exit(0);
});

// 当需要重启时会收到此消息
ipcMain.on('need-restart', (event) => {
  // 发送消息到渲染进程，通知需要重启
  event.sender.send('need-restart');
});

// 处理重启按钮点击事件
// 这个部分应该在 renderer.js 中处理，而不是在 main.js 中

// 提供给渲染进程获取当前配置的接口
ipcMain.handle('get-config', () => {
  return config;
});

app.whenReady().then(() => {
  createMenu();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
"""


    preload_js_content = """// preload.js
window.addEventListener('DOMContentLoaded', () => {
    // 在此可安全地暴露所需的 Node 功能
});
"""

    renderer_js_content = r"""const { ipcRenderer } = require('electron');
const { dialog } = require('@electron/remote');
const axios = require('axios');

let currentConfig = {};

// 创建一个 API 服务模块
const apiService = {
    async fetchPosts() {
        try {
            const response = await axios.get('https://jsonplaceholder.typicode.com/posts');
            return response.data;
        } catch (error) {
            console.error('获取数据时出错:', error);
            throw error;
        }
    }
};

// 初始化时获取配置并根据配置更新页面
async function loadConfig() {
    currentConfig = await ipcRenderer.invoke('get-config');
    updateUIFromConfig();
}

function updateUIFromConfig() {
    const body = document.body;
    const titleBar = document.querySelector('.title-bar');
    
    // 控制自定义标题栏显示
    if (currentConfig.menuBarVisible) {
        titleBar.style.display = 'none';  // 系统标题栏显示时，隐藏自定义标题栏
        body.style.paddingTop = '0';
        document.getElementById('btn-toggle-menu-bar').textContent = '显示自定义标题栏';
    } else {
        titleBar.style.display = 'flex';  // 系统标题栏隐藏时，显示自定义标题栏
        body.style.paddingTop = '32px';
        document.getElementById('btn-toggle-menu-bar').textContent = '显示系统标题栏';
    }

    // hideScrollBar
    if (currentConfig.hideScrollBar) {
        body.classList.add('no-scrollbar');
        document.getElementById('btn-toggle-scrollbar').textContent = '显示滚动条';
    } else {
        body.classList.remove('no-scrollbar');
        document.getElementById('btn-toggle-scrollbar').textContent = '隐藏滚动条';
    }
}

// 事件监听
document.getElementById('btn-minimize').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'minimize');
});
document.getElementById('btn-maximize').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'maximize');
});
document.getElementById('btn-close').addEventListener('click', () => {
    ipcRenderer.send('window-action', 'close');
});

// 切换 menuBarVisible 设置
document.getElementById('btn-toggle-menu-bar').addEventListener('click', () => {
    currentConfig.menuBarVisible = !currentConfig.menuBarVisible;
    requestConfigUpdate();
});

// 切换 hideScrollBar 设置
document.getElementById('btn-toggle-scrollbar').addEventListener('click', () => {
    currentConfig.hideScrollBar = !currentConfig.hideScrollBar;
    requestConfigUpdate();
});

function requestConfigUpdate() {
    // 更新配置文件
    ipcRenderer.send('update-config', currentConfig);
}

// 当需要重启时会收到此消息
ipcRenderer.on('need-restart', () => {
    const restartPanel = document.getElementById('restart-panel');
    restartPanel.style.display = 'block';
});

document.getElementById('btn-restart-now').addEventListener('click', () => {
    ipcRenderer.send('request-restart');
});

document.getElementById('nav-about').addEventListener('click', async (e) => {
    e.preventDefault();
    await dialog.showMessageBox({
        title: '关于',
        message: '洛小山 Cheshire Demo',
        detail: '版本 1.0.0\n作者：洛小山\n一个优雅的 Electron 应用示例。',
        buttons: ['确定'],
        type: 'info'
    });
});

// 使用 IPC 处理请求
document.getElementById('btn-fetch-data').addEventListener('click', async () => {
    try {
        const posts = await apiService.fetchPosts();
        console.log('获取的帖子数据:', posts);
        
        // 在这里更新 UI，例如显示帖子标题
        const postsContainer = document.getElementById('posts-container');
        postsContainer.innerHTML = ''; // 清空之前的内容
        posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.classList.add('post-card'); // 添加动画效果的类
            postElement.innerHTML = `<h3>${post.title}</h3><p>${post.body}</p>`;
            postsContainer.appendChild(postElement);
        });
    } catch (error) {
        // 处理错误
        alert('无法获取数据，请稍后再试。');
    }
});

// 初始化配置
loadConfig();
"""

    # index.html 增加隐藏滚动条按钮及重启提示区域
    index_html_content = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>我的 Electron 应用 - Config Demo</title>
    <link rel="stylesheet" href="static/css/styles.css">
    <script src="static/js/renderer.js" defer></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f7f7f7;
            overflow-y: scroll;
            padding-top: 32px;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }

        /* no-scrollbar 时隐藏滚动条 */
        .no-scrollbar::-webkit-scrollbar {
            display: none;
        }
        .no-scrollbar {
            scrollbar-width: none; /* for Firefox */
            -ms-overflow-style: none;  /* IE and Edge */
        }

        .fixed-header .title-bar,
        .fixed-header .navbar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 999;
        }
        .fixed-header .hero {
            margin-top: 64px; /* 标题栏 + 导航栏的总高度空间 */
        }
        
        .selectable {
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
            user-select: text;
        }
        
        .title-bar {
            -webkit-app-region: drag;
            background: #333;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 8px;
            color: #fff;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        .title-bar-buttons {
            display: flex;
            align-items: center;
            -webkit-app-region: no-drag;
        }
        .title-bar-button {
            width: 46px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .title-bar-button:hover {
            background: #444;
        }

        .navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #222;
            padding: 0.8rem 1.5rem;
        }
        .navbar .brand {
            color: #fff;
            font-size: 1.2rem;
            text-decoration: none;
        }
        .navbar .nav-links a {
            color: #fff;
            text-decoration: none;
            margin-left: 1rem;
        }
        .navbar .nav-links a:hover {
            text-decoration: underline;
        }

        .hero {
            background: linear-gradient(135deg, #ff7f50, #ff5f30);
            color: #fff;
            text-align: center;
            padding: 4rem 2rem;
            transition: margin-top 0.3s;
        }
        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        .btn {
            display: inline-block;
            padding: 0.6rem 1.2rem;
            background: #ff7f50;
            color: #fff;
            text-decoration: none;
            border-radius: 0.3rem;
            border: 0;
            transition: background 0.3s;
            cursor: pointer;
        }
        .btn:hover {
            background: #ff5f30;
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }

        .section-title {
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        .card {
            background: #fff;
            border-radius: 0.3rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 1rem;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            margin: 0 0 0.5rem;
            font-size: 1.2rem;
            color: #333;
        }
        .card p {
            font-size: 0.9rem;
            color: #666;
            line-height: 1.5;
        }
        .card .card-btn {
            margin-top: 1rem;
        }

        .footer {
            text-align: center;
            padding: 2rem 1rem;
            font-size: 0.9rem;
            color: #777;
            background: #f0f0f0;
        }

        .control-panel {
            text-align: center;
            margin: 2rem 0;
        }
        .control-panel button {
            margin: 0.5rem;
        }

        #restart-panel {
            display: none;
            text-align: center;
            background: #ffefc5;
            padding: 1rem;
            margin: 2rem;
            border: 1px solid #ccc;
            border-radius: 0.3rem;
        }
        #restart-panel p {
            margin-bottom: 1rem;
        }

        /* 自定义滚动条样式 */
        body:not(.no-scrollbar)::-webkit-scrollbar {
            width: 8px;
        }

        body:not(.no-scrollbar)::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        body:not(.no-scrollbar)::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        body:not(.no-scrollbar)::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* 添加动画效果 */
        .post-card {
            background: #fff;
            border-radius: 0.3rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 1rem;
            margin: 1rem 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .post-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="title-bar">
        <div>我的 Electron 应用</div>
        <div class="title-bar-buttons">
            <div class="title-bar-button" id="btn-minimize">━</div>
            <div class="title-bar-button" id="btn-maximize">□</div>
            <div class="title-bar-button" id="btn-close">×</div>
        </div>
    </div>

    <nav class="navbar">
        <a href="#" class="brand">Cheshire Demo</a>
        
        <div class="nav-links">
            <a href="#">首页</a>
            <a href="#" id="nav-about">关于</a>
            <a href="#">文档</a>
            <a href="#">联系我们</a>
        </div>
    </nav>

    <header class="hero">
        <img src="static/icon.svg" alt="SVG Icon" width="100" height="100" draggable="false" />
        <h1>欢迎使用 洛小山 Cheshire 框架演示!</h1>
        <p>此应用加载外部 config.json 根据配置显示界面特性。更改后需重启生效。</p>
        <a href="#" class="btn">开始体验</a>
    </header>

    <main class="container">
        <h2 class="section-title">特色模块展示</h2>
        <div class="grid">
            <div class="card">
                <h3>快速开发</h3>
                <p>Cheshire Framework 提供简单易用的样式类，助你快速搭建精美界面。</p>
                <div class="card-btn">
                    <a href="#" class="btn">了解更多</a>
                </div>
            </div>
            <div class="card">
                <h3>响应式设计</h3>
                <p>自动适配不同屏幕尺寸，无需为移动设备额外开发。</p>
                <div class="card-btn">
                    <a href="#" class="btn">查看示例</a>
                </div>
            </div>
            <div class="card">
                <h3>丰富组件</h3>
                <p>包含网格布局、按钮、导航栏、表单、对话框等基础组件。</p>
                <div class="card-btn">
                    <a href="#" class="btn">组件文档</a>
                </div>
            </div>
            <div class="card">
                <h3>轻量与扩展</h3>
                <p>核心样式轻量、快速，可灵活扩展，打造独特界面。</p>
                <div class="card-btn">
                    <a href="#" class="btn">开始使用</a>
                </div>
            </div>
        </div>

        <div class="card" style="margin-top: 2rem; text-align: center;">
            <h2>操作面板（需重启生效）</h2>
            <p>切换系统标题栏、菜单栏显示、是否隐藏滚动条。由于涉及窗口框架，所有更改都需要重启后生效。</p>
            <div class="control-panel">
                <button id="btn-toggle-menu-bar" class="btn">切换系统标题栏</button>
                <button id="btn-toggle-scrollbar" class="btn">切换隐藏滚动条</button>
            </div>
        </div>
        <div class="card" style="margin-top: 2rem; text-align: center;">
            <h2>帖子展示</h2>
            <button id="btn-fetch-data" class="btn">获取帖子数据</button>
            <div id="posts-container" style="margin-top: 20px;"></div>
            <div id="restart-panel">
                <p>配置已更改，需要重启才能生效。</p>
                <button id="btn-restart-now" class="btn">立即重启</button>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <p>© <script>document.write(new Date().getFullYear())</script> Cheshire Framework by 洛小山. All rights reserved.</p>
    </footer>
</body>
</html>
"""
    create_file(project_path / 'main.js', main_js_content)
    create_file(project_path / 'preload.js', preload_js_content)
    create_file(project_path / 'renderer.js', renderer_js_content)
    create_file(project_path / 'index.html', index_html_content)

    update_package_json(project_path)

    start_bat_content = """@echo off
cd /d "%~dp0"
npm start
"""
    create_file(project_path / 'start_electron.bat', start_bat_content)

    create_static_files(project_path)  # 创建 static 目录及文件

    print("\nElectron 示例项目已创建成功！")
    print(f"项目目录: {project_path}")
    print("\n请运行以下命令启动应用程序：")
    print(f"  cd {PROJECT_NAME}")
    print("  npm start")
    print("\n或者双击项目目录中的 'start_electron.bat' 文件。")

    print("\n要打包应用程序，请运行：")
    print("  npm run build")
    print("\n或者双击项目目录中的 'build_electron.bat' 文件。")

if __name__ == "__main__":
    main()