# Luoxiaoshan Electron Demo App

[![GitHub license](https://img.shields.io/github/license/itshen/electron-demo)](LICENSE)

An elegant Electron desktop application template that provides a fully functional starting point to help you quickly develop your own applications.

## ✨ Features

- 🎨 Beautiful custom title bar and system menu
- ⚙️ Support dynamic interface adjustment through configuration files
- 🌐 Integrated Axios for network requests
- 📱 Responsive design, perfect for various screen sizes
- 🎯 Complete window control functionality
- 💫 Elegant animations and interactions

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v14 or higher recommended)
- [npm](https://www.npmjs.com/) (typically comes with Node.js)

### Create Project

1. Run the creation script:
   ```bash
   python create_electron_project.py
   ```
   The script will automatically:
   - Create project directory structure
   - Install necessary dependencies
   - Generate configuration files
   - Create startup scripts

2. Navigate to project directory:
   ```bash
   cd my-electron-app-[timestamp]
   ```

### Launch Application

There are two ways to start the application:

- Using command line:
  ```bash
  npm start
  ```
- Or double-click `start_electron.bat` in the project directory

## 🛠️ Configuration

The application can be configured through `config.json`:

```json
{
  "menuBarVisible": false,  // Toggle system menu bar visibility
  "hideScrollBar": true     // Toggle scrollbar visibility
}
```

> Note: Application restart is required after configuration changes

## 🎯 Main Features

- Custom/System title bar toggle
- Window minimize/maximize/close controls
- Scrollbar show/hide toggle
- Example data fetching and display
- Responsive card layout
- Elegant animation effects

## 🤝 Contributing

Issues and improvement suggestions are welcome!

## 📝 License

[MIT License](LICENSE)

## 🙋‍♂️ About Author

Luoxiaoshan - [luoxiaoshan](https://github.com/itshen)
