# 首次运行与故障恢复

使用本技能 scripts 目录的 run.ps1 或 run.sh。doctor 输出 JSON；状态 ready 对应退出码 0，missing 对应 2，blocked 对应 3。执行 run 会自动处理可安装缺项，再用原参数运行一次。操作名及依赖组见 [清单](runtime.json)。

共享缓存由 RM_CACHE_DIR 指定。首次安装从官方分发获取 uv、Python 3.12、锁定依赖及本操作需要的资源。Linux x86_64、Windows x64、macOS arm64 提供 CPU 依赖锁。另选 CUDA 时请用 RM_SCIENCE_PYTHON 提供已准备的解释器。准备就绪的环境可离线重复使用；在线数据库仍需联网。

RM_ASSET_DIR 可指向已下载的上游原始文件，名称与 SHA-256 见本技能清单。自选模型按业务参数提供。文献生成默认为本地推理，RM_LLAMA_SERVER 可指定本机 llama-server。显式选择 RM_CHAT_BACKEND=remote 后使用 OPENAI_API_KEY、MODEL_USE 与可选 OPENAI_BASE_URL。嵌入的远程模式为 RM_EMBED_BACKEND=remote，使用 GOOGLE_API_KEY 或 OPENAI_API_KEY 与 OPENAI_EMBEDDING_MODEL。请通过宿主私密配置提供凭据。

如首次下载被宿主阻止，在宿主中完成必要授权或预置所需资源后，用原命令继续。检索服务失败、用户输入错误和科学计算失败分别查看业务输出。
