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
   "$here"/api_prefix.py \
   "$here"/gui.py \
   "$here"/AIsChat.spec \
   "$here"/installer.nsi \
   "$here"/LICENSE.txt \
   "$dest"/
cp -r "$here"/gui_app "$dest"/

# 品牌图标由主图 frontend/public/brand/coprexist-icon-512.png 派生出各档 PNG、ICO、ICNS。
# 打包前重跑一次，避免仓库里提交的二进制与主图漂移；改图只需替换主图。
python "$dest/scripts/make_app_icons.py"

# 版本号的唯一来源是 tag：源码里的 app_version 与 tag 不一致就直接失败。
# 否则会打出「版本号写着 A、内容却是 B」的包——0.4.14 曾因此重建过一次。
if [ -n "${TAG:-}" ]; then
  tag_version=${TAG#v}
  source_version=$(sed -n 's/^    app_version: str = "\([0-9][0-9.]*\)"/\1/p' "$dest/backend/app/config.py")
  if [ "$tag_version" != "$source_version" ]; then
    echo "tag ${TAG} 与源码版本 ${source_version:-未取到} 不一致：先改 backend/app/config.py" >&2
    exit 1
  fi
  echo "version ok: ${source_version}"
fi

# 只检查模块能否解析，不真的 import：GUI 依赖 tkinter，构建机上未必装了
cd "$dest"
python - <<'PY'
import importlib.util
import sys

missing = [m for m in ("gui", "gui_app", "server_core", "api_prefix")
           if importlib.util.find_spec(m) is None]
if missing:
    sys.exit(f"staging 不完整，缺少模块：{missing}")
print("staging ok: gui, gui_app, server_core, api_prefix")
PY
