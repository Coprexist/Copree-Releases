#!/usr/bin/env bash
# 把打包入口与 GUI 源码放进主仓库的检出目录（$1）。
#
# 三个平台共用这一份清单：以前每个 job 各写一份 cp 列表，漏拷一个文件不会让构建失败，
# 只会在用户机器上变成 ModuleNotFoundError——v0.4.1 的 exe / dmg / tar.gz 全是这么废掉的
# （run_packaged.py 里 from gui import AIsChatGUI，而 gui.py 从来没被拷进去）。
set -euo pipefail

dest=${1:?用法: scripts/stage.sh <目标目录>}
here=$(cd "$(dirname "$0")/.." && pwd)

cp "$here"/run_packaged.py \
   "$here"/server_core.py \
   "$here"/gui.py \
   "$here"/AIsChat.spec \
   "$here"/installer.nsi \
   "$here"/LICENSE.txt \
   "$dest"/
cp -r "$here"/gui_app "$dest"/

# 只检查模块能否解析，不真的 import：GUI 依赖 tkinter，构建机上未必装了
cd "$dest"
python - <<'PY'
import importlib.util
import sys

missing = [m for m in ("gui", "gui_app", "server_core") if importlib.util.find_spec(m) is None]
if missing:
    sys.exit(f"staging 不完整，缺少模块：{missing}")
print("staging ok: gui, gui_app, server_core")
PY
