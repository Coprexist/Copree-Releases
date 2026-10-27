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

注意触发源是**本仓库**的 tag——主仓库打 tag 不会触发这里（主仓库目前也没有发布 workflow）。
另一种触发方式是 `repository_dispatch`（`event_type=release`，`client_payload.tag` 给版本号）。
构建时按这个 tag 去检出主仓库的同一 tag，所以两边 tag 要同名。

打包入口与 GUI 源码由 `scripts/stage.sh` 统一拷进主仓库检出目录，并当场用 `find_spec`
校验 `gui` / `gui_app` / `server_core` 能否解析。这三者是运行期才 import 的模块，漏拷不会让
构建失败，只会让用户拿到 `ModuleNotFoundError`——v0.4.1 的 exe / dmg / tar.gz 都因此不可用。

### 发版约定

- **版本号只有一个来源：tag。** 源码里的 `app_version` 必须与 tag 一致，`stage.sh` 会在打包前
  核对，不一致直接让构建失败。包的 `/health` 自报的版本、安装包里的版本号都来自这一处。
- **已发布的 tag 不复用。** 内容有变化就递增版本号。同名重建会留下「同一个版本号、两份不同
  内容」的包，用户与自己都分不清（0.4.14 就重建过一次，只能在 Release 说明里额外标注）。
- **图标**：`frontend/public/brand/coprexist-icon-512.png` 是唯一主图，
  `scripts/make_app_icons.py` 从它派生出各档 PNG、`coprexist-icon.ico`（Windows）与
  `coprexist-icon.icns`（macOS）。打包前 `stage.sh` 会自动重跑一次，换图只需替换主图。

## Changelog

### v0.4.0 (2026-08-24)

**New Features**:- Desktop EXE installer for Windows- GUI launcher with CustomTkinter- Auto-start on boot- Minimize to system tray- Port configuration- Log panel with brief/detailed modes

**Improvements**- Fixed Windows window icon issue- Increased font size for better readability- Scrollable settings page- Single window view switching

**Technical Details**- Built with NSIS 3.09- UTF-8 Chinese character support- Installer size: ~40MB- License: MIT License

## License

MIT License
