# Xime 同步词库

推送到 `master` 且改动了 `rime/` 时，`.github/workflows/release-android.yml` 会校验并发布词库包，再更新 `xime-index` 分支上的商店索引。

## 日常更新

手机上打开 Xime：设置 → 扩展商店 → 方案 → 键道6 → 更新。更新后会保留启用状态并自动部署。

## 首次配置

只需做一次，需要 Xime v3.4.2 或更高版本。

1. 「输入方案」→「已导入」→「+」→「网络导入」，填入下面的地址，把 `xime.custom.yaml` 带到手机上：

   ```
   https://github.com/lvris/rime-keytao/releases/latest/download/keytao-android.zip
   ```

2. 「扩展商店」→「方案」，安装键道6。
3. 在「已启用」里打开键道，点「部署方案」。

## 键盘配置

键盘布局、主题和索引地址都在 `rime/xime.custom.yaml`。Xime 只用这一个文件保存这些配置，所以：

- 要改配置就改仓库里的文件，推送后在手机上更新。
- 手机上直接改的配置，以及在商店应用的单文件布局，都会在下次更新时被覆盖。想保留就把内容复制到仓库的文件里。

配置项参考 [Xime 的示例](https://github.com/ximeiorg/Xime/tree/master/docs/config_examples)。

## 注意

- 方案市场只显示第一个有内容的索引，所以看不到官方方案。要装官方方案时，先临时去掉 `base_urls` 的第一项。
- 每次安装都会替换整个方案目录，`*.userdb` 不保留。保留的只有 `xime.custom.yaml`、`themes/`、`fonts/` 和 `custom_phrase*.txt`。
- 固定下载地址始终指向最新版本，索引失效时可以回到「网络导入」。
