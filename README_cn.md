# 洛小山 Electron 示例应用

[![GitHub license](https://img.shields.io/github/license/itshen/electron-demo)](LICENSE)
这是一个优雅的 Electron 桌面应用程序模板，提供了一个功能完整的起点，帮助你快速开发自己的应用。

## ✨ 特性

- 🎨 精美的自定义标题栏和系统菜单
- ⚙️ 支持通过配置文件动态调整界面
- 🌐 集成 Axios 用于网络请求
- 📱 响应式设计，完美适配各种屏幕
- 🎯 包含完整的窗口控制功能
- 💫 优雅的动画和交互效果

## 🚀 快速开始

### 环境要求

- [Node.js](https://nodejs.org/) (推荐 v14 或更高版本)
- [npm](https://www.npmjs.com/) (一般随 Node.js 一起安装)

### 创建项目

1. 运行创建脚本:
   ```bash
   python create_electron_project.py
   ```
   脚本会自动完成以下工作:
   - 创建项目目录结构
   - 安装必要的依赖
   - 生成配置文件
   - 创建启动脚本

2. 进入项目目录:
   ```bash
   cd my-electron-app-[timestamp]
   ```

### 启动应用

有两种方式可以启动应用:

- 使用命令行:
  ```bash
  npm start
  ```
- 或者直接双击项目目录中的 `start_electron.bat`

## 🛠️ 配置说明

应用支持通过 `config.json` 文件进行配置:

```json
{
  "menuBarVisible": false,  // 是否显示系统菜单栏
  "hideScrollBar": true     // 是否隐藏滚动条
}
```

> 注意: 以下修改配置后需要重启应用才能生效

## 🎯 主要功能

- 自定义/系统标题栏切换
- 窗口最小化/最大化/关闭控制
- 滚动条显示/隐藏切换
- 示例数据获取展示
- 响应式卡片布局
- 优雅的动画效果

## 🤝 参与贡献

欢迎提交问题和改进建议！

## 📝 许可证

[MIT License](LICENSE)

## 🙋‍♂️ 关于作者
洛小山 - [luoxiaoshan](https://github.com/luoxiaoshan)
