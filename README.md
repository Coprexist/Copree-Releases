# AIsChat Launcher Installer

## Main Repository

[AIsChat](https://github.com/Coprexist/AIsChat) - AI Chat Framework

## Download

Go to [Releases](https://github.com/Coprexist/AIsChat-Releases/releases) to download the latest version.

## Installation

1. Download `AIsChat-Installer.exe`
2. Run the installer
3. Select installation language (English / Simplified Chinese)
4. Choose installation directory (default: `%LOCALAPPDATA%\AIsChat`)
5. Complete installation

## Uninstall

- Start Menu -> AIsChat -> Uninstall AIsChat
- Or Control Panel -> Programs and Features -> AIsChat Launcher -> Uninstall

## Build

三个平台的 job 都在 `.github/workflows/build.yml`：推 tag 触发，也可手动 `workflow_dispatch`
（`tag` 填版本号或 `main`；勾上 `build_only` 则只构建、不发 Release）。

打包入口与 GUI 源码由 `scripts/stage.sh` 统一拷进主仓库检出目录，并当场用 `find_spec`
校验 `gui` / `gui_app` / `server_core` 能否解析。这三者是运行期才 import 的模块，漏拷不会让
构建失败，只会让用户拿到 `ModuleNotFoundError`——v0.4.1 的 exe / dmg / tar.gz 都因此不可用。

## Changelog

### v0.4.0 (2026-08-24)

**New Features**:- Desktop EXE installer for Windows- GUI launcher with CustomTkinter- Auto-start on boot- Minimize to system tray- Port configuration- Log panel with brief/detailed modes

**Improvements**- Fixed Windows window icon issue- Increased font size for better readability- Scrollable settings page- Single window view switching

**Technical Details**- Built with NSIS 3.09- UTF-8 Chinese character support- Installer size: ~40MB- License: MIT License

## License

MIT License
