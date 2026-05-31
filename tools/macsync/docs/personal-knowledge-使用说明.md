# personal-knowledge 同步使用说明

这份说明书记录当前已经落地的同步方案：

```text
MacBook / Mac mini  <---->  local server bare Git hub
```

核心目录是：

```text
~/ICT/1-个人知识库
```

它现在是一个大的 Git 父仓库，也就是 `personal-knowledge`。里面已有的项目仓库继续作为独立 Git 仓库存在，并被父仓库以 submodule 的方式管理。

## 1. 当前结构

父仓库：

```text
~/ICT/1-个人知识库
```

内网中心仓库：

```text
ssh://justin@192.168.31.53:50701/home/justin/macsync-hub/repos/personal-knowledge.git
```

顶层 submodule：

```text
1-论文库/blockchain_conference_paper
4-论文工作/1-TrustMap
4-论文工作/4-CrossDataGen
6-个人项目/1-开源之夏/1-code/Web3Insights-data
6-个人项目/1-开源之夏/1-code/dw
6-个人项目/1-开源之夏/1-code/sakuin
6-个人项目/3-/studyhuaxia
```

深层 submodule：

```text
4-论文工作/1-TrustMap/5-实验/TrustMap-ETH
4-论文工作/4-CrossDataGen/1-实验/CrossDataGen
```

## 2. 日常开始工作

到一台设备开始工作时，先同步：

```bash
cd ~/ICT/1-个人知识库
macsync status
macsync sync
git submodule update --init --recursive
```

如果 `macsync sync` 提示不能 fast-forward，说明两台设备都有新提交。先看状态：

```bash
git status
git log --oneline --graph --decorate --all -20
```

确认可以合并时再使用：

```bash
macsync sync --merge
```

## 3. 离开设备前同步

离开 MacBook 或 Mac mini 前，执行：

```bash
cd ~/ICT/1-个人知识库
macsync status
macsync handoff
macsync status
```

`macsync handoff` 会对配置中的每个仓库执行：

```text
git add -A
git commit -m "wip: handoff from <hostname>"
git push macsync <branch>
```

如果某个仓库没有变化，它只会 push，不会创建空提交。

## 4. 新设备首次拉取

例如在 Mac mini 上第一次拉取：

```bash
mkdir -p ~/ICT
git clone --recurse-submodules \
  ssh://justin@192.168.31.53:50701/home/justin/macsync-hub/repos/personal-knowledge.git \
  ~/ICT/1-个人知识库
```

如果已经 clone 了父仓库，但 submodule 还没有拉下来：

```bash
cd ~/ICT/1-个人知识库
git submodule update --init --recursive
```

## 5. 查看状态

查看 macsync 管理的所有仓库：

```bash
macsync status
```

查看父仓库状态：

```bash
git -C ~/ICT/1-个人知识库 status
```

查看所有 submodule：

```bash
cd ~/ICT/1-个人知识库
git submodule status --recursive
```

查看每个 submodule 自己的 Git 状态：

```bash
cd ~/ICT/1-个人知识库
git submodule foreach --recursive 'echo === $name ===; git status --short'
```

## 6. 手动同步父仓库

只同步父仓库：

```bash
cd ~/ICT/1-个人知识库
git pull --ff-only macsync main
git push macsync main
```

注意：父仓库只记录普通文件和 submodule 指针。submodule 里的文件变化需要在对应子仓库里提交。

## 7. 手动同步某个子仓库

例如同步 `TrustMap-doc`：

```bash
cd ~/ICT/1-个人知识库/4-论文工作/1-TrustMap
git status
git pull --ff-only macsync main
git add -A
git commit -m "wip: update TrustMap docs"
git push macsync main
```

如果子仓库提交后，父仓库看到 submodule 指针变化，还需要回到父仓库提交一次：

```bash
cd ~/ICT/1-个人知识库
git status
git add 4-论文工作/1-TrustMap
git commit -m "chore: update TrustMap submodule"
git push macsync main
```

`macsync handoff` 会帮你统一做这件事。

## 8. GitHub 和内网同步的关系

每个仓库通常有两个 remote：

```text
origin   = GitHub
macsync  = local server
```

查看 remote：

```bash
git remote -v
```

查看所有 submodule 的 remote：

```bash
cd ~/ICT/1-个人知识库
git submodule foreach --recursive 'echo === $name ===; git remote -v'
```

`macsync` 默认只处理 `macsync` remote，不会覆盖 `origin`。

需要推 GitHub 时，仍然用普通 Git：

```bash
git push origin <branch>
```

## 9. 当前 config 配置

配置文件位置：

```text
~/.config/macsync/config.yml
```

当前关键配置：

```yaml
sync_remote: macsync
github_remote: origin
gitea_host: 192.168.31.53
gitea_web_url: http://192.168.31.53:3000
gitea_ssh_user: justin
gitea_ssh_port: 50701
gitea_owner: home/justin/macsync-hub/repos
repos:
  - name: personal-knowledge
    path: ~/ICT/1-个人知识库
    branch: main
    gitea_repo: personal-knowledge

  - name: TrustMap-doc
    path: ~/ICT/1-个人知识库/4-论文工作/1-TrustMap
    branch: main
    gitea_repo: TrustMap-doc

  - name: CrossDataGen-doc
    path: ~/ICT/1-个人知识库/4-论文工作/4-CrossDataGen
    branch: main
    gitea_repo: CrossDataGen-doc
```

完整配置可以直接查看：

```bash
cat ~/.config/macsync/config.yml
```

配置字段含义：

```text
sync_remote     macsync 使用的内网 remote 名称
github_remote   GitHub remote 名称，通常是 origin
gitea_host      local server 地址
gitea_ssh_user  SSH 用户
gitea_ssh_port  SSH 端口
gitea_owner     服务器上 bare repo 所在目录
repos[].name    本地显示名
repos[].path    本地路径
repos[].branch  同步分支
repos[].gitea_repo 服务器上的仓库名
repos[].github  GitHub 地址，仅用于记录
```

## 10. 常见问题

### macsync status 显示 origin ahead/behind

这表示相对 GitHub 有差异，不影响内网同步。

内网同步看这一段：

```text
macsync=+0/-0
```

`+0/-0` 表示本机和 local server 一致。

### submodule 目录是空的

执行：

```bash
cd ~/ICT/1-个人知识库
git submodule update --init --recursive
```

### 修改了子仓库，但父仓库也显示变化

这是正常的。子仓库提交后，父仓库记录的 submodule commit 指针变了。

处理方式：

```bash
cd ~/ICT/1-个人知识库
git add <submodule-path>
git commit -m "chore: update submodule pointer"
git push macsync main
```

或者直接用：

```bash
macsync handoff
```

### 出现冲突

macsync 使用 Git 原生命令，所以冲突基本就是 Git 冲突。

先看：

```bash
git status
git diff
```

解决后：

```bash
git add -A
git commit
git push macsync <branch>
```

## 11. 最常用命令

```bash
macsync status
macsync sync
git submodule update --init --recursive
macsync handoff
```
